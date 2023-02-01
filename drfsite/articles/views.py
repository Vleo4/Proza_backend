from django.forms import model_to_dict
from django.shortcuts import render
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .models import Artcile
from .permissions import IsOwnerOrReadOnly
from .serializers import ArticleSerializer, RegisterSerializer, UserSerializer
from django.contrib.auth.models import User

class ArticleAPIList(generics.ListCreateAPIView):
     queryset = Artcile.objects.all()
     serializer_class = ArticleSerializer
     permission_classes = (IsAuthenticatedOrReadOnly, )


class ArticleAPIUpdate(generics.RetrieveUpdateAPIView):
     queryset = Artcile.objects.all()
     serializer_class = ArticleSerializer
     permission_classes = (IsOwnerOrReadOnly, )

class ArticleAPIDetailView(generics.RetrieveUpdateDestroyAPIView):
     queryset = Artcile.objects.all()
     serializer_class = ArticleSerializer


class ArticleAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Artcile.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsOwnerOrReadOnly, )

class UserArticlesAPIView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Artcile.objects.filter(user=self.kwargs['pk']).exclude(is_published=False)

class CurrentUserArticlesAPIView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Artcile.objects.filter(user=self.request.user.id)

# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
        "user": UserSerializer(user, context=self.get_serializer_context()).data
        })
