import pytest
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


class CategoryTests(APITestCase):

    client = APIClient()

    def test_create_create(self):
        url = "/generate-otp/"
        data = {"mobile": "9162173800", "otp": "0654"}
        response = self.client.post(url, data, format="json")
        self.assertEquals(response.data, data)


# class RegisterTests(APITestCase):
#    client=APIClient()
#    def test_create_create(self):
#       url='/register/'
#       data={'first_name':'DEF','user_type':'STUDENT','mobile':'9162173800','otp':'3832','name':'wadhwa','password':'shubham@1234'}
#       response=self.client.post(url)
#       self.assertEquals(response.data,data)


class LoginTests(APITestCase):
    client = APIClient()

    def test_login(self):
        url = "/login/"
        data = {"mobile": "9162173822", "password": "admin"}
        response = self.client.post(url, data, format="json")
        self.assertEquals(response.data, data)
