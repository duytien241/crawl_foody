from django.contrib import admin
from .models import Website


# Register your models here.
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'uri')
    list_display_links = ('name', 'id')
    search_fields = ('name', 'uri')
    list_per_page = 20


admin.site.register(Website, WebsiteAdmin)
