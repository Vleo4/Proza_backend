from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Article)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(ProzaUser)
admin.site.register(ReportArticle)
admin.site.register(UserAchievement)
