from django.contrib import admin
from .models import Address, DataCrawl, Changes

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'typeAddress','active')

@admin.register(DataCrawl)
class DataCrawlAdmin(admin.ModelAdmin):
    list_display = ('id','directions')

@admin.register(Changes)
class ChangeAdmin(admin.ModelAdmin):
    list_display = ('id','source_old',)
# Register your models here.
