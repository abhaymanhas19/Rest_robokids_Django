from django.contrib import admin
from django.urls import path, include
from apps.notification import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("notification", views.notification, basename="notification")


urlpatterns = [] + router.urls
