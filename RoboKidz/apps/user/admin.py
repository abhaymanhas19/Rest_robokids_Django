from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from apps.user.models import User
from apps.post.models import Certificate
User = get_user_model()


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("password",)}),
        (
            _("Personal info"),
            {"fields": ("first_name", "name", "email", "user_type", "mobile")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    add_form = UserCreationForm
    list_display = (
        "id",
        "mobile",
        "email",
        "first_name",
        "name",
        "is_staff",
        "is_private",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = (
        "first_name",
        "name",
        "email",
    )
    ordering = ("date_joined",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "is_active",
    )
    list_filter = ("is_active", "name")
    search_fields = ("name",)
    list_editable = ("is_active",)




#admin.site.register(User, CustomUserAdmin)
# admin.site.register(Block)
# admin.site.register(FollowRequest)
# admin.site.register(Grade)
# admin.site.register(PhoneModel)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id','mobile', 'first_name','name',
                            'user_type',
                            'is_private',
                            'dob',
                            'username',
                            'gender',
                            'contact_number',
                            'poc_name',
                            'poc_mobile',
                            'poc_email',
                            'email',
                            'school',
                            'state',
                            'city',
                            'grade',
                            'parent_mobile',
                            'parent_email',
                            'address',
                            'pin_code',
                            'workspace',
                            'position',
                            'qualification',
                            'moile_verified',
                            'parent_email_verified',
                            'parent_mobile_verified',
                            'bio',
                            'profile_image',
                            'is_staff',
                            'is_active',
                            'abuse',
                            'date_joined',]
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = (
        "first_name",
        "name",
        "email",
        "mobile",
    )
    ordering = ("date_joined",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
            







@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['id','blocked_user',]                 #blocked_user_name
    list_filter = ("blocked_user",)
    search_fields = ("name",)
   



@admin.register(FollowRequest)
class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ['id',"created_by","updated_by",'status','receiver']
    list_filter = ("receiver",)
    search_fields = ("receiver",'status')
    

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ("name",)
    search_fields = ("name",'name')
    


@admin.register(PhoneModel)
class PhoneModelAdmin(admin.ModelAdmin):
    list_display = ['mobile','otp']

    list_filter = ("mobile",)
    search_fields = ("mobile",)

    





