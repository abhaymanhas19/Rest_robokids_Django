from random import choices
from secrets import choice
from unicodedata import name
from django.dispatch import receiver
from numpy import recarray
from rest_framework import status
from django.conf import settings
from rest_framework import serializers
from yaml import serialize
from apps.user.models import Block, FollowRequest, Grade, School
from apps.utils.enums import UserType
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers, exceptions
from apps.utils.serializers import CustomUserSerializer
import pyotp
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from apps.post.models import *
import requests

User = get_user_model()
from apps.post.models import *
from datetime import date
import requests
from django.db.models import F
from RoboKidz.settings.base import *
from .utils import *


class MyProfileSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    is_profile_completed = serializers.BooleanField(read_only=True)
    followercertificate = serializers.SerializerMethodField()
    followergrade = serializers.SerializerMethodField()
    is_parent_mobile_verified = serializers.SerializerMethodField()
    is_parent_email_verified = serializers.SerializerMethodField()

    def get_is_parent_mobile_verified(self, data_obj):
        return User.objects.filter(
            parent_mobile=data_obj.parent_mobile, parent_mobile_verified=True
        ).exists()

    def get_is_parent_email_verified(self, data_obj):
        return User.objects.filter(
            parent_email=data_obj.parent_email, parent_email_verified=True
        ).exists()

    def get_followergrade(self, data_obj):
        data = FollowRequest.objects.filter(
            created_by=data_obj, status="accepted"
        ).count()
        grade = (
            GradeNumber.objects.filter(maximum__lte=data, g_type="follow")
            .all()
            .values("name", "minimum", "maximum")
        )
        return grade

    # def get_followercertificate(self,data_obj):
    #     data=FollowRequest.objects.filter(created_by=data_obj,status='accepted').count()
    #     certificate=Certificate.objects.filter(maximum__lte=data,c_type='follow').all().values()
    #     return certificate
    def get_followercertificate(self, data_obj):
        data = PostCertificate.objects.all().values(
            "follow",
            certificateimage=F("certificate__certificate"),
            C_tyep=F("certificate__c_type"),
            Maximum=F("certificate__maximum"),
            Minimum=F("certificate__minimnum"),
            Name=F("certificate__name"),
        )
        return data

    def get_followers(self, data_obj):
        data = FollowRequest.objects.filter(
            receiver=data_obj, status="accepted"
        ).count()
        return data

    def get_following(self, data_obj):
        data = FollowRequest.objects.filter(
            created_by=data_obj, status="accepted"
        ).count()
        return data

    class Meta:
        model = User
        fields = (
            "id",
            "profile_image",
            "username",
            "name",
            "first_name",
            "user_type",
            "is_profile_completed",
            "followercertificate",
            "followergrade",
            "email",
            "dob",
            "mobile",
            "bio",
            "followers",
            "following",
            "date_joined",
            "parent_mobile_verified",
            "moile_verified",
            "parent_email_verified",
            "is_parent_mobile_verified",
            "is_parent_email_verified",
            "is_private",             
        )


class AllProfileSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_profile_completed = serializers.BooleanField(read_only=True)
    followercertificate = serializers.SerializerMethodField()
    followergrade = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()

    def get_followergrade(self, data_obj):
        data = FollowRequest.objects.filter(
            created_by=data_obj, status="accepted"
        ).count()
        grade = (
            GradeNumber.objects.filter(maximum__lte=data, g_type="follow")
            .all()
            .values("name", "minimum", "maximum")
        )
        return grade

    def get_followercertificate(self, data_obj):
        data = PostCertificate.objects.all().values("follow",
            certificateimage=F("certificate__certificate"),
            C_tyep=F("certificate__c_type"),
            Maximum=F("certificate__maximum"),
            Minimum=F("certificate__minimnum"),
            Name=F("certificate__name"),
        )
        return data

    def get_is_following(self, data_obj):
        user = self.context["request"].user
        data = FollowRequest.objects.filter(
            receiver=data_obj, status="accepted", created_by=user
        ).exists()
        if data:
            return True
        return False

    def get_request_status(self, data_obj):
        user = self.context["request"].user
        data = FollowRequest.objects.filter(
            Q(receiver=data_obj, status="accepted", created_by=user)
            | Q(receiver=data_obj, status="pending", created_by=user))
        for i in data:
             i.status
        if not data:
            return "empty"
        else:
            return i.status

        # return FollowRequest.is_friends(created_by=self.context["request"].user).exists()
        # data = FollowRequest.objects.filter(
        #     created_by=self.context["request"].user, status="accepted"
        # ).exists()
        # if data:
        #     return True
        # return False

    def get_followers(self, data_obj):
        data = FollowRequest.objects.filter(
            receiver=data_obj, status="accepted"
        ).count()
        return data

    def get_following(self, data_obj):
        data = FollowRequest.objects.filter(
            created_by=data_obj,
            status="accepted",
        ).count()
        return data

    class Meta:
        model = User
        fields = (
            "id",
            "profile_image",
            "username",
            "name",
            "first_name",
            "user_type",
            "is_profile_completed",
            "followercertificate",
            "followergrade",
            "email",
            "dob",
            "mobile",
            "bio",
            "is_following",
            "request_status",
            "followers",
            "following",
            "date_joined",
            "parent_mobile_verified",
            "moile_verified",
            "parent_email_verified", 
            "is_private", 
        )


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_type"] = user.user_type
        return token


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ("name",)


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ("name",)


class GradeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ("name",)


class ProfileSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        username = attrs.get("username")
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError("The email already exists")
        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError("The username already exists")
        return super().validate(attrs)

    class Meta:
        model = User


class StudentProfileSerializer(ProfileSerializer):
    school_name = serializers.CharField(max_length=100, required=False, write_only=True)
    grade_name = serializers.CharField(max_length=100, required=False, write_only=True)
    grade = GradeViewSerializer(read_only=True)
    school = SchoolSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "user_type",
            "first_name",
            "username",
            "is_private",
            "date_joined",
            "dob",
            "name",
            "email",
            "mobile",
            "bio",
            "profile_image",
            "school",
            "grade_name",
            "school_name",
            "state",
            "city",
            "address",
            "pin_code",
            "grade",
            "parent_mobile",
            "parent_email",
        )
        read_only_fields = ("user_type", "mobile", "school", "grade", "date_joined")
        extra_kwargs = {"school": {"read_only": True}, "grade": {"read_only": True}}

    def validate_school_name(self, data):
        if not data:
            return
        school_obj, _ = School.objects.get_or_create(name=data)
        return school_obj

    def validate_grade_name(self, data):
        if not data:
            return
        grade_obj, _ = Grade.objects.get_or_create(name=data)
        return grade_obj

    def create(self, validated_data):
        school_name = validated_data.pop("school_name", None)
        grade_name = validated_data.pop("grade_name", None)
        validated_data["school"] = school_name
        validated_data["grade"] = grade_name
        return super().create(validated_data)

    def update(self, instance, validated_data):
        school_name = validated_data.pop("school_name", None)
        grade_name = validated_data.pop("grade_name", None)
        validated_data["school"] = school_name
        validated_data["grade"] = grade_name
        super().update(instance, validated_data)
        user_name = instance.name        
        header = f"""Dear Parent/Guardian,\n\n 
        We are writing to inform you that your child {user_name} has expressed interest in registering with our education app, Clapz. We are thrilled to have your child on board and look forward to their participation in our platform. Clapz is an educational app that offers a fun and interactive way for children to learn new things. Our platform provides a variety of resources, including videos, games, and activities, that are tailored to your child's age and interests. Through Clapz, your child can explore new subjects, enhance their knowledge, and develop their skills.
        \n\n In addition to learning, Clapz also provides a platform for children to showcase their creativity and innovation. Your child can upload their own content, such as artwork or videos, to share with other children and receive feedback. We believe that this feature encourages children to think outside the box and inspires them to pursue their passions. \n\n 
         If you have any questions or concerns about Clapz, please do not hesitate to contact us at 'support@clapz.in' . Our team is always ready to assist you and ensure a smooth experience for your child. Thank you for your cooperation and support. """
        footer = "\n Best regards, \n  Clapz Admin Team"        
        email_body =  header + " \n "  +"\n\n" + footer
        data = {
            "email_body": email_body,
            "to_email": instance.parent_email,
            "email_subject": "Clapz Registration",
        }
        sendparentemail(data)
        
        return instance


class MentorProfileSerializer(ProfileSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "user_type",
            "first_name",
            "name",
            "email",
            "username",
            "is_private",
            "date_joined",
            "dob",
            "mobile",
            "profile_image",
            "bio",
            "state",
            "city",
            "pin_code",
            "address",
            "workspace",
            "position",
            "qualification",
        )
        read_only_fields = (
            "user_type",
            "mobile",
        )


