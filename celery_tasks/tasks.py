from celery import Celery
from django.core.mail import send_mail

from Plog import settings
import django
# 搭建环境
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Plog.settings")
django.setup()  # 调用django的setup方法，完成环境的初始化

# 创建一个celery的对象, 并设置中间人(broker),第一参数可以任意字符串，但一般为celery_tasks.task , 第二个参数为设置中间人，格式是redis：//ip:port/（第几个数据库）

app = Celery('celery_tasks.task', broker='redis://192.168.145.129:6379/7')


#定义任务函数
@app.task
def send_register_active_email(to_email, token):   # 可接收参数或者不接受参数
    '''发送激活邮件'''

    '''组织邮件信息'''
    subject = 'Plog注册激活'  # 主题
    message = ''  # 正文
    sender = settings.EMAIL_FROM  # 发送方
    receiver = [to_email]  # 邮件的接收者
    html_message = "<h1>欢迎您成为Plog的注册会员，请点击链接完成激活状态</h1><br /><a href='http://192.168.145.129:8000/user/active/{token}'>激活</a>".format(
        token=token)  # 显示html文档格式

    # django.core.mail 这个包中的send_mail函数，第一个参数为主题， 第二个参数为正文
    # 第三个参数为发送方，第四个参数为接收方，它是一个列表，可以对多个接收者发送邮件，第四个参数为html语言的内容
    send_mail(subject, message, sender, recipient_list=receiver, html_message=html_message)