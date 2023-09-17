from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Post)
class PostsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image",
        "video",
        "caption",
        "created_by",
        "caption",
        "description",
        "is_abused",
        "rating",
        "latitude",
        "longtitude",
    )
    list_filter = ("hashtags__hashtag", "created_by", "caption")
    search_fields = ("hashtags__hashtag",)


# @admin.register(PendingPost)
# class PendingPostAdmin(admin.ModelAdmin):
#     readonly_fields = ( "id","caption","created_by",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "post",
        "parent_comment",
        "body",
        "is_abused",
        "body",
        "created_by",
    )
    list_filter = ("id", "body")
    search_fields = ("created_by__name",)


class PostItemInline(admin.TabularInline):
    model = PostItem
    fields = ("data",)


class PostdatasAdmin(admin.ModelAdmin):
    inlines = [
        PostItemInline,
    ]


@admin.register(PendingPost)
class PendingPostsadmin(admin.ModelAdmin):
    list_display = ("id", "caption", "created_by", "is_approved")
    list_editable = ("is_approved",)

    inlines = [
        PostItemInline,
    ]
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_approved=False)


@admin.register(PostItem)
class PostItemadmin(admin.ModelAdmin):
    list_display = ("id", "post_id", "created_by")

    def post_id(self, obj):
        return obj.post.id

    post_id.admin_order_field = "post__id"


# admin.site.register(Like)
# admin.site.register(PostHashTags)
# admin.site.register(LikeComment)
# admin.site.register(ReportAbuse)
# admin.site.register(Certificate)
# admin.site.register(GradeNumber)
# admin.site.register(PostCertificate)
# admin.site.register(Event)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "post",
        "created_by",
    ]
    list_filter = ["post"]

    search_fields = ["post", "created_by"]


@admin.register(PostHashTags)
class PostHashTagsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "hashtag",
    ]
    list_filter = ["hashtag"]

    search_fields = ["hashtag"]


@admin.register(LikeComment)
class LikeCommentAdmin(admin.ModelAdmin):
    list_display = ["comment", "created_by"]
    list_filter = ["comment"]

    search_fields = ["comment"]


@admin.register(ReportAbuse)
class ReportAbuseAdmin(admin.ModelAdmin):
    list_display = [
        "post",
        "comment",
        "user",
        "reason",
    ]
    list_filter = ["post"]

    search_fields = ["user", "post"]


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "certificate",
        "signature",
        "c_type",
        "name",
        "minimnum",
        "maximum",
    ]
    list_filter = ["certificate"]

    search_fields = ["name", "certificate"]


@admin.register(GradeNumber)
class GradeNumberAdmin(admin.ModelAdmin):
    list_display = ["g_type", "name", "minimum", "maximum"]
    list_filter = ["name"]

    search_fields = ["name", "g_type"]


@admin.register(PostCertificate)
class PostCertificateAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "post",
        "user",
        #'follow',
        "certificate",
        "certificate_image",
        "created_by",
        "updated_by",
    ]

    list_filter = ["post", "user"]

    search_fields = ["post", "certificate", "user"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "image",
        "description",
        "location",
        "date",
        "time",
    ]
    list_filter = [
        "name",
    ]

    search_fields = ["date", "name", "location"]
