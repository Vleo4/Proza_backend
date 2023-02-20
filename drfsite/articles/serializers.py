from rest_framework import serializers

from .models import *
from django.contrib.auth.models import User


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    cat = serializers.StringRelatedField()
    class Meta:
        model = Article
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class ReviewPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class CategorySerizlizer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        return user


class ArticlePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'content', 'author', 'is_published', 'cat', 'user')
