from rest_framework import serializers
from profiles_api import models


class HelloSerializer(serializers.Serializer):
    """Serializes a name field for testing our APIView"""
    name = serializers.CharField(max_length=10)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes a user profile object"""
    class Meta:
        model = models.UserProfile
        fields = ('id', 'email', 'name', 'password')
        extra_kwargs = {
            'password': {
                'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        """Create and return a new user"""
        user = models.UserProfile.objects.create_user(
            email = validated_data['email'],
            name = validated_data['name'],
            password = validated_data['password']
        )

        return user


# class ProfileFeedItemSerializer(serializers.ModelSerializer):
#     # Serializes profile feed item
#     class Meta:
#         model = models.ProfileFeedItem
#         fields = ('id', 'user_profile', 'destination', 'message', 'timestamp')
#         extra_kwargs ={'user_profile': {'read_only': True}}


class MessageSerializer(serializers.Serializer):
    destination = serializers.CharField(max_length=255)
    message = serializers.CharField(max_length=1000)