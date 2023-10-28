from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER
from datetime import datetime
import os
import time
import requests
import json
import pandas as pd
from sqlalchemy import create_engine
import execjs
import matplotlib.pyplot as plt
import zmail
import pytz

#some variables
judge_state_dict={0:'QUEUEING',1:'AC',2:'TLE',3:'MLE',4:'RE',5:'SE',6:'WA',7:'FE',8:'CE',9:'OLE',10:'CANCELED'}
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

mail_file=open("./data/mail.txt")
musername=mail_file.readline()
musername=musername.rstrip('\n')
mpassword=mail_file.readline()
mpassword=mpassword.rstrip('\n')
mail_file.close()

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

def transfer_time(t):
    s='(new Date('+t+')).toGMTString()'
    return execjs.eval(s)
def get_time():
    s='new Date().getTime()'
    return execjs.eval(s)

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

def get_group_submits(group_num):
    contests_dataframe=pd.DataFrame(json.loads(requests.get("https://oj.qd.sdu.edu.cn/api/contest/list?pageNow=1&pageSize=200&groupId="+str(group_num),cookies=cookies_dict).text)['data']['rows'])
    contests_num=[]
    for index,row in contests_dataframe.iterrows():
        contests_num.append(row['contestId'])
    contests_total_data=[]
    for contest_id in contests_num:
        contest_single_dataframe=pd.DataFrame(json.loads(requests.get('https://oj.qd.sdu.edu.cn/api/contest/listSubmission?pageNow=1&pageSize=200&contestId='+str(contest_id),cookies=cookies_dict).text)['data']['rows'])
        contests_total_data.append(contest_single_dataframe)
    contest_total_dataframe=pd.concat(contests_total_data,ignore_index=True)
    return contest_total_dataframe

server=zmail.server(musername,mpassword)
to_mail='plx888888888@126.com'
group_members=pd.DataFrame(json.loads(requests.get('https://oj.qd.sdu.edu.cn/api/group/query?groupId=49',cookies=cookies_dict).text)['data']['members'])
now_time=0
while(True):
    send_text=''
    print(transfer_time(str(now_time))+' Starting to analyze...')
    all_submits=get_group_submits(49)
    all_submits.to_sql('group_submits',engine,if_exists='append',index=False)
    for index,row in all_submits.iterrows():
        if(row['gmtCreate']<str(now_time)):
            continue
        if(row['judgeResult']==1):
            filt_df=group_members[group_members['username']==row['username']]
            for index1,row1 in filt_df.iterrows():
                send_text+=row1['nickname']+' AC '+row['problemTitle']+' at '+transfer_time(str(int(row['gmtCreate'])+8*(3600000)))[:-3]+'\n'
                break
    print(send_text)
    if(send_text!=''):
        server.send_mail(to_mail,{'subject':'AC monitor','content_text':send_text})
    else:
        print("No one AC in these 15 minutes.")
    now_time=get_time()
    time.sleep(15*60) #wait 15 minutes