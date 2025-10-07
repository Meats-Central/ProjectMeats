"""
Bug Reports models for ProjectMeats.

Provides internal bug tracking and user feedback.
"""
from django.contrib.auth.models import User
from django.db import models


class BugReport(models.Model):
    """Bug report submitted by users."""
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('wont_fix', 'Won\'t Fix'),
    ]
    
    CATEGORY_CHOICES = [
        ('bug', 'Bug'),
        ('feature_request', 'Feature Request'),
        ('question', 'Question'),
        ('feedback', 'Feedback'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='bug'
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    
    # Reporter information
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='bug_reports'
    )
    reporter_email = models.EmailField(blank=True)
    
    # Technical details
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    screen_resolution = models.CharField(max_length=50, blank=True)
    url = models.URLField(blank=True)
    
    # Reproduction
    steps_to_reproduce = models.TextField(blank=True)
    expected_behavior = models.TextField(blank=True)
    actual_behavior = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bug Report'
        verbose_name_plural = 'Bug Reports'
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"
