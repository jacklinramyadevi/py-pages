# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:52:18 2018

@author: Administrator
"""
#%%
import smtplib

server = smtplib.SMTP('smtp-mail.outlook.com', 587)
server.ehlo()
server.starttls()
server.ehlo()
server.login("ramya_ramesh@outlook.com", "Dakshan04")
from_addr = "ramya_ramesh@outlook.com"
to_addr_list = "jacklinramya@gmail.com"
subject = 'test mail'
message = "YOUR MESSAGE!"
header  = 'From: %s\n' % from_addr
header += 'To: %s\n' % "jacklinramya@gmail.com" #','.join(to_addr_list)
header += 'Subject: %s\n\n' % subject
message = header + message
print(header)
server.sendmail("ramya_ramesh@outlook.com", "jacklinramya@gmail.com", message)
server.quit()


#%%
import smtplib
 
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login("rameshramyadevi@gmail.com", "Dakshan04")
 
msg = "YOUR MESSAGE!"
server.sendmail("rameshramyadevi@gmail.com", "jacklinramya@gmail.com", msg)
server.quit()

#%%


import smtplib
#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEText import MIMEText
 
 
fromaddr = "rameshramyadevi@gmail.com"
toaddr = "jacklinramya@gmail.com"
'''msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "SUBJECT OF THE MAIL"
 
body = "YOUR MESSAGE HERE"
msg.attach(MIMEText(body, 'plain'))'''
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "Dakshan04")
#text = msg.as_string()
server.sendmail(fromaddr, toaddr, "dsfdsfsdfsd")
server.quit()

#%%

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
 
fromaddr = "rameshramyadevi@gmail.com"
toaddr = "jacklinramya@gmail.com"
 
msg = MIMEMultipart()
 
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "SUBJECT OF THE EMAIL"
 
body = "TEXT YOU WANT TO SEND"
 
msg.attach(MIMEText(body, 'plain'))
 
filename = "NAME OF THE FILE WITH ITS EXTENSION"
attachment = open("PATH OF THE FILE", "rb")
 
part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
 
msg.attach(part)
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "YOUR PASSWORD")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()

#%%