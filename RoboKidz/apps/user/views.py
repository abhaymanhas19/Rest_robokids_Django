from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from typing import List
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
import smtplib
from email.mime.multipart import MIMEMultipart
import random, string
from email.mime.text import MIMEText
import requests
from .utils import *
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render,HttpResponse

from django.http import HttpResponse, HttpResponseNotFound
from django.template import Context, loader

from . helpers import *
class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = ()


# class ProfileAPIView(generics.GenericAPIView):
#     serializer_class = Profile
#     # queryset = User.objects.all()
#     # http_method_names: List[str] = ["get", "head", "option"]
#     def get(self,request,*args,**kwargs):
#         user =Block.objects.filter(created_by=request.data['created']).values(blockedId=F('blocked_user'),name=F('blocked_user__name'),email=F('blocked_user__email'),user_type=F('blocked_user__user_type'))
#         return Response({'data':user})


class ProfileAPIView(generics.ListAPIView):
    serializer_class = AllProfileSerializer

    def get_blocked_user_ids(self, data):
        ids = []
        for i in data:
            ids.append(i["created_by"])
            ids.append(i["blocked_user"])
       
        return set(ids)


    def get_queryset(self):
        blocked_users = Block.objects.filter(
            Q(created_by=self.request.user) | Q(blocked_user=self.request.user)
        ).values("created_by", "blocked_user")
        
        user_ids = self.get_blocked_user_ids(blocked_users)
        users = User.objects.exclude(id__in=user_ids).exclude(id=self.request.user.id)

        return users


# class MyProfileAPIView(generics.ListAPIView):
#     serializer_class = AllProfileSerializer

#     # def get_queryset(self):
#     #     queryset = super().get_queryset()
#     #     return queryset.filter(id=self.request.user.id)

#     def get_queryset(self, request, *args, **kwargs):
#         queryset = User.objects.get(id=self.request.user)
#         data = AllProfileSerializer(instance=queryset, context={"request": request}).data
#         return Response(data)


class MyProfileAPIView(generics.GenericAPIView):
    serializer_class = MyProfileSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user, context={"request": request})
        return Response({"data": serializer.data})


class ProfileByIdAPIView(generics.RetrieveAPIView):
    serializer_class = AllProfileSerializer

    def get(self, request, user_id):
        instance = get_object_or_404(User, pk=user_id)
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data)


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = ()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        refresh = LoginSerializer.get_token(serializer.instance)
        data = {**serializer.data}
        data["id"] = serializer.instance.id
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def get_tokens_for_use(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }



class VerifyTokenAPIView(APIView):
    def get(self, request, *args, **kwargs):
        data = True
        return Response({"data": data}, status=status.HTTP_200_OK)


class ParentPhoneAPIView(generics.CreateAPIView):
    serializer_class = ParentPhoneSerializer
    http_method_names: List[str] = ["post"]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.parent_mobile_verified = True
        user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "verified parent_mobile number"},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )




