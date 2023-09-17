# from copy import deepcopy
# from turtle import pos
from re import T
from django.shortcuts import get_object_or_404, render
from apps.user.serializers import *

from apps.utils.permissions import IsCurrentUserOwnerOrReadOnly
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import (
    authentication,
    permissions,
    generics,
    mixins,
    viewsets,
    status,
)
from datetime import datetime
from django.conf import settings

# Create your views here.
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework import viewsets
from apps.post import models, serializers
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from typing import List
from django.db.models import Q
from apps.user import models
from apps.post import models
import mimetypes

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pathlib import Path


from django.contrib.auth import get_user_model

User = get_user_model()

from PIL import Image
from io import BytesIO
from django.utils.crypto import get_random_string
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from rest_framework.decorators import action
from django.db.models import Q, F
from rest_framework.decorators import action
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from .models import Certificate


class PostAPIView(viewsets.ModelViewSet):
    serializer_class = serializers.PostSerializer
    queryset = models.Post.objects.all()
    permission_classes = (IsCurrentUserOwnerOrReadOnly,)

    def get_serializer(self, *args, **kwargs):
        if self.request.method in ["POST", "PATCH"]:
            serializer_class = self.get_serializer_class()
        else:
            serializer_class = PostResponseSerializer

        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    # def update(self, request, *args, **kwargs):
    # partial = kwargs.pop('partial', False)
    # instance = self.get_object()
    # serializer = self.PostSerializer(instance, data=request.data, partial=partial)
    # serializer.is_valid(raise_exception=True)
    # self.perform_update(serializer)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = PostResponseSerializer(
            instance=serializer.instance,
            context={
                "request": request,
            },
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self): 
        h = Post.objects.filter(created_by=self.request.user).values('created_by')                       

        friends = FollowRequest.objects.filter(status="accepted",created_by=self.request.user.id)
        user_friends = []
        for i in friends:
            user_friends.append(i.receiver.id)
        return Post.objects.filter( 
            Q(is_approved=True,created_by__is_private=False)
            | Q(is_approved=True, created_by__in=user_friends)
            | Q(is_approved=True, created_by=self.request.user.id))

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    @action(detail=True, methods=["get"], name="user_posts")
    def user_posts(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        data = []
        if (
            target_user != request.user
            and target_user.is_private
            and not FollowRequest.is_friends(target_user, request.user)
        ):
            return Response({"data": data})
        queryset = self.queryset.filter(created_by=target_user,is_approved=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    



class MyLikedPostAPIView(generics.ListAPIView):
    serializer_class = PostResponseSerializer

    def get_queryset(self):
        return Post.objects.filter(likes__created_by=self.request.user)


class PostItemAPIView(viewsets.ModelViewSet):
    serializer_class = serializers.PostItemSerializer
    queryset = models.PostItem.objects.all()
    http_method_names: List[str] = ["post", "get"]
    permission_classes = (IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        if self.request.method == "POST":
            serializer_class = self.get_serializer_class()
        else:
            serializer_class = ResponsePostItemSerializer
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = ResponsePostItemSerializer(
            instance=serializer.instance, context={"request": request}
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class LikeAPIView(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    http_method_names: List[str] = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = LikeResponseSerializer(
            instance=serializer.instance, context={"request": request}
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class DisLikeAPIView(viewsets.ModelViewSet):
    serializer_class = UnLikeSerializer
    queryset = Like.objects.all()
    http_method_names: List["str"] = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        disliked, message = self.dislike(serializer)
        headers = self.get_success_headers(serializer.data)
        # data=ResponseDislikeSerializer(instance=serializer.instance,context={"request":request}).data
        return Response(
            {"message": message, "status": disliked},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def dislike(self, serializer):
        liked_post = Like.objects.filter(
            post=serializer.data["post"], created_by=self.request.user
        ).first()
        if liked_post:
            liked_post.delete()
            return True, "post Disliked"
        return False, "Not found"


class DislikeComment(viewsets.ModelViewSet):
    serializer_class = DislikeCommentSerializer
    queryset = LikeComment.objects.all()
    http_method_names: List[str] = [
        "post",
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        commentdislike, message = self.dislike(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": message, "status": commentdislike},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def dislike(self, serializer):
        data = LikeComment.objects.filter(
            comment=serializer.data["comment"], created_by=self.request.user
        )
        if data:
            data.delete()
            return True, "dislike comment"
        return False, "not found"


class commentAPIView(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    http_method_names: List[str] = ["post","delete","get",
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = CommentViewSerializer(
            instance=serializer.instance, context={"request": request}
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class PostsCommentAPIView(generics.RetrieveAPIView):
    queryset = ""
    serializer_class = CommentViewSerializer

    def get(self, request, post_id):
        queryset = Comment.objects.filter(post=post_id, parent_comment=None)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, context={"request": request}, many=True
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# class ShareAPIView(viewsets.ModelViewSet):
#     serializer_class = ShareSerializer
#     queryset = Share.objects.all()
#     http_method_names: List[str] = ["post", "delete"]

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user, updated_by=self.request.user)


class MyProfileAPIView(generics.GenericAPIView):
    serializer_class = AllProfileSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, context={"request": request})
        return Response({"data": serializer.data})


class MyPostAPIView(generics.ListAPIView):
    serializer_class = PostResponseSerializer

    def get_queryset(self):
        return Post.objects.filter(created_by_id=self.request.user.id, is_approved=True)


class SharePostAPIView(generics.ListAPIView):
    serializer_class = PostResponseSerializer

    def get_queryset(self):
        return Post.objects.filter(created_by=self.request.user)


class HastTagApi(viewsets.ModelViewSet):
    serializer_class = PostHashtagSerializer
    queryset = PostHashTags.objects.all()
    permission_classes = (IsAuthenticated,)


class hashTag(generics.ListAPIView):
    queryset = PostHashTags.objects.all()
    serializer_class = PostHashtagSerializer


class SearchAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SearchSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        # search_val = serializer.validated_data["search"]
        search_val = request.data["search"]
        friends = FollowRequest.objects.filter(status="accepted",created_by=self.request.user.id)
        user_friends = []
        for i in friends:
            user_friends.append(i.receiver.id)


        posts = Post.objects.filter(
            Q(caption__icontains=search_val, is_approved=True)
            | Q(description__icontains=search_val,is_approved=True)
            | Q(created_by__mobile__icontains=search_val,is_approved=True)
            | Q(created_by__username__icontains=search_val,is_approved=True)
            | Q(created_by__name__icontains=search_val,is_approved=True)
            | Q(created_by__id__contains=search_val,is_approved=True)
            | Q(created_by__email__icontains=search_val,is_approved=True)
            | Q(created_by__first_name__icontains=search_val,is_approved=True)
          
            
        ).filter( Q(is_approved=True,created_by__is_private=False)
            | Q(is_approved=True, created_by__in=user_friends)
            | Q(is_approved=True, created_by=self.request.user.id))

        users = User.objects.filter(
            Q(user_type__icontains=search_val)
            | Q(username__icontains=search_val)
            | Q(email__icontains=search_val)
            | Q(school__name=search_val)
            | Q(first_name__icontains=search_val)
            | Q(name__icontains=search_val)
            # | Q(mobile=search_val)
            | Q(state__icontains=search_val)
            | Q(city__icontains=search_val)
            | Q(grade__name=search_val)
            | Q(parent_email=search_val)
            | Q(address__icontains=search_val)
            | Q(workspace__icontains=search_val)
            | Q(position__icontains=search_val)
            | Q(qualification__icontains=search_val)
        )
        posts_data = PostResponseSerializer( posts, context={"request": request}, many=True).data
        users = AllProfileSerializer(users, context={"request": request}, many=True ).data

        return Response({"posts": posts_data , 'users_data':users})


class ShareAPIView(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    # queryset = Post.objects.all()
    http_method_names: List[str] = ["post", "get"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = PostResponseSerializer(
            instance=serializer.instance, context={"request": request}
        ).data

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user, updated_by=self.request.user, is_approved=True
        )

    def get_queryset(self):
        return Post.objects.filter(is_approved=True)


class ViewSharedPostsAPIView(viewsets.ModelViewSet):
    serializer_class = PostResponseSerializer
    queryset = Post.objects.all()
    http_method_names: List[str] = ["get"]


class LikeCommentSerializer(viewsets.ModelViewSet):
    serializer_class = LikeCommentSerializer
    queryset = LikeComment.objects.all()
    http_method_names: List[str] = ["post","get"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = ResponseLikeCommentSerializer(
            instance=serializer.instance, context={"request": request}
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class PostReportAbuseAPI(viewsets.ModelViewSet):
    serializer_class = PostReportAbuseSerializer
    queryset = ReportAbuse.objects.all()
    http_method_names: List[str] = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = ResponsePostReportAbuseSerializer(
            instance=serializer.instance, context={"request": request}
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class CommentReportAbuseAPI(viewsets.ModelViewSet):
    serializer_class = CommentAbuseReportSerializer
    queryset = ReportAbuse.objects.all()
    http_method_names: List[str] = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = ResponseCommentAbuseReportSerializer(
            instance=serializer.instance, context={"request": request}
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class UserReportAbuseAPI(viewsets.ModelViewSet):
    serializer_class = UserReportAbuseSerializer
    queryset = ReportAbuse.objects.all()
    http_method_names: List[str] = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = ResponseUserAbuseSerializer(
            instance=serializer.instance, context={"request": request}
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class PendingPostAPIView(viewsets.ModelViewSet):
    serializer_class = PostResponseSerializer
    queryset = Post.objects.all()
    http_method_names: List[str] = ["get","delete"]

    def get_queryset(self):
        return Post.objects.filter(created_by=self.request.user, is_approved=False)


class EventDataAPIView(APIView):
    def get(self, request, *args, **kwargs):
        data = Event.objects.all().values()
        if not data:
            return Response({"event": "Event  Not Found", "status": 400})
        return Response({"event": data, "status": 200})


# class EventDetailAPIView(generics.RetrieveAPIView):
#     serializer_class = EventSerializer
#     def get(self, request, id):
#         queryset = Event.objects.filter(id=id)
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(
#                 page, context={"request": request}, many=True
#             )
#             return self.get_paginated_response(serializer.data)

#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)


class EventDetailAPIView(generics.RetrieveAPIView):
    serializer_class = EventSerializer

    def get(self, request, id):
        queryset = Event.objects.filter(id=id)
        if not queryset:
            return Response({"msg": "Not Found EventId", "status": 400})
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# class EventAPIView(viewsets.ModelViewSet):
#     serializer_class=EventSerializer
#     queryset=Event.objects.all()
#     http_method_names: List[str]=['get']


class CrateCirtificates(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CreateCertificateSerializer


class GetUsergeneratedCirtifiates(viewsets.ModelViewSet):
    serializer_class = GetAllusercirtificate
    queryset = PostCertificate.objects.all()
    http_method_names: List[str] = ["post", "get"]


# class PostCertificateAPI(generics.GenericAPIView):
#     serializer_class=PostCertificateSerializer
#     def post(self,request,*args,**kwargs):
#         serializer=self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         RA=serializer.save()
#         return Response({'msg':'certificate create successfully','status':200})


def data(request):
    return render(request, "post/b.html")


def data1(request):
    return render(request, "post/index.html")
