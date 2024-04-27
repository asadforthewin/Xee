import html
from django.core.mail import mail_admins, send_mail, BadHeaderError
from django.shortcuts import render


def say_hello(request):
    
    try:
        mail_admins('subject', 'messsage', html_message='i am good')
    except BadHeaderError:
        pass 

    return render(request, 'hello.html',{'name':'asad'})  