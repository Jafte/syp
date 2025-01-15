from uuid import uuid4

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    friends = models.ManyToManyField("self", through="Friendship", symmetrical=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def sent_friendship_requests_without_response(self):
        return self.sent_friendship_requests.filter(accepted_at__isnull=True, rejected_at__isnull=True)

    def received_friendship_requests_without_response(self):
        return self.received_friendship_requests.filter(accepted_at__isnull=True, rejected_at__isnull=True)

    def friendship_with(self, user):
        return Friendship.objects.filter(user=self, friend=user).first()

    def friendship_requests(self):
        return FriendshipRequest.objects.filter(Q(sender=self) | Q(receiver=self)).filter(accepted_at__isnull=True, rejected_at__isnull=True).all()

    def friendship_request_from(self, user):
        return FriendshipRequest.objects.filter(sender=user, receiver=self, accepted_at__isnull=True, rejected_at__isnull=True).first()

    def friendship_request_to(self, user):
        return FriendshipRequest.objects.filter(sender=self, receiver=user, accepted_at__isnull=True, rejected_at__isnull=True).first()


class Friendship(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE, related_name="friendships")
    friend = models.ForeignKey(User, verbose_name=_("friend"), on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)


class FriendshipRequest(models.Model):
    # uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_friendship_requests")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_friendship_requests")
    comment = models.TextField(blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_pending(self):
        return self.accepted_at is None and self.rejected_at is None

    def accept(self):
        if self.rejected_at:
            raise ValueError("Request already rejected")
        if self.accepted_at:
            raise ValueError("Request already accepted")
        self.accepted_at = timezone.now()
        self.save()
        Friendship.objects.create(user=self.sender, friend=self.receiver)
        Friendship.objects.create(user=self.receiver, friend=self.sender)

    def reject(self):
        if self.rejected_at:
            raise ValueError("Request already rejected")
        if self.accepted_at:
            raise ValueError("Request already accepted")
        self.rejected_at = timezone.now()
        self.save()
