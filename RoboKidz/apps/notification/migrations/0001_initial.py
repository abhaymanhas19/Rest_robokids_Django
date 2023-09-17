# Generated by Django 4.1.1 on 2022-11-30 05:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                (
                    "performed_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "message_key",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "notified_to",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notified",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "performed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="performed",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
