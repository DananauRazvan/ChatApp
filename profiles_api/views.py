from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework import filters
from rest_framework.authtoken import views
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from profiles_api import serializers
from profiles_api import models
from profiles_api import permissions

from elasticsearch import Elasticsearch
from datetime import datetime


class HelloApiView(APIView):
    """Test Api View"""
    serializer_class = serializers.HelloSerializer

    def get(self, request, format=None):
        """Returns a list of APIView features"""
        an_apiview = [
            'Uses HTTP methods as function (get, post, patch, put, delete)',
            'Is similar to a traditional Django View',
            'Gives you the most control over your application logic',
            'Is mapped manually to URLs'
        ]

        return Response({'message': 'Hello!', 'an_apiview': an_apiview})

    def post(self, request):
        """Create a hello message with our name"""
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            message = f'Hello {name}!'
            return Response({'message': message})
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, pk=None):
        """Handle updating an object"""
        return Response({'method': 'PUT'})

    def patch(self, request, pk=None):
        """Handle a partial update of an object"""
        return Response({'method': 'PATCH'})

    def delete(self, request, pk=None):
        """Delete an object"""
        return Response({'method': 'DELETE'})


class HelloViewSet(viewsets.ViewSet):
    """Test API ViewSet"""
    serializer_class = serializers.HelloSerializer

    def list(self, request):
        """Return a hello message"""
        a_viewset = [
            'Uses actions (list, create, retrieve, update, partial_update)',
            'Automatically maps to URLs using Routers',
            'Provides more functionality with less code'
        ]

        return Response({'message': 'Hello!', 'a_viewset': a_viewset})

    def create(self, request):
        """Create a new hello message"""
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            message = f'Hello {name}!'
            return Response({'message': message})
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, pk=None):
        """Handle getting an object by its ID"""
        return Response({'http_method': 'GET'})

    def update(self, request, pk=None):
        """Handle updating an object"""
        return Response({'http_method': 'PUT'})

    def partial_update(self, request, pk=None):
        """Handle updating part of an object"""
        return Response({'http_method': 'PATCH'})

    def destroy(self, request, pk=None):
        """Handle removing an object"""
        return Response({'http_method': 'DELETE'})


class UserProfileViewSet(viewsets.ModelViewSet):
    """Handle creating and updating profiles"""
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email',)


class UserLoginApiView(ObtainAuthToken):
    """Handle creating user authentication token"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    authentication_classes = (TokenAuthentication,)

# class UserProfileFeedViewSet(viewsets.ModelViewSet):
#      """Handle creating, reading and updating profile feed items"""
#      authentication_classes = (TokenAuthentication,)
#      serializer_class = serializers.ProfileFeedItemSerializer
#      queryset = models.ProfileFeedItem.objects.all()
#      permission_classes = (permissions.UpdateOwnStatus, IsAuthenticatedOrReadOnly)
#
#      def perform_create(self, serializer):
#          """Sets the user profile to the logged in user"""
#          serializer.save(user_profile=self.request.user)


class MessageAPIView(APIView):
    """Handle sending/getting messages between users"""
    serializer_class = serializers.MessageSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """Return from Elasticsearch"""
        username = str(request.user.name)

        es = Elasticsearch('http://localhost:9200')
        body = {
            'from': 0,
            'size': 10000,
            'query': {
                'match': {
                    'destination': username.lower()
                }
            }
        }
        res = es.search(index='posts', body=body)

        return Response(res['hits']['hits'])

    def post(self, request, format=None):
        """Send to Elasticsearch"""
        es = Elasticsearch('http://localhost:9200')
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            destination = serializer.validated_data.get('destination')
            destination_exists = models.UserProfile.objects.filter(name=destination).exists()
            message = serializer.validated_data.get('message')

            if destination_exists:
                doc = {
                    'source': str(request.user.name),
                    'destination': destination,
                    'message': message,
                    'timestamp': 124343253
                }
                res = es.index(index='posts', body=doc)
                return Response(res)
            else:
                return Response(
                    'User doesnt exist!',
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )