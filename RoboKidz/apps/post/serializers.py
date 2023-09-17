from rest_framework import serializers
from apps.user.serializers import *

# from apps.user.models import Follow
from .models import *
from rest_framework import serializers, exceptions
from apps.post import models
import re
from apps.post.models import Post
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models import F

from PIL import Image

User = get_user_model()
import cv2
import numpy as np
from PIL import ImageDraw


class PostHashtagSerializer(serializers.ModelSerializer):
    hashtag = serializers.CharField()

    class Meta:
        model = PostHashTags
        fields = (
            "id",
            "hashtag",
        )


class ResponsePostItemSerializer(serializers.ModelSerializer):
    created_by = CreatedBySerializer()
    updated_by = CreatedBySerializer()

    class Meta:
        model = PostItem
        fields = (
            "id",
            "post",
            "data",
            "thumbnail",
            "mime_type",
            "created_by",
            "updated_by",
            "created_at",
            "updated_by",
        )
        read_only_fields = (
            "thumbnail",
            "mime_type",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )


class PostItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostItem
        fields = (
            "id",
            "post",
            "data",
            "thumbnail",
            "mime_type",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        )
        read_only_fields = (
            "thumbnail",
            "mime_type",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        )

    def create(self, validated_data):
        # ff =ffmpy.FFmpeg(inputs={validated_data["data"]: None}, outputs={"media/"+validated_data['data']+"_thumbnail1.png": ['-ss', '00:00:4', '-vframes', '1']})
        # thumbnail_path= "media/"+validated_data['data']+"_thumbnail1.png"

        # video_input_path = validated_data['data']
        # img_output_path = 'thumbnail.jpg'
        # subprocess.call(['ffmpeg', '-i', video_input_path, '-ss', '00:00:00.000', '-vframes', '1',img_output_path])
        validated_data["mime_type"] = getattr(
            validated_data.get("data"), "content_type", None
        )

        # validated_data['mime_type']=validated_data.get('data').content_type
        data = PostItem.objects.create(**validated_data)
        return data


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "parent",
            "caption",
            "description",
            "hashtags",
            "rating",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "rating",
            "hashtags",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

 
    def validate(self, attr):
        parent = attr.get("parent")
        if parent and not parent.is_approved:
            raise serializers.ValidationError("Can not share non-approved posts")
        if parent and parent.parent:
            raise serializers.ValidationError("Can not share a shared post")
      
        return attr

    def create(self, validated_data):
        hashtags = re.findall(r"#\w+", validated_data["caption"])
        hashtags += re.findall(r"#\w+", validated_data["description"])
        post = Post.objects.create(**validated_data)
        tag_ids = []
        for hashtag in hashtags:
            tag, _ = PostHashTags.objects.get_or_create(hashtag=hashtag)
            tag_ids.append(tag.id)
        post.hashtags.add(*tag_ids)
        post.save()
        return post


class SearchSerializer(serializers.Serializer):
    search = serializers.CharField()


class HastagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostHashTags
        fields = ("id", "hashtag",)


class ParentPostItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "caption",
            "description",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "updated_by", "created_at", "updated_at",)


        


class ParentSerializer(serializers.ModelSerializer):
    created_by = UpdatedBySerialzier()
    updated_by = UpdatedBySerialzier()
    items = serializers.SerializerMethodField()

    def get_items(self, data_obj):
        items = data_obj.post_items.all()
        return PostItemSerializer(instance=items, many=True, context=self.context).data

    class Meta:
        model = Post
        fields = (
            "id",
            "caption",
            "description",
            "hashtags",
            "items",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "updated_by", "created_at", "updated_at",)


class PostResponseSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()
    share = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    is_like = serializers.SerializerMethodField()
    is_share = serializers.SerializerMethodField()
    hashtags = HastagSerializer(many=True)
    created_by = CreatedBySerializer()
    updated_by = CreatedBySerializer()
    parent = ParentSerializer()
    # parent = serializers.SerializerMethodField()
    postcertificate = serializers.SerializerMethodField()
    gradepost = serializers.SerializerMethodField()
    likecertificate = serializers.SerializerMethodField()
    # ImageName=serializers.SerializerMethodField()
    def get_gradepost(self, data_obj):
        data = Post.gradepost(created_by=data_obj.created_by)
        return data

    # def get_postcertificate(self, data_obj):
    #     certificates = Post.postcertificate(created_by=data_obj.created_by)
    #     return certificates
    def get_postcertificate(self, data_obj):
        data = PostCertificate.objects.filter(post=data_obj).values(
            "post",
            certificateimage=F("certificate__certificate"),
            C_tyep=F("certificate__c_type"),
            Maximum=F("certificate__maximum"),
            Minimum=F("certificate__minimnum"),
            Name=F("certificate__name"),
        )
        return data

    def get_likecertificate(self, data_obj):
        like = Like.likecertificate(post_id=data_obj.id)
        return like

    # def get_parent(self, data_obj):
    #     if not data_obj.parent:
    #         return
    #     return PostResponseSerializer(data_obj.parent, context=self.context).data

    def get_is_share(self, data_obj):
        return Post.objects.filter(post=data_obj.parent).exists()


    def get_is_like(self, data_obj):    
        return Like.objects.filter(
            post=data_obj, created_by=self.context["request"].user
        ).exists()

    def get_like(self, data_obj):
        like = data_obj.likes.all().count()
        return like

    def get_share(self, obj):
        share = obj.post_set.all().count()
        return share

    def get_comment(self, data_obj):
        comment = data_obj.comments.all().count()
        return comment

    def get_items(self, data_obj):
        items = data_obj.post_items.all()
        return PostItemSerializer(instance=items, many=True, context=self.context).data

    class Meta:
        model = models.Post
        fields = (
            "id",
            "caption",
            "description",
            "image",
            "video",
            "hashtags",
            "parent",
            "created_by",
            "updated_by",
            "gradepost",
            "is_like",
            "is_share",
            "rating",
            "items",
            "like",
            "share",
            "comment",
            "created_at",
            "updated_at",
            "postcertificate",
            "likecertificate",
        )
        read_only_fields = (
            "created_by",
            "updated_by",
            "rating",
            "hashtags",
            "created_at",
            "updated_at",
        )
        # depth = 1


class LikeResponseSerializer(serializers.ModelSerializer):
    post = PostSerializer()
    created_by = CreatedBySerializer()
    updated_by = CreatedBySerializer()

    class Meta:
        model = Like
        fields = (
            "id",
            "created_by",
            "post",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "updated_by", "created_at", "updated_at",)


class LikeSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        post = attrs.get("post")

        liked = Like.objects.filter(
            created_by=self.context["request"].user, post=post
        ).exists()
        if liked:
            raise ValidationError("user already liked post")
        return super().validate(attrs)

    class Meta:
        model = Like
        fields = (
            "id",
            "created_by",
            "post",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "updated_by", "created_at", "updated_at",)


# class ResponseDislikeSerializer(serializers.ModelSerializer):
#     created_by=CreatedBySerializer()
#     updated_by=CreatedBySerializer()
#     class Meta:
#         model=Like
#         fields=('id','post','created_by','updated_by','created_at','updated_at')
#         read_only_fields=('id','post','created_by','updated_by','created_at','updated_at')


class UnLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = (
            "id",
            "created_by",
            "post",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "updated_by", "created_at", "updated_at",)


class ChildCommentViewSerializer(serializers.ModelSerializer):
    created_by = CreatedBySerializer(read_only=True)
    updated_by = CreatedBySerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "parent_comment",
            "post",
            "body",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "updated_by", "created_at", "updated_at",)


class CommentSerializer(serializers.ModelSerializer):
    # created_by = CreatedBySerializer(read_only=True)
    # updated_by = CreatedBySerializer(read_only=True)
    children = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    def get_children(self, obj):
        child_comments = obj.comment_set.all()
        serializer = CommentSerializer(
            instance=child_comments, context=self.context, many=True
        )
        return serializer.data

    def get_is_liked(self, data_obj):
        return data_obj.likecomment.filter(
            created_by=self.context["request"].user
        ).exists()

    def get_like_count(self, data_obj):
        count = data_obj.likecomment.filter(comment=data_obj.id).count()
        return count

    def validate(self, attrs):
        parent_comment = attrs.get("parent_comment")
        if parent_comment and parent_comment.post.id != attrs.get("post").id:
            raise serializers.ValidationError("Invalid Parent Comment Id")
        return super().validate(attrs)

    class Meta:
        model = Comment
        fields = (
            "id",
            "parent_comment",
            "post",
            "body",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "is_liked",
            "children",
            "like_count",
        )
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "like_count",
        )


class ParentViewSerializer(serializers.ModelSerializer):
    created_by = CreatedBySerializer(read_only=True)
    updated_by = CreatedBySerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "post",
            "body",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "updated_by", "created_at", "updated_at",)


