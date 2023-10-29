# Openlab复试Q3
* ## 环境
  * python3.11
  * requirements.txt内容
  * chrome
* ## 3.1
  * 程序名称：greedy_Q.py
  * 需要的文件：
    * data/sql_login.txt(配置数据库)
      * line1:用户名
      * line2:密码
      * line3:数据库地址
      * line4:数据库名称
      * line5:数据库端口
  * 完成的功能：
    * 爬取oj的题目与提交
    * 针对全部提交进行可视化分析(保存在data/pics)
* ## 3.2
  * 程序名称:
    * AC.py
    * AC_monitor.py
  * 需要的文件:
    * data/sql_login.txt(同上)
    * data/pwd.txt(oj登录)
      * line1:用户名
      * line2:密码
    * data/mail.txt(邮件发送配置)
      * line1:邮箱用户名
      * line2:密码
    * src/AC_monitor.py
      * 可更改邮件推送目的地邮箱
  * 完成的功能:
    * 爬取用户组题目、提交
    * 保存自己未AC题目
    * 针对单个用户提交的可视化分析(保存在data/pics)
    * 监控用户组AC情况，发送至邮箱
* ## 3.3
  * 程序名称:save_pages.py
  * 需要的文件：
    * data/sql_login.txt(同上)
  * 完成的功能：
    * 爬取通知及页面pdf