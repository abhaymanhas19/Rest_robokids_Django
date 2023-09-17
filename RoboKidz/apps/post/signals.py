from .models import Like
from .models import *
from . models import Post
from apps.user.models import FollowRequest
from PIL import Image, ImageDraw, ImageFont
import datetime
import uuid
from django.db.models.signals import post_save, pre_delete, pre_save

from django.dispatch import receiver

from RoboKidz.settings import base

from django.core.mail import send_mail, EmailMessage
import boto3
from botocore.exceptions import ClientError
import os
from moviepy.editor import VideoFileClip
from botocore.exceptions import ClientError
import boto3
from moviepy.editor import VideoFileClip
from django.core.files.base import File
from io import BytesIO
import tempfile
import sys
import zlib
import moviepy.editor as mp

from django.core.files.storage import default_storage
# s3 = boto3.client(os.getenv("Service_Name"),os.getenv("AWS_ACCESS_KEY_ID"),os.getenv("AWS_SECRET_ACCESS_KEY"),os.getenv("AWS_S3_REGION_NAME"))

def Send_Cir_email(subject, message, att,email):
    try:
        email_from = base.EMAIL_HOST
        email_msg = EmailMessage(subject, message, email_from, [email])
        email_msg.attach_file(att)
        email_msg.send()
        print("Email Send Suscessfully")
    except Exception as e:
        print(e)

def gencirttificate(cir_image,cir_sign, username, c_type, cname):
    file_name = uuid.uuid4()
    now = datetime.datetime.now()
    today = now.strftime("%d-%m-%Y")
    img = Image.open(cir_image)
    image_editable = ImageDraw.Draw(img)    
    font = ImageFont.truetype("RoboKidz/asserts/FreeMono.ttf", 48)
    image_editable.text((700, 500), username, fill=(0, 0, 0), font=font)
    image_editable.text((700, 700), cname, fill=(0, 0, 0), font=font)
    image_editable.text((950, 800), c_type, fill=(0, 0, 0), font=font)
    font = ImageFont.truetype("RoboKidz/asserts/FreeMono.ttf", 38)
    image_editable.text((500, 900), today, fill=(0, 0, 0), font=font)
    sign = Image.open(cir_sign)
    new_img =sign.resize((300, 70))
    img.paste(new_img, (950,880),)
    img.show()
    img.save(f"RoboKidz/media/usercirtificate/Cirtificate{file_name}.png")
    return file_name

@receiver(post_save, sender=Like)
def likecertificate(sender, instance, **kwargs):
    name = instance.post.created_by
    email = instance.post.created_by.email
    username = str(name)
    c = Like.objects.filter(post_id=instance.post.id).count()
    try:
        c_id = Certificate.objects.filter(c_type="Likes", maximum=c).all()
        try:                
            for i in c_id:
                print(i.name, i.certificate, i.c_type, i.name,i.signature)
            cir_id = i.id
            cir_image = i.certificate
            cir_sign = i.signature
            c_type = str(i.c_type)
            cname = str(i.name)
            imgname = gencirttificate(cir_image, cir_sign,username,c_type, cname, )

            cir = PostCertificate.objects.create(
                post_id=instance.post.id,
                user_id=instance.post.created_by.id,
                created_by_id=instance.post.created_by.id,
                certificate_id=cir_id,
                updated_by_id=instance.post.created_by.id,
                certificate_image=f"/usercirtificate/Cirtificate{imgname}.png",
            )
            att = cir.certificate_image
            cir_image = f"RoboKidz/media/{att}"
            subject = " Robokidz Cirtificate"
            message = " Robokidz Eduventures Pvt Ltd We Are so thrilled to hear that you reached your goal"
            Send_Cir_email(subject, message,cir_image,email)

        except Exception as e:
            print(e)
    except Exception as e:
        print(e)



