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
# Custom anti-plagiarism & censorship
from .checking_new_data import censorship, anti_plagiarism


class ArticleAPIList(generics.ListAPIView):
    queryset = Article.objects.filter(is_published=True)
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class ArticleAPICreate(generics.CreateAPIView):
    serializer_class = ArticlePutSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Article.objects.all()

    def get_content_from_all_Articles(self):
        all_content = [article.content for article in self.queryset.all()]
        return all_content

    def post(self, request):
        all_content = [article.content for article in self.queryset.all()]
        new_poem = request.data.get("content")
        plagiarism = anti_plagiarism(new_poem, all_content)
        if plagiarism != 0:
            response = JsonResponse({"massage": 'Plagiarism',
                                     "plagiarism_source": self.queryset[plagiarism - 1].pk,
                                     "status_code": 0})
            return response

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        proza_user_id = request.data.get("user")
        proza_user = ProzaUser.objects.get(id=proza_user_id)
        proza_user.achieved.add(1)
        return Response({"article": serializer.data, "status_code": 1})


class ArticleAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleUpdateDodikSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def update(self, request, **kwargs):
        all_content = [article.content for article in self.queryset.all() if article.pk != kwargs['pk']]
        instance = self.get_object()
        new_poem = request.data.get("content")
        plagiarism = anti_plagiarism(new_poem, all_content)
        if plagiarism != 0:
            response = JsonResponse({"massage": 'Plagiarism',
                                     "plagiarism_source": self.queryset[plagiarism - 1].pk,
                                     "status_code": 0})
            return response
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, serializer.validated_data)

        return Response({"article": serializer.data, "status_code": 1})

class ArticleDetailAPIView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

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
            response = JsonResponse({"massage": 'Too much profanity', "status_code": 400})
            return response
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['article'].addCountReviews()
        serializer.save()
        return Response({'review': serializer.data, "status_code": 200})


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
        user = self.request.user.id
        article_like = Article.objects.get(id=kwargs['pk'])
        if article_like.likes.filter(id=user).exists():
            article_like.likes.remove(user)
            tmp = article_like.count_of_likes - 1
            article_like.count_of_likes = tmp
            return Response({'message': 'unliked'}, status.HTTP_200_OK)
        else:
            article_like.likes.add(user)
            tmp = article_like.count_of_likes + 1
            article_like.count_of_likes = tmp
            return Response({'message': 'liked'}, status.HTTP_200_OK)


class SaveArticleAPI(generics.UpdateAPIView):
    serializer_class = ProzaUserSerializer

    def update(self, request, *args, **kwargs):
        user = self.request.user
        proza_user = ProzaUser.objects.get(user=user)
        article_x = kwargs['pk']  # assuming the article ID is passed in as a URL parameter
        if proza_user.saved.filter(id=article_x).exists():
            proza_user.saved.remove(article_x)
            return Response({'massage': 'unsaved'}, status.HTTP_200_OK)
        else:
            proza_user.saved.add(article_x)
            return Response({'massage': 'saved'}, status.HTTP_200_OK)


class SavedArticlesAPI(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        user = self.request.user.prozauser
        return user.saved.all()


class ProzaUserAchievementAPI(generics.ListAPIView):
    serializer_class = ProzaUserAchievementSerializer
    queryset = ProzaUser.objects.all()

    def get_queryset(self):
        user = self.request.user.prozauser
        return user.achieved.all()


class ProzaUserCurrentProfileAPI(generics.RetrieveAPIView):
    serializer_class = ProzaUserProfileSerializer
    queryset = ProzaUser.objects.all()

    def get_object(self):
        return self.request.user.prozauser


class ProzaUserProfileAPI(generics.RetrieveAPIView):
    serializer_class = ProzaUserProfileSerializer

    def get_object(self):
        return ProzaUser.objects.get(user__username=self.kwargs['slug'])


class SubscriptionAPI(generics.UpdateAPIView):
    serializer_class = ProzaUserSubscriptionSerializer

    def update(self, request, *args, **kwargs):
        subscriber = ProzaUser.objects.get(user=request.user)
        proza_user = ProzaUser.objects.get(user__username=kwargs['slug'])
        if proza_user.subscribers.filter(id=subscriber.id).exists():
            proza_user.subscribers.remove(subscriber)
            subscriber.follows.remove(proza_user)
            return Response({'massage': 'subscribe canceled'})
        else:
            proza_user.subscribers.add(subscriber)
            subscriber.follows.add(proza_user)
            return Response({'massage': 'subscribe success'})


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



class CategoryListAPI(generics.ListAPIView):
    serializer_class = CategorySerizlizer
    queryset = Category.objects.all()


class ArticleFromCategoryAPI(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(cat=self.kwargs['pk'], is_published=True)


class RecommendationAPI(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        proza_user = ProzaUser.objects.get(user=self.request.user)
        fav_category = proza_user.fav_category.all()
        return Article.objects.filter(cat__in=fav_category).order_by('-time_create').exclude(is_published=False)


class ProzaUserAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = ProzaUser.objects.all()
    serializer_class = ProzaUserUpdateSerializer
    permission_classes = (IsOwnerOrReadOnly,)

class RecommendationFollowsAPI(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Article.objects.all()

    def get_queryset(self):
        proza_user = ProzaUser.objects.get(user=self.request.user)
        follows = [follow.user.id for follow in proza_user.follows.all()]
        return Article.objects.filter(user__in=follows).order_by('-time_create').exclude(is_published=False)


class ProzaUserAchievements(generics.RetrieveAPIView):
    serializer_class = ProzaUserAchSerializer
    queryset = ProzaUser.objects.all()