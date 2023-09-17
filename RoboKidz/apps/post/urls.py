from django.contrib import admin
from django.urls import path, include
from apps.post import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("posts", views.PostAPIView, basename="posts")
router.register("postitem", views.PostItemAPIView, basename="postitem")
router.register("like", views.LikeAPIView, basename="like")
router.register("likecomment", views.LikeCommentSerializer, basename="likecomment")
router.register("dislike", views.DisLikeAPIView, basename="DisLike")
router.register("comment", views.commentAPIView, basename="comment")
router.register("share", views.ShareAPIView, basename="share")
router.register("viewshare", views.ViewSharedPostsAPIView, basename="viewshare")
router.register("postreport", views.PostReportAbuseAPI, basename="commentreport")
router.register("comment-report-abuse", views.CommentReportAbuseAPI, basename="comment-report-abuse")
router.register("user-report-abuse", views.UserReportAbuseAPI, basename="user-report-abuse")
router.register('pendingpost',views.PendingPostAPIView,basename='pendingpost')
router.register('dislikecomment',views.DislikeComment,basename='dislike')
# router.register('Event',views.EventAPIView, basename='event')
router.register('createcirtificate',views.CrateCirtificates,basename='createcirtificate')
router.register('userscirtificates',views.GetUsergeneratedCirtifiates,basename='userscirtificates')

urlpatterns = [
    path("tag/", views.hashTag.as_view(), name="tagList"),
    path("search/", views.SearchAPIView.as_view(), name="search"),
    path("<post_id>/comments/", views.PostsCommentAPIView.as_view(), name="PostsComment"),
    path("my-posts/", views.MyPostAPIView.as_view(), name="MyPost"),
    path("shared-posts/", views.SharePostAPIView.as_view(), name="SharePost"),
    path("my-liked-posts/", views.MyLikedPostAPIView.as_view(), name="MyLiked"),
    path('data/',views.data,name='data'),
    path('data1/',views.data1,name='data1'),
    path('eventdata/',views.EventDataAPIView.as_view(),name='event'),
    path('<id>/eventdetail/',views.EventDetailAPIView.as_view(),name='eventdetail')

    
] + router.urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)

