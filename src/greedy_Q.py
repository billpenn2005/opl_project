import requests
import json
import pandas as pd
problem_request=requests.get("https://oj.qd.sdu.edu.cn/api/problem/list?pageNow=1&pageSize=200")
ac_request=requests.get("https://oj.qd.sdu.edu.cn/api/submit/list?pageNow=1&pageSize=20000") #https://oj.qd.sdu.edu.cn/api/submit/list?pageNow=1&pageSize=2000
problem_json=json.loads(problem_request.text)
ac_json=json.loads(ac_request.text)
problem_dataframe=pd.DataFrame(problem_json['data']['rows'])
ac_dataframe=pd.DataFrame(ac_json['data']['rows'])
problem_excel_dataframe=problem_dataframe[['problemId','problemCode','problemTitle','source','submitNum','acceptNum']]
problem_excel_dataframe.rename(columns={"problemId":"题目id","problemCode":"题目代码","problemTitle":"标题","source":"题目来源","submitNum":"提交数","acceptNum":"通过数"},inplace=True)
problem_excel_dataframe.to_excel('Problem_data.xlsx',index=False)