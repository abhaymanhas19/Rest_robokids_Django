from apps.user.serializers import CreatedBySerializer
from .models import *
from rest_framework import serializers
from apps.notification import models
from apps.user import models
from apps.user.serializers import *
from apps.post.serializers import *
from apps.post.models import *
from apps.user.models import *


class NotificationResponseSerializer(serializers.ModelSerializer):
    performed_by = CreatedBySerializer()

    class Meta:
        model = Notification
        fields = (
            "id",
            "performed_by",
            "notified_to",
            "message",
            "is_read",
            "performed_at",
            "message_key",
        )
        read_only_fields = (
            "id",
            "performed_by",
            "notified_to",
            "message",
            "performed_at",
            "message_key",
        )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "performed_by",
            "notified_to",
            "message",
            "is_read",
            "performed_at",
            "message_key",
        )
        read_only_fields = (
            "id",
            "performed_by",
            "notified_to",
            "message",
            "performed_at",
            "message_key",
        )