class BlockAPI(viewsets.ModelViewSet):
    serializer_class = BlockSerializer
    http_method_names: List[str] = ["post", "get", "option"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = ResponseBlockSerializer(
            instance=serializer.instance, context={"request": request}
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ResponseBlockSerializer(
                page, context={"request": request}, many=True
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return Block.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class UnBlockAPIView(viewsets.ModelViewSet):
    serializer_class = UnBlockSerializer
    queryset = Block.objects.all()
    http_method_names: List[str] = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unblocked, message = self.unblock(serializer)
        headers = self.get_success_headers(serializer.data)
        # data=UnBlockSerializer(instance=serializer.instance,context={'request':request}).data
        return Response(
            {"message": message, "status": unblocked},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def unblock(self, serializer):
        block = Block.objects.filter(
            blocked_user=serializer.data["blocked_user"]
        ).first()
        if block:
            block.delete()
            return True, "UnBlock"
        return False, "Not Found"


class FollowRequestAPI(viewsets.ModelViewSet):
    serializer_class = FollowRequestSerializer
    queryset = FollowRequest.objects.all()
    http_method_names: List[str] = ["post", "options"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = FollowRequestViewSerializer(
            instance=serializer.instance, context={"request": request}
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class UnFollowRequestAPI(viewsets.ModelViewSet):
    serializer_class = UnFollowRequestSerializer
    http_method_names: List[str] = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unfollowed, message = self.unfollow(serializer)
        headers = self.get_success_headers(serializer.data)
        data = ResponseUnFollowRequestSerializer(
            instance=serializer.instance, context={"request": request}
        ).data
        return Response(
            {"message": message, "status": unfollowed},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def unfollow(self, serializer):
        follow = FollowRequest.objects.filter(
            receiver_id=serializer.data["receiver"],
            created_by=self.request.user,
            status="accepted",
        ).first()
        if follow:
            follow.delete()
            return True, "Unfollowed"
        return False, "Not Found"


class FollowersViewAPI(generics.ListAPIView):
    serializer_class = FollowerSerializer

    def get_queryset(self):
        return FollowRequest.objects.filter(
            receiver=self.request.user, status="accepted"
        )


class FollowingViewAPI(generics.ListAPIView):
    serializer_class = FollowingSerializer
    def get_queryset(self):
        return FollowRequest.objects.filter(
            created_by=self.request.user,
        )


class ReceivedRequestViewAPI(generics.ListAPIView):
    serializer_class = ReceivedFollowSerializer

    def get_queryset(self):
        return FollowRequest.objects.filter(
            receiver=self.request.user, status="pending"
        )


class SchoolAPI(generics.ListAPIView):
    serializer_class = SchoolSerializer

    def get_queryset(self):
        return School.objects.filter(is_active=True)


class GradeAPI(generics.ListAPIView):
    serializer_class = GradeSerializer
    queryset = Grade.objects.all()


class StudentProfileAPIView(viewsets.ModelViewSet):
    serializer_class = StudentProfileSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    # parser_classes = (FormParser, MultiPartParser)
    http_method_names: List[str] = ("get", "patch","delete")

    def get_queryset(self):
        return User.objects.filter(user_type="STUDENT")


class MentorProfileAPIView(viewsets.ModelViewSet):
    serializer_class = MentorProfileSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    http_method_names: List[str] = ("get", "patch",'delete')

    def get_queryset(self):
        return User.objects.filter(user_type="MENTOR")


class InstituteProfileAPIView(viewsets.ModelViewSet):
    serializer_class = InstituteProfileSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    http_method_names: List[str] = ("get", "patch","delete")

    def get_queryset(self):
        return User.objects.filter(user_type="INSTITUTE")


class GenerateOtpAPIView(generics.CreateAPIView):
    serializer_class = PhoneModelSerializer
    permission_classes = ()
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            mo = serializer.validated_data["mobile"]
            if PhoneModel.objects.filter(mobile=mo).exists():
                instance = PhoneModel.objects.get(mobile=mo)
                instance.otp = random.randint(1000, 9999)
                instance.save()
                content = {"mobile": instance.mobile, "otp": instance.otp}
                mobile = instance.mobile
                otp = instance.otp
                message = f"Your OTP for registration to the Clapz Platform is {otp}. The OTP is valid for 5 minute.Please do not share this OTP with anyone for security reasons. Best Regards, Clapz Team"
                send=SendOTP(message, mobile)
                print("t",send)
                if not send:
                    return Response( status=status.HTTP_400_BAD_REQUEST)
                return Response(content, status=status.HTTP_201_CREATED)
            else:   
                userotp = random.randint(1000, 9999)
                obj = PhoneModel.objects.create(mobile=mo, otp=userotp)
                mobile = obj.mobile
                otp = obj.otp
                message = f"Your OTP for registration to the Clapz Platform is {otp}. The OTP is valid for 5 minute.Please do not share this OTP with anyone for security reasons. Best Regards, Clapz Team"
                #
                send = SendOTP(message, mobile)
                print("",send)
                if not send:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                    return Response( {"message": "Invalid Request"})

                content = {"mobile": mobile, "otp": otp}
                return Response(content, status=status.HTTP_201_CREATED)
        return Response(
            {"message", "invalid number"}, status=status.HTTP_400_BAD_REQUEST
        )


    


        


# class OtpAPIView(generics.CreateAPIView):
#     serializer_class=EmailModelSerializer
#     def post(self,request):
#         serializer=self.serializer_class(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             instance=serializer.save()
#             content={'mobile':instance.email,'otp':instance.otp}
#             return Response(content,status=status.HTTP_201_CREATED)
#         return Response({'message','invalid emial'},status=status.HTTP_400_BAD_REQUEST)


class CheckNumberAPIView(generics.GenericAPIView):
    serializer_class = CheckNumberSerializer
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"message": "mobile number is available"}, status=status.HTTP_200_OK
            )
        return Response(
            {"message": serializer.error}, status=status.HTTP_400_BAD_REQUEST
        )


class AttendrequestAPIView(generics.GenericAPIView):
    serializer_class=AcceptedSerializer
    permission_classes=(IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        
        data=FollowRequest.objects.filter(created_by=request.data['created_by'],receiver=request.user).update(status='accepted')
        if data:
            return Response({"msg": 'follow request accepted', "status": 200})
        if not data:
            return Response({"msg": "User don't exist", "status": 200})


    

    


class RejectRequestAPIView(APIView):
    serializer_class=AcceptedSerializer
    permission_classes=(IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        data=FollowRequest.objects.filter(created_by=request.data['created_by'],receiver=request.user).update(status="rejected")
        if data:
            return Response({'msg':'Reject request','status':200})
        if not data:
            return Response({'msg':"user  don't exist",'status':400})
 
class ProfileImageUpdateAPIView(viewsets.ModelViewSet):
    serializer_class = ProfileImageUpdateSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    # parser_classes = (FormParser, MultiPartParser)
    http_method_names: List[str] = ("get", "patch")

    def get_queryset(self):
        return User.objects.filter()


class UserBioUpdateAPIView(viewsets.ModelViewSet):
    serializer_class = UserTextUpdateSerializer
    queryset = User.objects.all()
    http_method_names: List[str] = ["patch"]







class AccountDelete(viewsets.ModelViewSet):
    serializer_class = UserDeleterAccountSerializer
    queryset = User.objects.all()
    http_method_names: List[str] = ["delete"]



class ForgotPasswordAPIView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        data = serializer.is_valid()
        otp = serializer.validated_data["otp"]     
        mobile = serializer.validated_data["mobile"]
        val = serializer.is_valid_otp(otp,mobile)
       
        if val == True:

            u = PhoneModel.objects.filter(otp=otp)           
            u = User.objects.get(mobile=mobile)
            pwd = str(request.data["password"])
            u.set_password(pwd)
            u.save()
            return Response({"msg": "Your password is updated successfully", "status": 200})
        else:
            return Response({"msg": "OTP Invalid ", "status": 400})



# class SendemailAPIView(generics.GenericAPIView):
#     serializer_class = ParentEmailVerifySerializer

#     def post(self, request, *args, **kwargs):
#         try:
#             user = request.data
#             serializer = self.serializer_class(data=user)
#             serializer.is_valid(raise_exception=True)
#             user_data = serializer.data
#             user = User.objects.get(email=user_data["email"])
#             token = RefreshToken.for_user(user).access_token
#             current_site = get_current_site(request).domain
#             relative_Link = reverse("email-verify")
#             # relative_Link=reverse("home")
#             absurl = "http://" + current_site + relative_Link + "?token=" + str(token)
#             email_body = "Hi" + "use link below to  verify email \n" + absurl
#             data = {
#                 "email_body": email_body,
#                 "to_email": user.parent_email,
#                 "email_subject": "verify your email",
#             }
#             Util.send_mail(user_data)
#             return Response(user_data,status=status.HTTP_201_CREATED)
#         except:
#             return Response({"message": "NotFound"}, status=status.HTTP_400_BAD_REQUEST)


class SendemailAPIView(generics.GenericAPIView):
    serializer_class = ParentEmailVerifySerializer
    def get(self, request, *args, **kwargs):
        user_name = request.user
        token = RefreshToken.for_user(request.user).access_token
        current_site = get_current_site(request).domain
        relative_Link = reverse("email-verify")
        absurl = "http://" + current_site + relative_Link + "?token=" + str(token)
        header = f"Dear Parent/Guardian,\n\n I am writing to inform you that your child, {user_name}, has expressed interest in registering with our education portal, Clapz. We are thrilled to have them as a potential student and would like to extend a warm welcome to them.\n\n As part of our registration process, we require all parents/guardians to verify their email address. This is a mandatory step in order to proceed with the registration process. To complete this verification process, please click on the link provided below and follow the instructions on the screen.\n \n"
        header2= "We take the privacy and security of our students very seriously and assure you that all personal information shared with us will be kept confidential and used solely for the purpose of providing educational services to your child. Thank you for considering Clapz as an education portal for your child. We look forward to hearing from you soon."
        footer = "\n Best regards, \n  Clapz Support Team"        
        email_body =  header + " \n " + absurl +"\n\n" + header2+ "\n \n" + footer
        data = {
            "email_body": email_body,
            "to_email": request.user.parent_email,
            "email_subject": "Clapz Email Verification",
        }
        sendparentemail(data)
        return Response(data,status=status.HTTP_201_CREATED)
        





        
from rest_framework.decorators import api_view, authentication_classes, permission_classes
@authentication_classes([])
@permission_classes([])
class VerifyEmail(generics.GenericAPIView):
    
    permission_classes = []
    serializer_class = PrentEmailSerializer

    def get(self, request):
        token = request.GET.get("token")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])        
        user = User.objects.get(id=payload['user_id'])

        if not user.parent_email_verified:
            user.parent_email_verified = True
            
            user.save() 

            return  HttpResponse('<img style="margin-left: 40%; " src="/media/logoclapz.png" alt="Trulli" width="300" height="200">' '<h1 style="color:MediumSeaGreen; text-align: center;">Email verified successfully</h1>'  )
            
        else:
            # return render(request,'email.html')
            return  HttpResponse(  '<img style="margin-left: 40%; " src="/media/logoclapz.png" alt="Trulli" width="300" height="200">' '<h1 style="color:MediumSeaGreen; text-align: center;">Email verified successfully</h1>' '<h2 style="text-align: center;"><a  href="https://play.google.com/store/apps/details?id=com.robokidz">Download Clapz App </a> </h2>'    )
        












# class VerifyEmail(generics.GenericAPIView):
#     def get(self, request):
#         token = request.GET.get("token")
#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY)
#             user = User.objects.get(id=payload["user_id"])
#             if not user.parent_email_verified:
#                 user.parent_email_verified = True
#                 user.save()
#             return Response({"email": "succefull activated"}, status=status.HTTP_200_OK)
#         except jwt.ExpiredSignatureError as identifier:
#             return Response(
#                 {"error": "activation exiperd"}, status=status.HTTP_400_BAD_REQUEST
#             )
#         except jwt.exceptions.DecodeError as identifier:
#             return Response(
#                 {"error": "invalid token"}, status=status.HTTP_400_BAD_REQUEST
#             )



def home(request):
    return render(request,'index.html')


class ChangePasswordAPI(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    def post(self, request, *args, **kwargs):
        passwordd=request.data['old_password']
        u=request.user
        if u is not None and u.check_password(passwordd):
            u.set_password(request.data['new_password'])
            u.save()
            return Response({"msg":'Password Updated.',"status":200})  
        else:
            return Response({"status":400,"msg":'Incorrect old password.'})







