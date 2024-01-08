from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _ 

class CustomUserManager(BaseUserManager):
    '''
    custom user manager where email is the unique indentifier 
    instead of usernames
    '''
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The email must be set'))
        
        email = self.normalize_email(email)
        # create the user using defined custom user model 
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):

        # set the default params a superuser should have
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        if extra_fields.get('is_active') is not True:
            raise ValueError(_('Superuser must have is_active=True'))

        self.create_user(email, password, **extra_fields)



