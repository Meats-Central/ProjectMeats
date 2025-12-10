"""
AI Assistant models for ProjectMeats.

This module provides AI-powered chatbot functionality for meat market operations,
including document processing, entity extraction, and intelligent assistance
for purchase orders, suppliers, customers, and other business entities.
"""
import uuid

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from apps.tenants.models import Tenant

from apps.core.models import OwnedModel, StatusModel


class ChatSessionStatusChoices(models.TextChoices):
    """Status choices for chat sessions."""

    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    ARCHIVED = "archived", "Archived"


class ChatSession(OwnedModel, StatusModel):
    """Chat session model for managing conversations with the AI assistant."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the chat session",
    )

    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Optional title for the chat session",
    )

    session_status = models.CharField(
        max_length=20,
        choices=ChatSessionStatusChoices.choices,
        default=ChatSessionStatusChoices.ACTIVE,
        help_text="Current status of the chat session",
    )

    context_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON field for storing session context",
    )

    last_activity = models.DateTimeField(
        auto_now=True, help_text="Timestamp of last activity in this session"
    )

    class Meta:
        db_table = "ai_assistant_chat_sessions"
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"
        ordering = ["-last_activity"]

    def __str__(self):
        return f"Chat Session: {self.title or f'Session {self.id.hex[:8]}'}"


class MessageTypeChoices(models.TextChoices):
    """Message type choices for chat messages."""

    USER = "user", "User Message"
    ASSISTANT = "assistant", "AI Assistant Response"
    SYSTEM = "system", "System Message"
    DOCUMENT = "document", "Document Upload"


class ChatMessage(OwnedModel):
    """Individual chat message within a session."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the message",
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="Chat session this message belongs to",
    )

    message_type = models.CharField(
        max_length=20,
        choices=MessageTypeChoices.choices,
        help_text="Type of message",
    )

    content = models.TextField(help_text="Message content/text")

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the message",
    )

    is_processed = models.BooleanField(
        default=True, help_text="Whether the message has been fully processed"
    )

    class Meta:
        db_table = "ai_assistant_chat_messages"
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        ordering = ["created_on"]

    def __str__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.get_message_type_display()}: {preview}"


class AIConfiguration(models.Model):
    """Configuration settings for AI providers and models."""
    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="ai_configurations",
        help_text="Tenant this aiconfiguration belongs to"
    )

    name = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50, default="openai")
    model_name = models.CharField(max_length=100, default="gpt-4o-mini")
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_assistant_configurations"
        verbose_name = "AI Configuration"
        verbose_name_plural = "AI Configurations"

    def __str__(self):
        return f"{self.name} ({self.provider} - {self.model_name})"
