from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    # username = None
    email = models.EmailField(_('email address'), unique=True)
    email_confirmation = models.BooleanField(default=False)

    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.username
    

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='', null=True)
    # avatar = models.ImageField(upload_to=)

# account activation via email 
class AccountVerificationToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,  related_name='account_verification_token')

    token = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)


class EmailVerificationCode(models.Model):
    from django.conf import settings
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.PositiveBigIntegerField()
    used = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now_add=True)

    @property
    def expired(self):
        time_passed = (timezone.now() - self.creation_time).total_seconds() / 60
        return time_passed >= 1
    
    def __str__(self) -> str:
        return f'{self.code}'