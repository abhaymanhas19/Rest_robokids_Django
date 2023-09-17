from django.contrib import admin
from django.urls import path, include
from apps.user import views
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenVerifyView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register("block", views.BlockAPI, basename="block")
router.register("unblock", views.UnBlockAPIView, basename="unblock")
router.register("follow", views.FollowRequestAPI, basename="follow")
router.register("unfollow", views.UnFollowRequestAPI, basename="unfollow")
router.register("student", views.StudentProfileAPIView, basename="student")
router.register("mentor", views.MentorProfileAPIView, basename="mentor")
router.register("institute", views.InstituteProfileAPIView, basename="institute")
router.register('imageupdate',views.ProfileImageUpdateAPIView,basename='profileimage')
router.register('userbioupdate',views.UserBioUpdateAPIView,basename='userbio')
router.register('deleteuseraccount',views.AccountDelete,basename='delete')

    

urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path("refresh-token/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.RegisterAPIView.as_view(), name="register"),
    path("school/", views.SchoolAPI.as_view(), name="school"),
    path("grade/", views.GradeAPI.as_view(), name="grade"),
    path("generate-otp/", views.GenerateOtpAPIView.as_view(), name="generateotp"),
    path("check-number-availability/",views.CheckNumberAPIView.as_view(),name="CheckNumber"),
    path("profile/", views.ProfileAPIView.as_view(), name="profile"),
    path("followers/", views.FollowersViewAPI.as_view(), name="Follower"),
    path("following/", views.FollowingViewAPI.as_view(), name="Following"),
    path("received-request/", views.ReceivedRequestViewAPI.as_view(), name="Received"),
    path("my-profile/", views.MyProfileAPIView.as_view(), name="my-Profile"),
    path("profile-by-id/<user_id>",  views.ProfileByIdAPIView.as_view(),name="profile-by-id"),
    path("accept/", views.AttendrequestAPIView.as_view(), name="attend"),
    path("rejectrequest/", views.RejectRequestAPIView.as_view(), name="rejectrequest"),
    path('forgot/',views.ForgotPasswordAPIView.as_view(),name='reset'),
    path('parentphone/',views.ParentPhoneAPIView.as_view(),name='ParentPhone'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('sendemail/',views.SendemailAPIView.as_view(),name='Sendemail'),
    path('email-verify/',views.VerifyEmail.as_view(),name='email-verify'),
    path('home/',views.home,name='home'),
    path('changepassword/',views.ChangePasswordAPI.as_view(),name='changepassowrd')

] + router.urls





