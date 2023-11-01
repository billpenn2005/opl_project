from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
import json
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import os

#Retested on 2023/11/1, found problem that the program would error when user finished all the problems, fixed.

def mkdir(path):
	folder = os.path.exists(path)
	if not folder:
		os.makedirs(path)
mkdir('./data')
mkdir('./data/pics')

#some variables
judge_state_dict={0:'QUEUEING',1:'AC',2:'TLE',3:'MLE',4:'RE',5:'SE',6:'WA',7:'PE',8:'CE',9:'OLE',10:'CANCELED'}
titles=['QUEUEING','AC','TLE','MLE','RE','SE','WA','PE','CE','OLE','CANCELED']
colors=['#9b9b9b','#7ed321','#4a90e2','#9013fe','#bd10e0','#000000','#d0021b','#f8e71c','#f5a623','#8b572a','#4a4a4a']

login_url="https://oj.qd.sdu.edu.cn/v2/login"
chrome_options=Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('log-level=3')
driver=webdriver.Chrome(options=chrome_options)
driver.get(login_url)

pwd_file=open("./data/pwd.txt")
username=pwd_file.readline()
password=pwd_file.readline()
pwd_file.close()

#login session
driver.find_element(By.XPATH,'//*[@id="root"]/section/section/main/div/div/div/div[2]/form/a/button').click()
time.sleep(1)
name_input=driver.find_element("id","un")
password_input=driver.find_element("id","pd")
login_button=driver.find_element("id","index_login_btn")
name_input.send_keys(username)
password_input.send_keys(password)
login_button.click()
print("\033[92m[+]Login successfully!\033[0m")

time.sleep(3)
cookies=driver.get_cookies()
cookies_dict = dict()
for cookie in cookies:
    cookies_dict[cookie['name']] = cookie['value']

#sql
pwd=open('./data/sql_login.txt')
sql_username=pwd.readline()
sql_username=sql_username.rstrip('\n')
sql_password=pwd.readline()
sql_password=sql_password.rstrip('\n')
host=pwd.readline()
host=host.rstrip('\n')
dbname=pwd.readline()
dbname=dbname.rstrip('\n')
port=pwd.readline()
port=port.rstrip('\n')
pwd.close()
DB_URI = 'mysql+pymysql://{username}:{pwd}@{host}:{port}/{db}?charset=utf8'\
    .format(username =sql_username,pwd = sql_password,host = host,port=port,db = dbname)
engine = create_engine(DB_URI, paramstyle="format")

def load_group_contest_data(group_num):
    contests_dataframe=pd.DataFrame(json.loads(requests.get("https://oj.qd.sdu.edu.cn/api/contest/list?pageNow=1&pageSize=200&groupId="+str(group_num),cookies=cookies_dict).text)['data']['rows'])
    contests_num=[]
    for index,row in contests_dataframe.iterrows():
        contests_num.append(row['contestId'])
    contests_total_data=[]
    for contest_id in contests_num:
        contest_single_dataframe=pd.DataFrame(json.loads(requests.get('https://oj.qd.sdu.edu.cn/api/contest/query?contestId='+str(contest_id),cookies=cookies_dict).text)['data']['problems'])
        contests_total_data.append(contest_single_dataframe)
    contest_total_dataframe=pd.concat(contests_total_data,ignore_index=True)
    return contest_total_dataframe,contests_total_data,contests_num
