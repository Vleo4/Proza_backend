from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from articles.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/article/', ArticleAPIList.as_view()),
    path('api/v1/article/', ArticleAPIUpdate.as_view()),
    path('api/v1/articlecreate/', ArticleAPICreate.as_view()),
    path('api/v1/articledelete/', ArticleAPIDestroy.as_view()),
    path('api/v1/article/<int:pk>/', ArticleAPIUpdate.as_view()),
    path('api/v1/articlecreate/', ArticleAPICreate.as_view()),
    path('api/v1/articledelete/<int:pk>/', ArticleAPIDestroy.as_view()),
    path('api/v1/register/', RegisterAPI.as_view(), name='register'),
    path('api/v1/getcurrentuserarticles/', CurrentUserArticlesAPIView().as_view()),
    path('api/v1/getuserarticles/', UserArticlesAPIView().as_view()),
    path('api/v1/getarticlereviews/', GetReviewsToArticleAPIView.as_view()),
    path('api/v1/getarticlesfromcategory/<int:pk>/', GetArticlesFromCategory.as_view()),
    # re_path(r".*", TemplateView.as_view(template_name='index.html')),
    path('api/v1/reviewcreate/', ReviewAPICreate.as_view()),
    path('api/v1/reviewdelete/<int:pk>/', ReviewAPIDestroy.as_view()),
    path('api/v1/review/', ReviewAPIList.as_view()),
    path('api/v1/searcharticle/', SearchArticles.as_view()),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='verify'),
]
