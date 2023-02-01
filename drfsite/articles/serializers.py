import io
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from .models import Artcile
from django.contrib.auth.models import User
#class ArticleModel:
#    def __init__ (self, title, content, author):
#        self.title = title
#        self.content = content
#        self.author = author

class ArticleSerializer(serializers.ModelSerializer):
    #user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Artcile
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        return user

# def encode():
#     model = ArticleModel('Paradise', 'Been spendin most their lives, livin in the gangstas paradise', 'Coolio')
#     model_sr = ArticleSerializer(model)
#     print(model_sr.data)
#     json = JSONRenderer().render(model_sr.data)
#     print(json)