def analyze_user(user_id,contest_id):
    #user_id=username.rstrip('\n')
    contest_single_dataframe=pd.DataFrame(json.loads(requests.get('https://oj.qd.sdu.edu.cn/api/contest/query?contestId='+str(contest_id),cookies=cookies_dict).text)['data']['problems'])
    user_total_data=[]
    not_ac_problems=[]
    t_results=[0,0,0,0,0,0,0,0,0,0,0]
    for index,row in contest_single_dataframe.iterrows():
        user_data=pd.DataFrame(json.loads(requests.get('https://oj.qd.sdu.edu.cn/api/contest/listSubmission?pageNow=1&pageSize=200&username='+str(user_id)+'&problemCode='+row['problemCode']+'&contestId='+str(contest_id),cookies=cookies_dict).text)['data']['rows'])
        time.sleep(0.5)
        user_total_data.append(user_data)
        results=[0,0,0,0,0,0,0,0,0,0,0]
        for index2,row2 in user_data.iterrows():
            if(row2['judgeResult']>10):
                continue
            results[row2['judgeResult']]+=1
            t_results[row2['judgeResult']]+=1
        res_to_plot=[]
        tit_to_plot=[]
        col_to_plot=[]
        for i in range(11):
            if(results[i]!=0):
                res_to_plot.append(results[i])
                tit_to_plot.append(titles[i])
                col_to_plot.append(colors[i])
        if(results[1]==0):
            not_ac_problems.append(row)
        plt.pie(res_to_plot,labels=tit_to_plot,colors=col_to_plot, autopct=lambda p: '{:.1f}%'.format(round(p)) if p >= 0.1 else '')
        plt.title(str(user_id)+'_'+str(row['problemCode']))
        plt.savefig('./data/pics/'+str(user_id)+'_'+str(contest_id)+'_'+str(row['problemCode'])+'.jpg')
        time.sleep(0.5)
        plt.close()
    t_res_to_plot=[]
    t_tit_to_plot=[]
    t_col_to_plot=[]
    for i in range(11):
        if(t_results[i]!=0):
            t_res_to_plot.append(t_results[i])
            t_tit_to_plot.append(titles[i])
            t_col_to_plot.append(colors[i])
    plt.pie(t_res_to_plot,labels=t_tit_to_plot,colors=t_col_to_plot, autopct=lambda p: '{:.1f}%'.format(round(p)) if p >= 0.1 else '')
    plt.title(str(user_id)+'_'+str(contest_id)+'_total')
    plt.savefig('./data/pics/'+str(user_id)+'_'+str(contest_id)+'_total.jpg')
    time.sleep(0.5)
    plt.close()
    return not_ac_problems,user_total_data,t_results
def get_group_submits(group_num):
    contests_dataframe=pd.DataFrame(json.loads(requests.get("https://oj.qd.sdu.edu.cn/api/contest/list?pageNow=1&pageSize=200&groupId="+str(group_num),cookies=cookies_dict).text)['data']['rows'])
    contests_num=[]
    for index,row in contests_dataframe.iterrows():
        contests_num.append(row['contestId'])
    contests_total_data=[]
    for contest_id in contests_num:
        contest_single_dataframe=pd.DataFrame(json.loads(requests.get('https://oj.qd.sdu.edu.cn/api/contest/listSubmission?pageNow=1&pageSize=2000&contestId='+str(contest_id),cookies=cookies_dict).text)['data']['rows'])
        contests_total_data.append(contest_single_dataframe)
    contest_total_dataframe=pd.concat(contests_total_data,ignore_index=True)
    return contest_total_dataframe
my_id=username.rstrip('\n')
contest_problems,contest_data_array,contest_ids=load_group_contest_data(49)
contest_problems.to_sql('group_problems',engine,if_exists='replace',index=True)
contest_problems.to_excel('Group_Problem.xlsx',index=False)
not_ac_problems=[]
tot_count=[0,0,0,0,0,0,0,0,0,0,0]
for i in contest_ids:
    my_not_ac_problems,my_total_data,tot_res=analyze_user(my_id,i)
    for j in range(11):
        tot_count[j]+=tot_res[j]
    not_ac_problems.append(pd.DataFrame(my_not_ac_problems))
if(len(not_ac_problems)):
    print("You have finished all the problems.")
else:
    nac_df=pd.concat(not_ac_problems)
    nac_df.to_sql('unfinished_problems',engine,if_exists='replace',index=False)
    nac_df.to_excel('Unfinished_Problems.xlsx',index=False)
group_df=get_group_submits(49)
group_df.to_sql('group_submits',engine,index=False,if_exists='replace')
group_df.to_excel('Group_Submits.xlsx',index=False)
t_res_to_plot=[]
t_tit_to_plot=[]
t_col_to_plot=[]
for i in range(11):
    if(tot_count[i]!=0):
        t_res_to_plot.append(tot_count[i])
        t_tit_to_plot.append(titles[i])
        t_col_to_plot.append(colors[i])
plt.pie(t_res_to_plot,labels=t_tit_to_plot,colors=t_col_to_plot, autopct=lambda p: '{:.1f}%'.format(round(p)) if p >= 0.1 else '')
plt.title(str(my_id)+'_total')
plt.savefig('./data/pics/'+str(my_id)+'_total.jpg')
time.sleep(0.5)
plt.close()