from rest_framework import serializers

from .models import *
from django.contrib.auth.models import User


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )
    cat = serializers.StringRelatedField()

    class Meta:
        model = Article
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username'}
        }


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

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
    #nickname = serializers.CharField(max_length=100)
    #description = serializers.CharField(allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password') #, 'nickname', 'description')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        proza_user = ProzaUser.objects.create(
            user=user,
            #nickname=validated_data['nickname'],
            #description=validated_data['description'],
        )

        return user


class ArticlePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'content', 'author', 'is_published', 'cat', 'user')


class ArticleLikeSerializer(serializers.ModelSerializer):
    likes = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all(), many=True)
    class Meta:
        model = Article
        fields = ('likes',)

class ProzaUserSaveSerializer(serializers.ModelSerializer):
    saved = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all(), many=True)

    class Meta:
        model = ProzaUser
        fields = ('saved',)


class ProzaUserSerializer(serializers.ModelSerializer):
    user = UserSerializer
    saved = ProzaUserSaveSerializer()

    class Meta:
        model = ProzaUser
        fields = "__all__"


class UserAchievementSerializer(serializers.ModelSerializer):
    user = UserSerializer

    class Meta:
        model = ProzaUser
        fields = "__all__"


class ProzaUserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = ProzaUser
        fields = "__all__"


class ProzaUserSubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = ProzaUser
        fields = ('follows', 'subscribers', 'user')
        fields = ('user', 'nickname', 'description')


class ReportArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportArticle
        fields = "__all__"


