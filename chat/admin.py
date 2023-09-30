from django.contrib import admin
from .models import UserProfile, Message

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'online')
    list_filter = ('online',)
    search_fields = ('user__username', 'user__email')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp','content')
    list_filter = ('sender', 'recipient', 'timestamp')
    search_fields = ('sender__username', 'recipient__username', 'content', 'timestamp')
