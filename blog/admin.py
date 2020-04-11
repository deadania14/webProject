from django.contrib import admin
from .models import Post
from .models import Article, Tag, Category
# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title', )}
    list_display = ('title', 'date_created', 'published', )
    list_filter = ('published', )

# Register your models here.
admin.site.register(Article, ArticleAdmin)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Post)