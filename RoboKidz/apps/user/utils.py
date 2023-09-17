import requests
from django.shortcuts import render, HttpResponse
from RoboKidz.settings.production import *
from RoboKidz.settings.development import *
from RoboKidz.settings.base import *
from .models import *
import logging

from django.core.mail import EmailMessage
class Util:
    @staticmethod
    def send_mail(data):
        email=EmailMessage(subject=data['email_subject'],body=data['email_body'] , to=[data['to_email']])
        # email=EmailMessage(subject=data['email_subject'],body=data['email_body'])
        email.send()



from django.core.mail import send_mail, EmailMessage

def sendparentemail(data):
    try:
        email=EmailMessage(subject=data['email_subject'],body=data['email_body'] ,
              from_email = EMAIL_HOST ,to=[data['to_email']])
        email.send()
        print("Email Send Suscessfully")
    except Exception as e:
        print(e)