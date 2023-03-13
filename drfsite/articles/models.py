from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Article(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField()
    author = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    count_of_likes = models.IntegerField(default=0)
    count_of_reviews = models.IntegerField(default=0)
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True, related_name='article_likes')

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

    def addCountReviews(self):
        self.count_of_reviews = self.count_of_reviews + 1
        self.save()

    def reduceCountReviews(self):
        self.count_of_reviews = self.count_of_reviews - 1
        self.save()


class Review(models.Model):
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name='Article', on_delete=models.CASCADE)
    content = models.TextField()
    time_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    def on_delete(self):
        self.article.reduceCountReviews()


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class ProzaUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    saved = models.ManyToManyField('Article')
    follows = models.ManyToManyField('ProzaUser', related_name='ProzaUser_follows')
    subscribers = models.ManyToManyField('ProzaUser', related_name='ProzaUser_subscribers')
    fav_category = models.ManyToManyField('Category')
    achieved = models.ManyToManyField('Achievement')

class ReportArticle(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    content = models.TextField()
    article = models.ForeignKey(Article, verbose_name='Article', on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class Achievement(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    requirement = models.TextField()
    ico = models.TextField()

    def __str__(self):
        return self.name



