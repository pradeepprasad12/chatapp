# app/views.py
from chat.models import UserProfile,User
from .serializers import UserSerializer,UserProfileSerializer,ChatStartSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .renderers import UserRenderer
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view, permission_classes
import json
from django.http import JsonResponse
from django.views import View
from django.conf import settings  

class OnlineUsersListView(ListAPIView):
    queryset = UserProfile.objects.filter(online=True)
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]



def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }
  
class SignupAPIView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)
    
class LoginAPIView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            token = get_tokens_for_user(user)
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.online = True
            user_profile.save()
            return Response({'token': token,'msg':'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_chat(request):
    serializer = ChatStartSerializer(data=request.data)
    if serializer.is_valid():
        recipient_username = serializer.validated_data['recipient_username']

        # Check if the recipient is online
        try:
            recipient_profile = UserProfile.objects.get(user__username=recipient_username, online=True)
            return Response({'detail': 'Chat started with ' + recipient_username}, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'Recipient is offline or unavailable.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def suggest_friends(json_data, user_id):
    target_user = None

    for user in json_data:
        if user['id']  == user_id:
            target_user = user
            break

    if not target_user:
        return []

    def calculate_similarity(user1, user2):
        
        shared_interests = set(user1['interests'].keys()) & set(user2['interests'].keys())
        score = sum(user1['interests'][interest] for interest in shared_interests)
        return score

    similar_users = []
    for user in json_data:
        if user['id'] != user_id:
            similarity_score = calculate_similarity(target_user, user)
            similar_users.append((user, similarity_score))

    similar_users.sort(key=lambda x: x[1], reverse=True)

    top_recommendations = [user[0] for user in similar_users[:5]]
    return top_recommendations

class SuggestedFriendsView(View):
    def get(self, request, user_id):
        json_file_path = settings.BASE_DIR / 'chat' / 'api' / 'user_data.json'

        with open(json_file_path, 'r') as json_file:
            user_data = json.load(json_file)
            
        user_data = user_data.get('users', [])  

        recommendations = suggest_friends(user_data, int(user_id))

        return JsonResponse(recommendations, safe=False)