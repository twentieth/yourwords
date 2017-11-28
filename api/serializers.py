from django.contrib.auth.models import User
from rest_framework import serializers
from yourwords.models import English


class EnglishSerializer(serializers.ModelSerializer):
    class Meta:
        model = English
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
