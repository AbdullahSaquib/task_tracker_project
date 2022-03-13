from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Manager for allowing createsuperuser command for our custom user
    model
    """
    def create_user(self, email, password=None):
        """Creates and saves a User with the given email and password"""
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email),)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """Creates and saves a superuser with the given email and password"""
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    Custom user model for distinguishing between two types of users:
    team leader and team member
    """
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_team_leader = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        """To be able to use admin interface we require is_staff property"""
        return self.is_team_leader

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

class Team(models.Model):
    """Team of users"""
    name = models.CharField(max_length=256)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leading_team")
    members = models.ManyToManyField(User)


class Task(models.Model):
    """Task information"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status

    class Priority(models.IntegerChoices):
        LOW = 1
        MEDIUM = 2
        HIGH = 3
    
    class Status(models.TextChoices):
        ASSIGNED = "assigned"
        IN_PROGRESS = "in progress"
        UNDER_REVIEW = "under review"
        DONE = "done"
    
    # Status for which user is considered as unavailable
    BUSY_STATUS = (Status.ASSIGNED, Status.IN_PROGRESS)

    name = models.CharField(max_length=256)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leading_task")
    team_members = models.ManyToManyField(User)  # members assigned to the task
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ASSIGNED)
    status_updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s %s" % (self.name, self.status)

    def save(self, *args, **kwargs):
        if self.status != self._original_status:
            self.status_updated_at = timezone.now()
        super().save(*args, **kwargs)
        self._original_status = self.status
