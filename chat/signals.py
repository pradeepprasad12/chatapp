from django.contrib.auth.signals import user_logged_in,user_logged_out
from django.dispatch import receiver
from .models import UserProfile

@receiver(user_logged_in)
def set_user_online(sender, request, user, **kwargs):
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    user_profile.online = True
    user_profile.save()

@receiver(user_logged_out)
def set_user_offline(sender, request, user, **kwargs):
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    user_profile.online = False
    user_profile.save()
