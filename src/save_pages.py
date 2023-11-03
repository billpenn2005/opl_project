from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
from sqlalchemy import create_engine
import base64
import os
import execjs

#Retested on 2023/11/1, passed.

def mkdir(path):
	folder = os.path.exists(path)
	if not folder:
		os.makedirs(path)
mkdir('./data')
mkdir('./data/pdfs')

def get_time():
    s='new Date().getTime()'
    return execjs.eval(s)

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


chrome_options=Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('log-level=3')
driver=webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)
driver.get('https://www.bkjx.sdu.edu.cn/sanji_list.jsp?PAGENUM=1&wbtreeid=1010')
total=int(driver.find_element(By.XPATH,'//*[@id="fanye128813"]').text[-4:-1])
dts=[]
for i in range(1,total):
    driver.get('https://www.bkjx.sdu.edu.cn/sanji_list.jsp?PAGENUM='+str(i)+'&wbtreeid=1010')
    links=driver.find_elements(By.CLASS_NAME,'leftNews3')
    for j in links:
        lks=j.find_element(By.TAG_NAME,'a')
        elm=j.find_element(By.XPATH,'div[3]').text
        lnk=lks.get_property('href')
        lkt=lks.text
        new_row={'标题':lkt,'时间':elm[1:-1],'链接':lnk,'爬取时间':get_time()}
        dts.append(new_row)
df=pd.DataFrame(dts)
df.to_sql('notice_data',engine,if_exists='replace',index=True)
df.to_excel('Notice_Data.xlsx',index=False)

for index,row in df.iterrows():
    link=row['链接']
    driver.get(link)
    b64_str=driver.print_page()
    b64_bytes=base64.b64decode(b64_str)
    pathstr=row['标题']+row['时间']+'.pdf'
    pathstr=pathstr.replace('/','')
    pathstr=pathstr.replace('\\','')
    pathstr=pathstr.replace(':','')
    pathstr=pathstr.replace('*','')
    pathstr=pathstr.replace('?','')
    pathstr=pathstr.replace('"','')
    pathstr=pathstr.replace('<','')
    pathstr=pathstr.replace('>','')
    pathstr=pathstr.replace('|','')
    with open('./data/pdfs/'+pathstr,'wb') as f:
        f.write(b64_bytes)