class InstituteProfileSerializer(ProfileSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "user_type",
            "first_name",
            "is_private",
            "username",
            "contact_number",
            "profile_image",
            "bio",
            "date_joined",
            "poc_name",
            "poc_mobile",
            "poc_email",
            "name",
            "email",
            "mobile",
            "state",
            "city",
            "address",
            "pin_code",
        )
        read_only_fields = (
            "user_type",
            "mobile",
        )




class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    mobile = serializers.CharField(max_length=16)
    user_type = serializers.ChoiceField(choices=UserType.choices())
    otp = serializers.IntegerField(write_only=True)
    password = serializers.CharField(max_length=100, write_only=True)
    
    # password = serializers.CharField(max_length=100, write_only=True)
    # confirm_password = serializers.CharField(max_length=100, write_only=True,)

    def is_valid_otp(self, otp, mobile):
        if mobile and otp:
            return PhoneModel.objects.filter(mobile=mobile, otp=otp).exists()
        return False

    

    def validate(self, attrs):
        mobile = attrs.get("mobile")
        otp = attrs.pop("otp")
        user = User.objects.filter(mobile=mobile).exists()
        if user:
            raise ValidationError("User already exists.")
        if not self.is_valid_otp(otp, mobile):
            raise ValidationError("Please enter vaild mobile number and otp ")
        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        PhoneModel.objects.filter(mobile=user.mobile).delete()
        return user











# class RegisterSerializer(serializers.Serializer):
    # first_name = serializers.CharField(max_length=100)
    # name = serializers.CharField(max_length=100)
    # mobile = serializers.CharField(max_length=16)
    # user_type = serializers.ChoiceField(choices=UserType.choices())
    # otp = serializers.IntegerField(write_only=True)
    # password = serializers.CharField(max_length=100, write_only=True)

#     def is_valid_otp(self, otp, mobile):
#         totp = pyotp.TOTP(settings.OTP_SECRET, interval=300, digits=4)
#         if totp.verify(otp):
#             return PhoneModel.objects.filter(mobile=mobile, otp=otp).exists()
#         return False

#     def validate(self, attrs):
#         mobile = attrs.get("mobile")
#         otp = attrs.pop("otp")
#         user = User.objects.filter(mobile=mobile).exists()
#         if user:
#             raise ValidationError("User already exists.")
#         if not self.is_valid_otp(otp, mobile):
#             raise ValidationError("Invalid OTP")
#         return super().validate(attrs)

#     def create(self, validated_data):
#         validated_data["moile_verified"] = True
#         user = User.objects.create_user(**validated_data)
#         PhoneModel.objects.filter(mobile=user.mobile).delete()
#         return user


class ParentPhoneSerializer(serializers.Serializer):
    parent_mobile = serializers.CharField(max_length=100)
    otp = serializers.IntegerField(write_only=True)

    def is_valid_otp(self, otp, parent_mobile):
        totp = pyotp.TOTP(OTP_SECRET, interval=300, digits=4)
        # if totp.verify(otp):
        return PhoneModel.objects.filter(mobile=parent_mobile, otp=otp).exists()
        # return False

    def validate(self, attrs):
        parent_mobile = attrs.get("parent_mobile")
        otp = attrs.pop("otp")
        if not self.is_valid_otp(otp, parent_mobile):
            raise ValidationError("Invalid OTP")

        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        PhoneModel.objects.filter(mobile=user.mobile).delete()
        return user


class PrentEmailSerializer(serializers.Serializer):
    parent_email = serializers.EmailField()


#     otp=serializers.IntegerField(write_only=True)

#     def is_valid_otp(self,otp,parent_email):
#         totp=pyotp.TOTP(settings.OTP_SECRET,interval=300,digits=4)
#         if totp.verify(otp):
#             return EmailModel.objects.filter(email=parent_email,otp=otp).exists()
#         return False

#     def validate(self,attrs):
#         parent_email=attrs.get('parent_email')
#         otp=attrs.get('otp')
#         data=User.objects.filter(parent_email=parent_email)
#         if not data:
#             raise ValidationError('Invalid Parent_Email')
#         if not self.is_valid_otp(otp,parent_email):
#             raise ValidationError('Invalid OTP')
#         return super().validate(attrs)

#     def create(self,validated_data):
#         user=User.objects.create_user(**validated_data)
#         EmailModel.objects.filter(email=user.parent_email).delete()
#         return user


class AuthTokenSerializer(serializers.Serializer):
    email_phone = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )
    custom_error = {"authentication_error": "Enter Password Correctly"}

    def validate(self, attrs):
        email_phone = attrs.get("email_phone")
        password = attrs.get("password")
        if email_phone and password:
            user = User.objects.get((Q(email=email_phone) | Q(mobile=email_phone)))
            if not user:
                raise exceptions.AuthenticationFailed(
                    detail=self.custom_error["authentication_error"]
                )
            user = authenticate(
                request=self.context.get("request"),
                username=email_phone,
                password=password,
            )
            if not user:
                raise exceptions.AuthenticationFailed(
                    detail=self.custom_error["authentication_error"]
                )

        else:
            raise exceptions.NotAuthenticated()
        attrs["user"] = user
        return attrs


class UserSerializer(CustomUserSerializer):
    can_post = serializers.BooleanField(source="can_post", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "first_name",
            "name",
            "phone",
            "email",
            "user_type",
            "can_post",
        )


class CreatedBySerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()

    def get_is_following(self, data_obj):
        # return FollowRequest.is_friends(created_by=data_obj)
        user = self.context["request"].user
        data = FollowRequest.objects.filter(
            receiver=data_obj, status="accepted", created_by=user
        ).exists()
        if data:
            return True
        return False

    class Meta:
        model = User
        fields = [
            "id",
            "profile_image",
            "username",
            "name",
            "first_name",
            "user_type",
            "email",
            "mobile",
            "date_joined",
            "is_following",
            "bio",
        ]


