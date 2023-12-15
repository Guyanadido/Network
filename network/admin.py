from django.contrib import admin
from .models import Post, Comments, Likes, User, Flollow


# Register your models here.
admin.site.register(Post)
admin.site.register(Comments)
admin.site.register(Likes)
admin.site.register(User)
admin.site.register(Flollow)
