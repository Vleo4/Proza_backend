from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, viewsets, mixins, filters, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

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

from django.shortcuts import render


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
        return Article.objects.filter(user__username=self.kwargs['slug'],
                                      is_published=True)  # .exclude(is_published=False)


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

        # Generating jwt token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "access": access_token,
            "refresh": str(refresh),
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


class ArticleAPILike(generics.UpdateAPIView):
    serializer_class = ArticleLikeSerializer
    queryset = Article.objects.all()

    def update(self, request, *args, **kwargs):
        user = self.request.user
        article_id = kwargs['pk']
        article_like, created = Article.objects.get_or_create(id=article_id)
        article_like.likes.add(user)
        serializer = ArticleLikeSerializer(article_like, data=request.data)
        return Response({'please move along': 'nothing to see here'}, status.HTTP_200_OK)

class SaveArticleAPI(generics.UpdateAPIView):
    serializer_class = ProzaUserSerializer

    def update(self, request, *args, **kwargs):
        user = self.request.user
        article_id = kwargs['pk']  # assuming the article ID is passed in as a URL parameter
        proza_user, created = ProzaUser.objects.get_or_create(user=user)
        proza_user.saved.add(article_id)
        serializer = ProzaUserSerializer(proza_user, data=request.data)
        return Response({'please move along': 'nothing to see here'}, status.HTTP_200_OK)


class SavedArticlesAPI(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        user = self.request.user.prozauser
        return user.saved.all()


class ProzaUserCurrentProfileAPI(generics.RetrieveAPIView):
    serializer_class = ProzaUserProfileSerializer
    queryset = ProzaUser.objects.all()

    def get_object(self):
        return self.request.user.prozauser


class ProzaUserProfileAPI(generics.RetrieveAPIView):
    serializer_class = ProzaUserProfileSerializer

    def get_object(self):
        return ProzaUser.objects.get(user__username=self.kwargs['slug'])


class TopListAPI(generics.ListAPIView):
    serializer_class = ArticleSerializer
    queryset = Article.objects.filter(is_published=True).order_by('-likes')


class ReportArticleAPI(generics.CreateAPIView):
    serializer_class = ReportArticleSerializer
    queryset = ReportArticle.objects.all()

    def report_article(self):
        article_id = ReportArticleSerializer.validated_data['article_id']
        reason = ReportArticleSerializer.validated_data['reason']
        article = Article.objects.get(id=article_id)
        report = ReportArticle(article=article, reason=reason)
        report.save()


class UserAchievementsAPI(generics.ListAPIView):
    serializer_class = UserAchievementSerializer
    queryset = UserAchievement.objects.all()

    def user_achievements(self):
        serializer = UserAchievementSerializer.objects.filter(user=self.kwargs['pk'])


class CategoryListAPI(generics.ListAPIView):
    serializer_class = CategorySerizlizer
    queryset = Category.objects.all()

class ArticleFromCategoryAPI(generics.ListAPIView):
    serializer_class = ArticleSerializer
    def get_queryset(self):
        return Article.objects.filter(cat=self.kwargs['pk']).exclude(is_published=False)

