from django.shortcuts import render
from apps.notification.serializers import NotificationSerializer
from .models import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from typing import List
from .serializers import *
from rest_framework import (
    authentication,
    permissions,
    generics,
    mixins,
    viewsets,
    status,
)

# Create your views here.
class notification(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    http_method_names: List[str] = ["get", "patch"]

    def get_serializer(self, *args, **kwargs):
        if self.request.method in ["POST","PATCH"]:
            serializer_class = self.get_serializer_class()
        else:
            serializer_class = NotificationResponseSerializer
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        return Notification.objects.filter(notified_to=self.request.user.id)
         

    

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = NotificationSerializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


# class Notification(generics.GenericAPIView):
#     def post(self,request,*args,**kwargs):
#         serializer=self.get_serializer(data=request.data)
           
