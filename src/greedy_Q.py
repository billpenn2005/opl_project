import requests
import json
import pandas as pd
from sqlalchemy import create_engine
import execjs
import matplotlib.pyplot as plt
import time

#some variables
judge_state_dict={0:'QUEUEING',1:'AC',2:'TLE',3:'MLE',4:'RE',5:'SE',6:'WA',7:'FE',8:'CE',9:'OLE',10:'CANCELED'}
titles=['QUEUEING','AC','TLE','MLE','RE','SE','WA','PE','CE','OLE','CANCELED']
colors=['#9b9b9b','#7ed321','#4a90e2','#9013fe','#bd10e0','#000000','#d0021b','#f8e71c','#f5a623','#8b572a','#4a4a4a']

#some functions
def transfer_time(t):
    s='(new Date('+t+')).toGMTString()'
    return execjs.eval(s)

#get data
problem_request=requests.get("https://oj.qd.sdu.edu.cn/api/problem/list?pageNow=1&pageSize=200")
ac_request=requests.get("https://oj.qd.sdu.edu.cn/api/submit/list?pageNow=1&pageSize=2000") #https://oj.qd.sdu.edu.cn/api/submit/list?pageNow=1&pageSize=2000
problem_json=json.loads(problem_request.text)
ac_json=json.loads(ac_request.text)

#process data

#xls
problem_dataframe=pd.DataFrame(problem_json['data']['rows'])
ac_dataframe=pd.DataFrame(ac_json['data']['rows'])
problem_excel_dataframe=problem_dataframe[['problemId','problemCode','problemTitle','source','submitNum','acceptNum']]
problem_excel_dataframe.rename(columns={"problemId":"题目id","problemCode":"题目代码","problemTitle":"标题","source":"题目来源","submitNum":"提交数","acceptNum":"通过数"},inplace=True)
problem_excel_dataframe.to_excel('Problem_data.xlsx',index=False)
ac_dataframe_excel=ac_dataframe[['submissionId','username','problemCode','problemTitle','judgeResult','judgeScore','judgeTemplateTitle','usedMemory','usedTime','gmtCreate']]
for index,row in ac_dataframe_excel.iterrows():
    ac_dataframe_excel.at[index,'judgeResult']=judge_state_dict[row['judgeResult']]
    ac_dataframe_excel.at[index,'gmtCreate']=transfer_time(str(row['gmtCreate']))
ac_dataframe_excel.rename(columns={'submissionId':'ID','username':"用户名",'problemCode':'题目编号','problemTitle':'题目名','judgeResult':'测评结果','judgeScore':'测评得分','judgeTemplateTitle':'测评模板','usedMemory':'内存使用','usedTime':'时间使用(ms)','gmtCreate':'提交时间'},inplace=True)
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
ac_dataframe_excel.to_sql('judgement_data',engine,if_exists='replace',index=True)

#analyze
problem_analyze_dataframe=pd.read_sql_table('problem_data',engine)
problem_analyze_dataframe.drop('index',axis='columns',inplace=True)
judge_analyze_dataframe=pd.read_sql_table('judgement_data',engine)
judge_analyze_dataframe.drop('index',axis='columns',inplace=True)
most_ac_dataframe=problem_analyze_dataframe.sort_values(by='通过数',axis=0,ascending=False)[:20]
most_submit_dataframe=problem_analyze_dataframe.sort_values(by='提交数',axis=0,ascending=False)[:20]
most_ac_dataframe.to_excel('Mostly_AC.xlsx',index=False)
most_ac_dataframe.to_sql('most_ac_data',engine,if_exists='replace',index=False)
most_submit_dataframe.to_excel('Mostly_Submitted.xlsx',index=False)
most_submit_dataframe.to_sql('most_submitted_data',engine,if_exists='replace',index=False)

#extra_analyze
for index,row in problem_analyze_dataframe.iterrows():
    problem_id=row['题目代码']
    problem_analyze_request=requests.get('https://oj.qd.sdu.edu.cn/api/submit/list?pageNow=1&pageSize=1000&problemCode='+str(problem_id))
    problem_analyze_json=json.loads(problem_analyze_request.text)
    problem_single_dataframe=pd.DataFrame(problem_analyze_json['data']['rows'])
    results=[0,0,0,0,0,0,0,0,0,0,0]
    for i2,row2 in problem_single_dataframe.iterrows():
        if(row2['judgeResult']>10):
            continue
        results[row2['judgeResult']]+=1
    res_to_plot=[]
    tit_to_plot=[]
    col_to_plot=[]
    for i in range(11):
        if(results[i]!=0):
            res_to_plot.append(results[i])
            tit_to_plot.append(titles[i])
            col_to_plot.append(colors[i])
    plt.pie(res_to_plot,labels=tit_to_plot,colors=col_to_plot, autopct=lambda p: '{:.1f}%'.format(round(p)) if p >= 0.1 else '')
    plt.title(problem_id)
    plt.savefig('./data/pics/'+str(problem_id)+'.jpg')
    time.sleep(1)
    #plt.show()
    plt.close()