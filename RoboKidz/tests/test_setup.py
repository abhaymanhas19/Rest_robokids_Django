from rest_framework.test import APITestCase
from django.urls import reverse


class TestSetUp(APITestCase):
    def setUp(self):
        self.generateotp_url = reverse("generateotp")

        user_data = {"mobile": "9162173800", "otp": "0654"}
        return super().setUp()

    def tearDown(self):
        return super().tearDown()
