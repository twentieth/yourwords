from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from yourwords.models import English
from .serializers import EnglishSerializer


class EnglishList(generics.ListCreateAPIView):
    serializer_class = EnglishSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return English.users.where_user(self.request.user).all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EnglishDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EnglishSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return English.users.where_user(self.request.user).all().order_by('-created_at')
