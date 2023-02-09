"""drfsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from articles.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/drf-auth/', include('rest_framework.urls')),
    path('api/v1/article/', ArticleAPIList.as_view()),
    path('api/v1/article/<int:pk>/', ArticleAPIUpdate.as_view()),
    path('api/v1/articlecreate/<int:pk>/', ArticleAPICreate.as_view()),
    path('api/v1/articledelete/<int:pk>/', ArticleAPIDestroy.as_view()),
    path('api/v1/register/', RegisterAPI.as_view(), name='register'),
    path('api/v1/getcurrentuserarticles/', CurrentUserArticlesAPIView().as_view()),
    path('api/v1/getuserarticles/<int:pk>/', UserArticlesAPIView().as_view()),
    path('api/v1/getarticlereviews/<int:pk>/', GetReviewsToArticleAPIView.as_view()),
    path('api/v1/getarticlesfromcategory/<int:pk>/', GetArticlesFromCategory.as_view()),
    #re_path(r".*", TemplateView.as_view(template_name='index.html')),
    path('api/v1/reviewcreate/', ReviewAPICreate.as_view()),
    path('api/v1/reviewdelete/<int:pk>/', ReviewAPIDestroy.as_view()),
    path('api/v1/review/', ReviewAPIList.as_view()),
    path('api/v1/searcharticle/', SearchArticles.as_view()),
]
