from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

User = settings.AUTH_USER_MODEL
from django.utils import timezone
import django


class Notification(models.Model):
    performed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="performed"
    )
    notified_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notified"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    performed_at = models.DateTimeField(default=django.utils.timezone.now)
    message_key = models.CharField(max_length=100, blank=True, null=True)
    