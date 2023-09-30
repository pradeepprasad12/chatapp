from rest_framework import serializers
from chat.models import UserProfile,User



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user', 'online')
  
class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = User
        fields=['username','password','password2']
        extra_kwargs={
        'password':{'write_only':True}
        }

    # Validating Password and Confirm Password while Registration
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        return attrs

    def create(self, validate_data):
        validate_data.pop('password2')  # Remove password2 from validated_data
        return User.objects.create_user(**validate_data)
        
class ChatStartSerializer(serializers.Serializer):
    recipient_username = serializers.CharField()