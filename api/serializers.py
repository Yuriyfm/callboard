from rest_framework import serializers
from main.models import Rubric, Ad


class RubricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubric
        fields = ['name', 'super_rubric']


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['rubric', 'title', 'content', 'price', 'contacts', 'image', 'author', 'is_active', 'created_at']
