import requests
import json
import pandas as pd
from sqlalchemy import create_engine
import execjs

#some variables
judge_state_dict={0:'QUEUEING',1:'AC',2:'TLE',3:'MLE',4:'RE',5:'SE',6:'WA',7:'FE',8:'CE',9:'OLE',10:'CANCELED'}

#some functions
def transfer_time(t):
    s='(new Date('+t+')).toGMTString()'
    return execjs.eval(s)

#get data
problem_request=requests.get("https://oj.qd.sdu.edu.cn/api/problem/list?pageNow=1&pageSize=200")
ac_request=requests.get("https://oj.qd.sdu.edu.cn/api/submit/list?pageNow=1&pageSize=20000") #https://oj.qd.sdu.edu.cn/api/submit/list?pageNow=1&pageSize=2000
problem_json=json.loads(problem_request.text)
ac_json=json.loads(ac_request.text)

#process data

#xls
problem_dataframe=pd.DataFrame(problem_json['data']['rows'])
ac_dataframe=pd.DataFrame(ac_json['data']['rows'])
problem_excel_dataframe=problem_dataframe[['problemId','problemCode','problemTitle','source','submitNum','acceptNum']]
problem_excel_dataframe.rename(columns={"problemId":"题目id","problemCode":"题目代码","problemTitle":"标题","source":"题目来源","submitNum":"提交数","acceptNum":"通过数"},inplace=True)
problem_excel_dataframe.to_excel('Problem_data.xlsx',index=False)
ac_dataframe_excel=problem_dataframe[['submissionId','username','problemCode','problemTitle','judgeResult','judgeScore','judgeTemplateTitle','usedMemory','usedTime','gmtCreate']]
for i in ac_dataframe_excel['gmtCreate']:
    i=transfer_time(str(i))
for i in ac_dataframe_excel['judgeResult']:
    i=judge_state_dict(i)
ac_dataframe_excel.to_excel('Judgement_data.xlsx',index=False)

#sql
pwd=open('./data/sql_login.txt')
username=pwd.readline()
username=username.rstrip('\n')
password=pwd.readline()
password=password.rstrip('\n')
host=pwd.readline()
host=host.rstrip('\n')
dbname=pwd.readline()
dbname=dbname.rstrip('\n')
port=pwd.readline()
port=port.rstrip('\n')
pwd.close()
DB_URI = 'mysql+pymysql://{username}:{pwd}@{host}:{port}/{db}?charset=utf8'\
    .format(username =username,pwd = password,host = host,port=port,db = dbname)
engine = create_engine(DB_URI, paramstyle="format")
problem_excel_dataframe.to_sql('problem_data',engine,if_exists='replace',index=True)