# Openlab复试Q3 看看你的
* ## 环境
  * python3.11
  * requirements.txt内容
  * chrome
* ## 3.1 贪心的小 Q
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
    * 数据存储到数据库
* ## 3.2 AC 通知书
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
    * 数据存储到数据库
* ## 3.3 狡猾的幕后人
  * 程序名称:save_pages.py
  * 需要的文件：
    * data/sql_login.txt(同上)
  * 完成的功能：
    * 爬取通知及页面pdf(pdf保存在data/pdfs)
    * 数据存储到数据库
* ## 获取爬取数据
  * 网盘：https://cloud.189.cn/web/share?code=JfUru2jQ3eQf（访问码：4xik）