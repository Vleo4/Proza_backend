from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, viewsets, mixins, filters
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .custom_exceptions import CensorError
from .models import *
from .permissions import IsOwnerOrReadOnly
from .serializers import *
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import get_object_or_404, redirect


def censorship(validated_text):
    text = validated_text.lower().replace('.,#?!', ' ').split()
    roman_names_list = ['хуй', 'вагіна']
    swearword_count = 0
    word_count = len(text)
    for word in text:
        if word in roman_names_list:
            raise CensorError()
    return True


class ArticleAPIList(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class ArticleAPICreate(generics.CreateAPIView):
    serializer_class = ArticlePutSerializer
    permission_classes = (IsAuthenticated,)


class ArticleAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsOwnerOrReadOnly,)


class ArticleAPIDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        likes_connected = get_object_or_404(Article, id=self.kwargs['pk'])
        liked = False
        if likes_connected.likes.filter(id=self.request.user.id).exists():
            liked = True
        data['number_of_likes'] = likes_connected.number_of_likes()
        data['article_is_liked'] = liked
        return data


class ArticleAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsOwnerOrReadOnly,)


class UserArticlesAPIView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(user=self.kwargs['pk']).exclude(is_published=False)


class CurrentUserArticlesAPIView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user.id)


class GetReviewsToArticleAPIView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(article=self.kwargs['pk'])


class GetArticlesFromCategory(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(cat=self.kwargs['pk']).order_by('-time_create').exclude(is_published=False)


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


class ReviewAPICreate(generics.CreateAPIView):
    serializer_class = ReviewPutSerializer

    def post(self, request):
        try:
            censorship(request.data.get("content"))
        except CensorError:
            response = JsonResponse({"massage": 'Too much profanity', "status_code": 0})
            return response
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['article'].addCountReviews()
        serializer.save()
        return Response({'review': serializer.data})


class ReviewAPIList(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class ReviewAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def delete(self, instance, pk):
        review_id = pk
        review = get_object_or_404(Review, id=review_id)
        review.on_delete()
        review.delete()
        return Response(status=204)


class SearchArticles(generics.ListAPIView):
    search_fields = ['title', 'author', 'user__username', 'content']
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()


class ArticleAPILike(generics.RetrieveUpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def ArticleLike(self, pk):
        post = get_object_or_404(Article, id=self.POST.get('article_id'))
        if post.likes.filter(id=self.user.id).exists():
            post.likes.remove(self.user)
        else:
            post.likes.add(self.user)

            return HttpResponseRedirect(reverse('article_detail', args=[str(pk)]))
