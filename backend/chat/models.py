from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class ChatSession(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_sessions"
    )
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title()


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("assistance", "Assistance"),
    )
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:30]}"
