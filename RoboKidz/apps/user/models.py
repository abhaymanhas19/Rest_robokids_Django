from pyexpat import model
from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.dispatch import receiver
from django.db.models import Q


# from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.utils.enums import GenderType, UserType
from apps.utils.models import TimeStampModel
import django
from datetime import date

# from apps.post.models import *


class UserAccountManager(BaseUserManager):
    def _create_user(self, mobile, password=None, **extra_fields):
        user = self.model(mobile=mobile, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_user(self, mobile, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(mobile, **extra_fields)

    def create_admin(self, mobile, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(mobile, password, **extra_fields)

    def create_superuser(self, mobile, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(mobile, password, **extra_fields)


class School(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Grade(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    gender = models.CharField(max_length=100, choices=GenderType.choices(), blank=True)
    user_type = models.CharField(max_length=100, choices=UserType.choices())
    username = models.CharField(_("Username"), max_length=200)
    dob = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=12, blank=True, null=True)
    poc_name = models.CharField(max_length=100, blank=True, null=True)
    poc_mobile = models.CharField(max_length=16, blank=True, null=True)
    poc_email = models.EmailField(blank=True)
    first_name = models.CharField(_("First name"), max_length=30, blank=True)
    name = models.CharField(_("Name"), max_length=30, blank=True)
    email = models.EmailField(_("Email address"))
    mobile = models.CharField(_("Mobile"), max_length=20, unique=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, blank=True, null=True)
    state = models.CharField(_("State"), max_length=100, blank=True, null=True)
    city = models.CharField(_("City"), max_length=100, blank=True, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, blank=True, null=True)
    parent_mobile = models.CharField(
        _("Parent Mobile"), max_length=15, blank=True, null=True
    )
    parent_email = models.EmailField(_("Parent E-Mail"), blank=True, null=True)
    address = models.CharField(_("Address"), max_length=200, blank=True, null=True)
    pin_code = models.IntegerField(_("Pin Code"), blank=True, null=True)
    workspace = models.CharField(_("Work Space"), max_length=200, blank=True, null=True)
    position = models.CharField(_("Position"), max_length=200, blank=True, null=True)
    qualification = models.CharField(
        _("Qualification"), max_length=100, blank=True, null=True
    )
    parent_mobile_verified = models.BooleanField(default=False)
    moile_verified = models.BooleanField(default=False)
    parent_email_verified = models.BooleanField(default=False)
    bio = models.TextField(_("Bio"), blank=True)
    profile_image = models.ImageField(
        _("ProfileImage"), upload_to="media", blank=True, null=True
    )
    is_staff = models.BooleanField(
        _("Company Admin"),
        default=False,
        help_text=_("Designates whether the user is a company admin or not."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_("Designates whether this user should be treated as active."),
    )
    abuse = models.BooleanField(_("ReportAbuse"), default=False)
    date_joined = models.DateTimeField(
        _("Date joined"), default=django.utils.timezone.now
    )
    is_private = models.BooleanField(_("Is Private"), default=False)
    objects = UserAccountManager()
    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = [
        "first_name",
    ]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-pk"]

    @property
    def is_profile_completed(self):
        if self.user_type == "STUDENT" and (
            self.first_name
            and self.username
            and self.date_joined
            and self.dob
            and self.name
            and self.email
            and self.mobile
            and self.profile_image
            and self.school
            and self.state
            and self.address
            and self.city
            and self.grade
            and self.address
            and self.pin_code
            and self.parent_mobile
            and self.parent_email
        ) not in [None, ""]:
            return True
        if self.user_type == "MENTOR" and (
            self.first_name
            and self.name
            and self.email
            and self.username
            and self.dob
            and self.mobile
            and self.profile_image
            and self.state
            and self.city
            and self.pin_code
            and self.address
            and self.workspace
            and self.position
        ) not in [None, ""]:
            return True
        if self.user_type == "INSTITUTE" and (
            self.first_name
            and self.username
            and self.contact_number
            and self.profile_image
            and self.poc_name
            and self.poc_mobile
            and self.poc_email
            and self.name
            and self.email
            and self.mobile
            and self.state
            and self.city
            and self.pin_code
        ) not in [None, ""]:
            return True
        return False

    def __str__(self) -> str:
        return self.first_name


class Block(TimeStampModel):
    blocked_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blocked_users"
    )


class FollowRequest(TimeStampModel):
    Category_Choices = (
        ("pending", "pending"),
        ("accepted", "accepted"),
        ("rejected", "rejected"),
    )
    # sender = models.ForeignKey(
    #     User, on_delete=models.CASCADE, related_name="follow_sender"
    # )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follow_receiver"
    )
    status = models.CharField(_("Status"), max_length=200, choices=Category_Choices)

    @classmethod
    def is_friends(cls, target_user, requesting_user):
        return cls.objects.filter(
            Q(
                receiver=target_user,
                created_by=requesting_user,
                status__in=("accepted", "pending"),
            )
            | Q(
                receiver=requesting_user,
                created_by=target_user,
                status__in=("accepted", "pending"),
            )
        ).exists()

    # @classmethod
    # def is_friends(cls,created_by):
    #     return cls.objects.filter(created_by=created_by,status='accepted').exists()

    def __str__(self):
        return self.status

    # @classmethod
    # def followerscerficate(cls,created_by):
    #     data=cls.objects.filter(created_by=created_by,status='accepted')
    #     if 1 <= len(data) <= 9999:
    #         return 'silver'
    #     if 10000 <= len(data) <= 99999:
    #         return 'gold'
    #     if len(data)>100000:
    #         return 'diamond'
    #     return None

    # @classmethod
    # def followerscerficate(cls,created_by):
    #     data=cls.objects.filter(created_by=created_by,status='accepted').count()
    #     return data

    # @classmethod
    # def followergrade(cls,created_by):
    #     data=cls.objects.filter(created_by=created_by, status='accepted')
    #     if 1<= len(data) <=2:
    #         return 'New User'
    #     if 2 <= len(data) <=3:
    #         return 'Expericence'
    #     if len(data)>1000:
    #         return 'Proficient'
    #     return None
    # @classmethod
    # def followersgrade(cls,created_by):
    #     data=cls.objects.filter(created_by,status='accepted').count()
    #     grade=Certificate.objects.filter(maximum__lte=data, g_type='follow').all().values('name','minimnum','maximum')
    #     return grade


class PhoneModel(models.Model):
    mobile = models.CharField(max_length=16)
    otp = models.CharField(max_length=6)

    def __str__(self) -> str:
        return f"{self.mobile}"