class UpdatedBySerialzier(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()

    def get_is_following(self, data_obj):
        # return FollowRequest.is_friends(created_by=data_obj)
        user = self.context["request"].user
        data = FollowRequest.objects.filter(
            receiver=data_obj, status="accepted", created_by=user
        ).exists()
        if data:
            return True
        return False

    class Meta:
        model = User
        fields = (
            "id",
            "profile_image",
            "username",
            "name",
            "first_name",
            "user_type",
            "email",
            "mobile",
            "date_joined",
            "is_following",
        )


class ResponseBlockSerializer(serializers.ModelSerializer):
    created_by = CreatedBySerializer()
    updated_by = CreatedBySerializer()

    class Meta:
        model = Block
        fields = (
            "id",
            "blocked_user",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )


class BlockSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        blocked_user = attrs.get("blocked_user")
        data = Block.objects.filter(blocked_user=blocked_user).exists()
        if data:
            raise ValidationError("block user alread exist")
        return super().validate(attrs)

    class Meta:
        model = Block
        fields = (
            "blocked_user",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )


class UnBlockSerializer(serializers.ModelSerializer):
    created_by = CreatedBySerializer()
    updated_by = CreatedBySerializer()

    class Meta:
        model = Block
        fields = (
            "id",
            "blocked_user",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )


class UnBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = (
            "id",
            "blocked_user",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )


class StudentSerializer(serializers.ModelSerializer):
    model = User
    fields = (
        "id",
        "user_type",
        "first_name",
        "username",
        "is_private",
        "dob",
        "name",
        "email",
        "mobile",
        "school",
        "state",
        "city",
        "address",
        "pin_code",
        "grade",
        "parent_mobile",
        "parent_email",
    )


class FollowRequestViewSerializer(serializers.ModelSerializer):
    receiver = AllProfileSerializer(read_only=True)
    created_by = CreatedBySerializer(read_only=True)

    class Meta:
        model = FollowRequest
        fields = (
            "id",
            "created_by",
            "receiver",
            "status",
        )
        read_only_fields = (
            "created_by",
            "receiver",
            "status",
        )


class FollowerSerializer(serializers.ModelSerializer):
    user = AllProfileSerializer(source="created_by")

    class Meta:
        model = FollowRequest
        fields = (
            "id",
            "user",
        )


class FollowingSerializer(serializers.ModelSerializer):
    user = AllProfileSerializer(source="receiver")

    class Meta:
        model = FollowRequest
        fields = (
            "id",
            "user",
        )


class FollowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowRequest
        fields = ("id", "created_by", "receiver", "status")
        read_only_fields = ("created_by", "status")

    def validate(self, attrs):
        created_by = self.context["request"].user
        receiver = attrs.get("receiver")
        if created_by == receiver:
            raise ValidationError("cannot follow self")
        # follow_exists = FollowRequest.is_friends(receiver, created_by)
        follow_exists = FollowRequest.objects.filter(
            created_by=created_by, receiver=receiver
        )
        if follow_exists:
            raise ValidationError("user already follow")
        return super().validate(attrs)

    def create(self, validated_data):
        is_private_user = validated_data["receiver"].is_private
        validated_data["status"] = "pending" if is_private_user else "accepted"
        data = FollowRequest.objects.create(**validated_data)
        return data


class ReceivedFollowSerializer(FollowRequestSerializer):
    created_by = CreatedBySerializer()
    receiver = CreatedBySerializer()

    class Meta:
        model = FollowRequest
        fields = ("id", "created_by", "receiver", "status")


class ResponseAcceptFollowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowRequest
        fields = (
            "receiver",
            "created_by",
            "status",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "created_by",
            "status",
            "updated_by",
            "created_at",
            "updated_at",
        )


class AcceptFollowRequestSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        created_by = self.context["request"].user
        receiver = attrs.get("receiver")
        if created_by == receiver:
            raise ValidationError("cannot follow self")
        return super().validate(attrs)

    class Meta:
        model = FollowRequest
        fields = (
            "receiver",
            "created_by",
            "status",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "status",
        )

    def create(self, validated_data):
        # data=FollowRequest.objects.filter(created_by=self.context['request'].user,receiver=validated_data['receiver']).update(status='accepted')
        follow = FollowRequest.objects.create(**validated_data)
        return follow


class RejectFollowRequestSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        created_by = self.context["request"].user
        receiver = attrs.get("receiver")
        if created_by == receiver:
            raise ValidationError("cannot  follow self")
        return super().validate(attrs)

    class Meta:
        model = FollowRequest
        fields = (
            "receiver",
            "created_by",
            "status",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        # data=FollowRequest.objects.filter(created_by=self.context['request'].user,receiver=validated_data['receiver']).update(status='rejected')
        RA = FollowRequest.objects.create(**validated_data)
        return RA


class ResponseUnFollowRequestSerializer(serializers.ModelSerializer):
    receiver = CreatedBySerializer()

    class Meta:
        model = FollowRequest
        fields = ("id", "receiver", "created_by", "status")
        read_only_fields = ("created_by", "status")


class UnFollowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowRequest
        fields = ("id", "receiver", "created_by", "status")
        read_only_fields = ("created_by", "status")


class PhoneModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneModel
        fields = ("mobile",)

    def validate_mobile(self, value):
        if not value.isnumeric():
            raise serializers.ValidationError(" Mobile Must be Number")

        elif len(value) < 7:
            raise serializers.ValidationError(
                "Ensure this field has more than 7 characters."
            )
        return value
    
    
    # class Meta:
    #     model = PhoneModel
    #     fields = ["mobile"]

    # def create(self, validated_data):
    #     totp = pyotp.TOTP(settings.OTP_SECRET, interval=300, digits=4)
    #     otp = totp.now()
    #     phoen_num = validated_data["mobile"]
    #     apikey = settings.THIRD_PARTY_CONFIG["smsalert"]["SECRET_KEY"]
    #     sender = settings.THIRD_PARTY_CONFIG["smsalert"]["sender"]        
    #     msg = "Your OTP for registration to the Clapz Platform is {}. The OTP is valid for 5 minute. Please do not share this OTP with anyone for security reasons. Best Regards, Clapz Team".format(otp)
    #     url = "https://www.smsalert.co.in/api/push.json?apikey={}&sender={}&mobileno={}&text={}".format(apikey,sender,phoen_num,msg)
    #     payload = {}
    #     headers= {}
    #     response = requests.request("POST", url, headers=headers, data = payload)
    #     print(response.text.encode('utf8'))

    #     instance, _ = self.Meta.model.objects.get_or_create(**validated_data)
    #     instance.otp = otp
    #     instance.save()
    #     return instance


# class EmailModelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=EmailModel
#         fields=['email']

#     def create(self,validated_data):
#         totp=pyotp.TOTP(settings.OTP_SECRET,interval=300,digits=4)
#         otp=totp.now()
#         instance, _ =self.Meta.model.objects.get_or_create(**validated_data)
#         instance.otp=otp
#         instance.save()
#         return instance


class CheckNumberSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=16)

    def validate_mobile(self, attrs):
        data = User.objects.filter(mobile=attrs).exists()
        if data:
            raise serializers.ValidationError(
                "Mobile already exist", code=status.HTTP_400_BAD_REQUEST
            )
        return attrs


class ProfileImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("profile_image",)


class UserTextUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("bio",)


class UserDeleterAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id",)


class ParentEmailVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)


class ForgotPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField()
    mobile = serializers.CharField()
    password = serializers.CharField()


    def is_valid_otp(self, otp, mobile):
        result = PhoneModel.objects.filter(mobile=mobile, otp=otp).exists()
        return result

class RejectSerializer(serializers.Serializer):
    created_by = serializers.IntegerField()


class AcceptedSerializer(serializers.Serializer):
    created_by = serializers.IntegerField()
