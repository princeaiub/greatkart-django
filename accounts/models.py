from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
# class MyAccountManager(BaseUserManager):
#     def create_user(self, first_name,last_name, user_name, email, password=None):
#         if not email:
#             raise ValueError('User Must Have an email address')
#         if not user_name:
#             raise ValueError('User Must Have an username address')
#         user = self.model(
#             email = self.normalize_email(email),
#             user_name=user_name,
#             first_name = first_name,
#             last_name = last_name
#         )
#         user.set_password(password)
#         user.save(using = self._db)
#         return user
#     def create_superuser(self, first_name,last_name, user_name, email, password):
#         user = self.create_user(
#             email= self.normalize_email(email),
#             user_name= user_name,
#             password= password,
#             first_name=first_name,
#             last_name= last_name
#         )
#         is_admin     = True
#         is_staff     = True
#         is_active    = True
#         is_superuser = True
#         user.save(using = self._db)


# class Account(AbstractBaseUser):
#     first_name   = models.CharField(max_length=50)
#     last_name    = models.CharField(max_length=50)
#     user_name    = models.CharField(max_length=50, unique=True)
#     email        = models.EmailField(max_length=100, unique=True)
#     phone        = models.CharField(max_length=50)

#     # required
#     date_of_join = models.DateTimeField(auto_now_add=True)
#     last_login   = models.DateTimeField(auto_now_add=True)
#     is_admin     = models.BooleanField(default=False)
#     is_staff     = models.BooleanField(default=False)
#     is_active    = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['user_name','first_name','last_name']
#     objects = MyAccountManager()

#     def __str__(self):
#         return self.email
    
#     def has_perm(self,perm,obj=None):
#         return self.is_admin
    
#     def has_module_perms(self, add_label):
#         return True

# create super user

class Superuser(models.Model):
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    user_name       = models.CharField(max_length=50, unique = True)
    password        = models.CharField(max_length=128,null=True, blank=True)
    email           = models.EmailField(max_length=100, unique=True)
    phone           = models.CharField(max_length=20, unique=True)
    is_admin        = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_superuser    = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=False)
    date_of_join    = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now_add=True)
    photo_superuser = models.ImageField(upload_to='superuser/profile_photo', blank=True)
    
    class Meta:
        verbose_name        = 'superuser'
        verbose_name_plural = 'superusers'

    def __str__(self):
        return self.user_name

# create staff user
class Staffuser(models.Model):
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    user_name       = models.CharField(max_length=50, unique = True)
    password        = models.CharField(max_length=128, null=True, blank=True)
    email           = models.EmailField(max_length=100, unique=True)
    phone           = models.CharField(max_length=20, unique=True)
    is_admin        = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_superuser    = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=False)
    date_of_join    = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now_add=True)
    photo_staffuser = models.ImageField(upload_to='staffuser/profile_photo', blank=True)
    
    class Meta:
        verbose_name        = 'staffuser'
        verbose_name_plural = 'staffusers'

    def __str__(self):
        return self.user_name


# create general user
class Generaluser(models.Model):
    first_name          = models.CharField(max_length=50)
    last_name           = models.CharField(max_length=50)
    user_name           = models.CharField(max_length=50, unique = True)
    password            = models.CharField(max_length=128, null=True, blank=True)
    email               = models.EmailField(max_length=100, unique=True)
    phone               = models.CharField(max_length=20, unique=True)    
    is_active           = models.BooleanField(default=False)
    date_of_join        = models.DateTimeField(auto_now_add=True)
    last_login          = models.DateTimeField(auto_now_add=True)
    photo_generaluser   = models.ImageField(upload_to='generaluser/profile_photo', blank=True)
    
    class Meta:
        verbose_name        = 'Generaluser'
        verbose_name_plural = 'Generalusers'

    def __str__(self):
        return self.user_name
