from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from yourwords.models import English
from .serializers import EnglishSerializer, UserSerializer


class EnglishList(generics.ListCreateAPIView):
    serializer_class = EnglishSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return English.users.where_user(self.request.user).all()


class EnglishDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EnglishSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return English.users.where_user(self.request.user).all()
