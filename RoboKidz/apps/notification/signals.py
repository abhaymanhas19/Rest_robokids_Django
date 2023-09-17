from django.db.models.signals import post_save, pre_save

# from django.contrib.auth.models import User
from django.dispatch import receiver
from apps.post.models import Like, LikeComment, Post, Comment
from .models import Notification
from apps.user.models import FollowRequest
from django.db.models import signals


@receiver(post_save, sender=Like)
def post_save_like(sender, instance, created, **kwargs):
    if instance.created_by==instance.post.created_by:
        return False
    Notification.objects.create(
        performed_by=instance.created_by,
        notified_to=instance.post.created_by,
        message=instance.created_by.username + " " +" Liked on your posts.",
        message_key="post like",
    )


@receiver(post_save, sender=LikeComment)
def post_save_like_comment(sender, instance, created, **kwargs):
    if instance.created_by==instance.comment.created_by:
        return False
    Notification.objects.create(
        performed_by=instance.created_by,
        notified_to=instance.comment.created_by,
        message=instance.created_by.username + " " +" Liked  on one  your comment. ",
        message_key="comment like",
    )


@receiver(post_save, sender=FollowRequest)
def post_save_follow_request(sender, instance, created, **kwargs):
    if instance.status == "pending":
        Notification.objects.create(
            performed_by=instance.created_by,
            notified_to=instance.receiver,
            message=instance.created_by.username + " " +"send your follow request",
            message_key="follow-request-sent",
        )


@receiver(post_save, sender=FollowRequest)
def post_save_accept_follow_request(sender, instance, created, **kwargs):
    if instance.status == "accepted":
        Notification.objects.create(
            performed_by=instance.created_by,
            notified_to=instance.receiver,
            message=instance.created_by.username + " " + "accepted your follow request",
            message_key="follow-request-accepted",
        )


@receiver(post_save, sender=Comment)
def post_save_comment(sender, instance, created, **kwargs):
    if instance.created_by==instance.post.created_by:
        return False
    Notification.objects.create(
        performed_by=instance.created_by,
        notified_to=instance.post.created_by,
        message=instance.created_by.username +" "+ "commented on  your post. ",
        message_key="comment send",
    )


# @receiver(post_save, sender=FollowRequest)
# @receiver(post_save, sender=Post)
# def update_user_profile(sender, instance, created, **kwargs):
#     if sender.__name__==['FollowRequest']:
#         if instance.status=='accepted':
#             if sender.__name__==['Post']:
#                 Notification.objects.create(performed_by=instance.created_by,notified_to=instance.created_by,message=instance.created_by.username +" "+ "commented on  your post. ",message_key="comment send",)
          
        
            








