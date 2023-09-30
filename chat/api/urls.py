
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from chat.api.views import SignupAPIView,LoginAPIView,OnlineUsersListView,start_chat,SuggestedFriendsView
router = DefaultRouter()

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('',include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api-signup/',SignupAPIView.as_view(),name='api-signup'),
    path('api-login/', LoginAPIView.as_view(), name='api-login'),
    path('online-users/', OnlineUsersListView.as_view(), name='online-users-list'),
    path('chat/start/', start_chat, name='start-chat'),
    path('suggested-friends/<int:user_id>/', SuggestedFriendsView.as_view(), name='SuggestedFriendsView'),




]
