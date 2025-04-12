from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.
class EmailLevel(models.Model):
    level_id = models.AutoField(primary_key=True)
    level_desc = models.CharField(max_length=200)

    def __str__(self):
        return self.level_desc


class EmailType(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_desc = models.CharField(max_length=200)

    def __str__(self):
        return self.type_desc

class Announcement(models.Model):
    email_level = models.ForeignKey(EmailLevel, on_delete=models.CASCADE)
    email_type = models.ForeignKey(EmailType, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    content = CKEditor5Field('Content', config_name='default')
    created_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_url = models.URLField(max_length=500, null=True, blank=True)
    drive_file_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.subject

class ViberContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    viber_id = models.CharField(max_length=255)

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['start_date']