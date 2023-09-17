from django.apps import AppConfig


class PostConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.post"

    def ready(self):
        from apps.post import signals