@receiver(post_save, sender=PendingPost)
def PostCirtificate(sender, instance, **kwargs):
    name = instance.created_by
    email = instance.created_by.email
    username = str(name)
    c = Post.objects.filter(created_by_id=instance.created_by.id,is_approved=instance.is_approved).count()
    print("Count" , c)
    try:
        c_id = Certificate.objects.filter(c_type="Posts", maximum=c).all()
        try:
            for i in c_id:
                print(i.name, i.certificate, i.c_type, i.name , i.signature)
            cir_id = i.id
            cir_image = i.certificate
            c_type = str(i.c_type)
            cname = str(i.name)
            cir_sign = i.signature
            imgname = gencirttificate(cir_image,cir_sign ,username,c_type,cname )

            cir = PostCertificate.objects.create(
                post_id=instance.id,
                user_id=instance.created_by.id,
                created_by_id=instance.created_by.id,
                certificate_id=cir_id,
                updated_by_id=instance.created_by.id,
                certificate_image=f"/usercirtificate/Cirtificate{imgname}.png",
            )
            att = cir.certificate_image
            cir_image = f"RoboKidz/media/{att}"
            subject = " Robokidz Cirtificate"
            message = " Robokidz Eduventures Pvt Ltd We Are so thrilled to hear that you reached your goal"
            Send_Cir_email(subject, message,cir_image,email)
        except Exception as e:
            print(e)
    except Exception as e:  
        print(e)


@receiver(post_save, sender=FollowRequest)
def followcirtificate(sender, instance, **kwargs):
    name = instance.receiver.first_name
    username = str(name)
    followcount = FollowRequest.objects.filter(receiver_id=instance.receiver.id).count()
    try:
        c_id = Certificate.objects.filter(c_type="Followers", maximum=followcount).all()
        try:
            for i in c_id:
                print(i.name, i.certificate, i.c_type, i.name , i.signature)
            cir_id = i.id
            cir_image = i.certificate
            c_type = str(i.c_type)
            cname = str(i.name)
            cir_sign = i.signature
            imgname = gencirttificate(cir_image,cir_sign ,username,c_type,cname,)
            user = User.objects.get(id =instance.receiver.id )
            cir = PostCertificate.objects.create(
                user_id = user.id,
                created_by_id=instance.created_by.id ,
                certificate_id=cir_id,
                updated_by_id=user.id,
                certificate_image=f"/usercirtificate/Cirtificate{imgname}.png",
            )
            cir.created_by_id=instance.receiver.id
            cir.save()
            att = cir.certificate_image
            cir_image = f"RoboKidz/media/{att}"
            subject = " Robokidz Cirtificate"
            message = " Robokidz Eduventures Pvt Ltd We Are so thrilled to hear that you reached your goal"
            Send_Cir_email(subject, message,cir_image,user.email)
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)





@receiver(pre_save, sender=PostItem)
def compress_media(sender, instance, **kwargs):
        data = instance.data
        # data = getattr(instance, 'data')
        def filetype(data):
            if data.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return True
            if data.name.lower().endswith(('.mp4', '.mov', '.avi', '.wmv')):
                return False
        status = filetype(data)
        image_field = data
        video_field = data
       # Compress image
        if image_field and status == True:
            im = Image.open(image_field)
            if im.mode == 'RGBA':
                im = im.convert('RGB')
            im_io = BytesIO()
            im.save(im_io, 'JPEG', quality=60)     
            compressed_image = File(im_io, name=image_field.file.name)
            image_field.file = compressed_image

        # Compress video
        #         # Compress video
        if video_field and status==False:
            input_data = video_field.file.read()
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(input_data)
                temp_file_path = temp_file.name
            # Compress video using MoviePy
            video = VideoFileClip(temp_file_path)
            compressed_video = video.resize((640, 360))
            compressed_video_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            compressed_video.write_videofile(compressed_video_file.name, codec='libx264', audio_codec='aac')
            # Save compressed video to media folder
            with open(compressed_video_file.name, 'rb') as f:
                compressed_video_file = File(f)
                compressed_video_path = os.path.join('', compressed_video_file.name.split('/')[-1])
                default_storage.save(compressed_video_path, compressed_video_file)
            instance.data = compressed_video_path

            os.unlink(temp_file_path)
            os.unlink(compressed_video_file.name)







