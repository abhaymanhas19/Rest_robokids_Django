from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampModel(models.Model):
    created_by = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="%(class)s_created_by"
    )
    updated_by = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="%(class)s_updated_by"
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        abstract = True
