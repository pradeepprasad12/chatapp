from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import User,UserProfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from chat.models import Message
from django.db.models import Q


def home(request):
    user = request.user
    if user.is_authenticated:
        user = request.user
        online_users = UserProfile.objects.filter(online=True)
        return render(request, 'chat/home.html', {'user': user,'online_users': online_users})
    else:
        return render(request, 'chat/home.html')
    

@login_required
def chat_view(request, user_id,sender_id):
    user = request.user
    if user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user__id=user_id, online=True)
        except UserProfile.DoesNotExist:
            return redirect('home')
        id=user_profile.id
        print("------------",id)
        if user.id == sender_id:
            suser = request.user
            recipient = get_object_or_404(User, id=user_id)
            
            messages = Message.objects.filter(
                
                Q(sender=user_id, recipient=sender_id) | Q(sender=sender_id, recipient=user_id)
            ).order_by('timestamp')
            
            formatted_messages = ["{} -- {}".format(message.sender.username, message.content) for message in messages]

            return render(request, 'chat/chat.html', {'recipient': recipient,'sender':suser,'formatted_messages': formatted_messages})
        else:
            return redirect('home')
    else:
        return redirect('login')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'chat/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to user's profile page
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})
