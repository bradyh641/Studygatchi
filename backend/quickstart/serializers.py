from datetime import datetime
from typing import Any
from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import ProhibitedSite, StudyUser, Task

# TODO Add docstrings to each of these functions to help newcomers understand what they do


# serializers are cool because they allow you to skip having to deal with the model constructors
User = get_user_model()


class StudyUserSerializer(serializers.HyperlinkedModelSerializer):
    # includes support for password hashing and safety
    class Meta:  # type: ignore
        # TODO Changed from User to StudyUser
        model = User
        fields = ["id", "username", "email", "password", "money"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {
                    "input_type": "password",
                },
            }
        }

    def create(self, validated_data: dict[str, Any]) -> StudyUser:
        # hashes passwords
        return StudyUser.objects.create_user(**validated_data)


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:  # type: ignore
        model = Task
        fields: list[str] = ["reward", "name", "category", "due_date", "description", "user"]

    def validate_due_date(self, value: datetime) -> datetime:
        if value < timezone.now():
            raise serializers.ValidationError("Newly created task cannot be past due")
        return value


class ProhibitedSiteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ProhibitedSite
        fields = ["id", "hostname", "user"]
        read_only_fields = ["id"]

    def validate_hostname(self, value: str) -> str:
        hostname = value.strip()
        if not hostname:
            raise serializers.ValidationError("A website address is required.")

        parsed = urlsplit(hostname if "://" in hostname else f"https://{hostname}")
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise serializers.ValidationError("Enter a valid website address.")
        if parsed.username or parsed.password or parsed.port:
            raise serializers.ValidationError("Enter a hostname without credentials or a port.")

        normalized = parsed.hostname.rstrip(".").lower()
        if "." not in normalized or any(
            not label or label.startswith("-") or label.endswith("-")
            for label in normalized.split(".")
        ):
            raise serializers.ValidationError("Enter a valid website hostname.")

        return normalized

    def validate_reward(self, value: int) -> int:
        if value < 0:
            raise serializers.ValidationError("Reward cannot be negative")

        # Reward moderation will go here, for now we can have basic moderation and set a limit (like $100)
        if value > 100:
            raise serializers.ValidationError("Reward exceeds permitted amount")

        return value
