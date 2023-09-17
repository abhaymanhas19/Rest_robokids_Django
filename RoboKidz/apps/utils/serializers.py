from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(CustomUserSerializer, self).__init__(*args, **kwargs)
        if self.context and self.context["request"].method in ["PUT", "PATCH"]:
            self.fields.pop("email")
            self.fields.pop("password")

    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False, write_only=True
    )

    def create(self, validated_data):
        # password = validated_data.pop('password')
        user_obj = User.objects.create_user(**validated_data)
        # user_obj.is_active = True
        # user_obj.set_password(password)
        # user_obj.save()
        return user_obj

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["email"] = instance.email
        return ret
