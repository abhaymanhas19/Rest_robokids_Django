from distutils.command.upload import upload
from mimetypes import MimeTypes
from random import choices
from django.db import models
from django.forms import NullBooleanField

from django.utils.translation import gettext_lazy as _
from apps.utils.models import TimeStampModel
from django.contrib.auth import get_user_model

User = get_user_model()
from apps.user.models import *
from django.db.models import *
from django.utils import timezone


class Certificate(TimeStampModel):
    CATEGORY_CHOICES = [
        ("Posts", "Posts"),
        ("Likes", "Likes"),
        ("Followers", "Followers"),
    ]
    certificate = models.ImageField(upload_to="certificates")
    c_type = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100)
    minimnum = models.CharField(max_length=100)
    maximum = models.CharField(max_length=100)
    signature = models.ImageField(upload_to="certificates", null=True, blank=True)

    def __str__(self):
        return self.c_type

    # @classmethod
    # def imagename(cls,certificate,name):
    #     data=cls.objects.filter(certificate=certificate)
    #     if data.exist():
    #         return cls.objects.filter(name=name)


class GradeNumber(TimeStampModel):
    CATEGORY_CHOICES = [("post", "post"), ("like", "like"), ("follow", "follow")]
    g_type = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100)
    minimum = models.CharField(max_length=100)
    maximum = models.CharField(max_length=100)


class PostHashTags(models.Model):
    hashtag = models.CharField(max_length=200, null=False)

    def __str__(self):
        return self.hashtag


class Post(TimeStampModel):
    # post = models.FileField(_("Post"), upload_to="media")
    caption = models.CharField(_("Caption"), max_length=255)
    description = models.TextField(_("Description"))
    # material = models.CharField(_("Material"), max_length=255)
    hashtags = models.ManyToManyField(
        PostHashTags, related_query_name="posts", blank=True )
    # thumbnail = models.ImageField(_('thumbnail'),upload_to='thumbs',blank=True,null=True)
    parent = models.ForeignKey("self",null=True,blank=True,on_delete=models.CASCADE,)
    is_approved = models.BooleanField(_("Is Approved"), default=False)
    is_abused = models.BooleanField(_("ReportAbused"), default=False)
    rating = models.IntegerField(_("Rating"), blank=True, null=False, default=0)
    latitude = models.FloatField(blank=True, null=True)
    longtitude = models.FloatField(blank=True, null=True)
    
    image=models.ImageField(upload_to='media', null=True,blank=True)
    video=models.FileField(upload_to='media', null=True,blank=True)
    # @classmethod
    # def gradepost(cls,created_by):
    #     data = cls.objects.filter(created_by=created_by,is_approved=True).count()
    #     if 1 <= data <= 23:
    #         return "New User"
    #     if 24 <= data <= 99:
    #         return "Experienced"
    #     if data > 100:
    #         return "Proficient"
    #     return None

    @classmethod
    def gradepost(cls, created_by):
        data = cls.objects.filter(created_by=created_by, is_approved=True).count()
        grade = (
            GradeNumber.objects.filter(maximum__lte=data, g_type="post").all()
            .values("name", "minimum", "maximum")
        )
        return grade

    @classmethod
    def postcertificate(cls, created_by):
        total_posts = cls.objects.filter(
            created_by=created_by, is_approved=True
        ).count()
        certificates = (
            Certificate.objects.filter(maximum__lte=total_posts, c_type="post").all().values()
        )
        return certificates

    def __str__(self):
        return self.caption


class PendingPost(Post):
    class Meta:
        proxy = True
        verbose_name = "PendingPost"

    def __str__(self):
        return self.caption


class PostCertificate(TimeStampModel):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="postcertificate",blank=True,null=True,
    )
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="usercertificate",blank=True,null=True,)
    follow = models.ForeignKey(FollowRequest, on_delete=models.CASCADE, blank=True, null=True,)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, blank=True, null=True)
    certificate_image = models.ImageField(upload_to="usercirtificate", null=True, blank=True)

    def __str__(self):
        return str(self.certificate)


class PostItem(TimeStampModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_items")
    data = models.FileField(_("data"), upload_to="post_items", blank=True, null=True)
    thumbnail = models.FileField(
        _("thumbnail"), upload_to="thumbnails", blank=True, null=True
    )
    mime_type = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.data)


class Like(TimeStampModel):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    @classmethod
    def likecertificate(cls, post_id):
        data = cls.objects.filter(post_id=post_id).count()
        certificates = Certificate.objects.filter(maximum__lte=data, c_type="likes").all()
        return certificates

    def __str__(self):
        return str(self.post)


class Comment(TimeStampModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent_comment = models.ForeignKey("self",null=True,blank=True,on_delete=models.CASCADE,)
    body = models.TextField(_("Body"))
    is_abused = models.BooleanField(_("ReportAbused"), default=False)

    def __str__(self):
        return self.body


class LikeComment(TimeStampModel):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likecomment" )


class ReportAbuse(TimeStampModel):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="posts", blank=True, null=True
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="commment",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user", blank=True, null=True
    )
    reason = models.TextField()


class Event(TimeStampModel):
    name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to="media/")
    description = models.TextField()
    location = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(default=django.utils.timezone.now)
    time = models.TimeField(default=django.utils.timezone.now)
