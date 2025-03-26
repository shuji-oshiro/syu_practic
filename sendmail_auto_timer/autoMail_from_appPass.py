# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 15:08:13 2025
Gmailを使った自動メール送信
app_passを使用した認証

@author: owner-pc
"""

import smtplib
from email.mime.text import MIMEText

#Googleアプリパスワード
app_pass=""

#本文
body="""これはPython学習帳のテスト3です。
2行目
3行目
4行目"""
msg=MIMEText(body)

#メールの件名
msg["Subject"]="Python学習帳のテスト3"

#あなたのGmailアドレス
msg["From"]=""

#メールの送信先
msg["To"]=""

smtp=smtplib.SMTP("smtp.gmail.com",587)
smtp.ehlo()
smtp.starttls()
smtp.ehlo()

#あなたのGmailアドレス,あなたのGmailアプリパスワード
smtp.login("",app_pass)
smtp.send_message(msg)
smtp.close()