from rest_framework import serializers
from yourwords.models import English


class EnglishSerializer(serializers.ModelSerializer):
    class Meta:
        model = English
        fields = ('id', 'polish', 'english',
                  'sentence', 'rating', 'updated_at', 'created_at')
        read_only_fields = ('id', 'updated_at', 'created_at')