class CommentViewSerializer(serializers.ModelSerializer):
    child = serializers.SerializerMethodField()
    parent_comment = ParentViewSerializer(read_only=True)
    created_by = CreatedBySerializer(read_only=True)
    updated_by = CreatedBySerializer(read_only=True)
    # child = ChildCommentViewSerializer(read_only=True)
    comment = serializers.SerializerMethodField()
    likecomment = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    is_likecomment = serializers.SerializerMethodField()
    likeparentcomment = serializers.SerializerMethodField()

    # def get_comment(self, data_obj):
    #     data =Comment.objects.filter(parent_comment=data_obj.parent_comment)
    #     data1=Comment.objects.filter(created_by=data_obj.created_by).all().count()
    #     if  data:
    #         return data1
    #     return False
    def get_comment(self, data_obj):
        data = Comment.objects.filter(
            comment=data_obj, created_by=data_obj.created_by
        ).count()
        if data:
            return data
        return 0

    def get_likecomment(self, data_obj):
        count = data_obj.likecomment.filter(comment=data_obj.id).count()
        return count
        # data = LikeComment.objects.filter(
        #     comment=data_obj, created_by=data_obj.created_by
        # ).count()
        # if data:
        #     return data
        # return 0


    def get_is_likecomment(self, data_obj):
        data = LikeComment.objects.filter(
            comment=data_obj, created_by=self.context["request"].user
        ).exists()
        if data:
            return True
        return False



    def get_likeparentcomment(self, data_obj):
        data = LikeComment.objects.filter(
            comment=data_obj.parent_comment, created_by=data_obj.created_by
        ).count()
        if data:
            return data
        return 0

    def get_replies(self, data_obj):
        data = Comment.objects.filter(parent_comment=data_obj).count()
        return data

    def get_child(self, obj):
        child_comments = obj.comment_set.all()
        serializer = CommentViewSerializer(instance=child_comments, many=True, context=self.context)
        return serializer.data

    class Meta:
        model = Comment
        fields = (
            "id",
            "parent_comment",
            "post",
            "body",
            "comment",
            "likecomment",
            "is_likecomment",
            "likeparentcomment",
            "replies",
            "child",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

        read_only_fields = ("created_by", "updated_by", "created_at", "updated_at",)


class ResponseLikeCommentSerializer(serializers.ModelSerializer):
    created_by = CreatedBySerializer()
    updated_by = CreatedBySerializer()

    class Meta:
        model = LikeComment
        fields = (
            "id",
            "comment",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "updated_by", "created_at", "updated_at",)


class LikeCommentSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        comment = attrs.get("comment")
        data = LikeComment.objects.filter(
            comment=comment, created_by=self.context["request"].user
        ).exists()
        if data:
            raise ValidationError("comment like already exists")
        return super().validate(attrs)

    class Meta:
        model = LikeComment
        fields = (
            "id",
            "comment",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "updated_by", "created_at", "updated_at",)


class DislikeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeComment
        fields = ("comment", "created_by", "updated_by", "created_at", "updated_at",)
        read_only_fields = ("created_by", "updated_by", "created_at", "uddated_at",)


class ResponseCommentAbuseReportSerializer(serializers.ModelSerializer):
    created_by = CreatedBySerializer()
    updated_by = CreatedBySerializer()

    class Meta:
        model = ReportAbuse
        fields = (
            "id",
            "comment",
            "reason",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )


class CommentAbuseReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAbuse
        fields = (
            "id",
            "comment",
            "reason",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("updated_by", "created_by", "created_at", "updated_at",)


class ResponsePostReportAbuseSerializer(serializers.ModelSerializer):
    created_by = CreatedBySerializer()
    updated_by = CreatedBySerializer()

    class Meta:
        model = ReportAbuse
        fields = (
            "id",
            "post",
            "reason",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fieds = ("created_by", "updated_by", "created_at", "updated_at",)


class PostReportAbuseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAbuse
        fields = (
            "id",
            "post",
            "reason",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "updated_by", "created_by", "updated_by",)


class ResponseUserAbuseSerializer(serializers.ModelSerializer):
    created_by = CreatedBySerializer()
    updated_by = CreatedBySerializer()

    class Meta:
        model = ReportAbuse
        fields = ("id", "user", "created_by", "updated_by", "created_at", "updated_at",)
        read_only_fields = ("created_by", "updated_by", "created_at", "updated_by",)


class UserReportAbuseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAbuse
        fields = (
            "id",
            "user",
            "reason",
            "created_by",
            "updated_by",
            "created_by",
            "updated_by",
        )
        read_only_fields = ("created_at", "updated_at", "created_by", "updated_by",)


#########


class CreateCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ('certificate',
                    'c_type',
                    'name',
                    'minimnum',
                    'maximum',
                    'signature',)


class GetAllusercirtificate(serializers.ModelSerializer):
    class Meta:
        model = PostCertificate
        fields = (
            "post",
            "user",
            "follow",
            "certificate",
            "certificate_image",
            "created_by",
            "updated_by",
        )


class EventSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = Event
        fields = (
            "name",
            "image",
            "description",
            "location",
            "date",
            "time",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

        read_only_fields = ("created_by", "updated_by", "created_at", "updated_at",)


class EventDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
