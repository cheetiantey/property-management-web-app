from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    role = models.CharField(max_length=12, default="viewer")
    phone_number = models.CharField(max_length=10, default="0000000000")

class Unit(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    lease = models.IntegerField()
    sqft = models.IntegerField()
    bed = models.IntegerField()
    bath = models.IntegerField()
    photo = models.CharField(max_length=500, default=None)
    location = models.TextField()
    
    def is_valid_unit(self):
        return self.lease > 0 and self.sqft > 0 and self.bed != 0 and self.bath != 0 

class Tenant(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, default=None)
    email = models.CharField(max_length=256, default=None)

class Maintenance(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, default=None)
    content = models.TextField()
    resolved = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Document(models.Model):
    unit = models.ForeignKey(Unit, on_delete = models.CASCADE)
    title = models.TextField()
    uploaded_file = models.FileField(upload_to='management/documents')
    
class Email(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="emails")
    sender = models.ForeignKey("User", on_delete=models.PROTECT, related_name="emails_sent")
    recipients = models.ManyToManyField("User", related_name="emails_received")
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender.email,
            "recipients": [user.email for user in self.recipients.all()],
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "read": self.read,
            "archived": self.archived
        }
