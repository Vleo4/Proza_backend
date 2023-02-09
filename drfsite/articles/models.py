from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Artcile(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField(blank=True)
    author = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    count_of_likes = models.IntegerField(default=0)
    count_of_reviews = models.IntegerField(default=0)
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)

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
    article = models.ForeignKey(Artcile, verbose_name='Article', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    def on_delete(self):
        self.article.reduceCountReviews()


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name
