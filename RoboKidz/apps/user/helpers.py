import requests
from django.shortcuts import render, HttpResponse
from RoboKidz.settings.production import *
from RoboKidz.settings.development import *
from RoboKidz.settings.base import *
from .models import *
import logging

# create an instance of the logger
logger = logging.getLogger()



def SendOTP(message, mobile):
    # message = f"Your OTP for registration to the Clapz Platform is {otp}. The OTP is valid for 5 minute.Please do not share this OTP with anyone for security reasons. Best Regards, Clapz Team"
    url = f"{SMS_BASE_URL}apikey={SMS_API_KEY}&sender={API_SENDER}&mobileno={mobile}&text={message}"
    response = requests.post(url, headers={}, data={})
    print(response)
    return True if response.status_code == 200 else False









