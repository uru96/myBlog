from django.contrib import admin
from .models import Post

# Register model Post in django admin

# Own style of Posts in django admin
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)} # fill slug field based on title
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')

