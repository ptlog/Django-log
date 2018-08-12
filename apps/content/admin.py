from django.contrib import admin
from content.models import Content
from django.core.cache import cache
# Register your models here.

class BaseAdmin(admin.ModelAdmin):
    '''站点管理基类'''

    def save_model(self, request, obj, form, change):
        '''新增或跟新表中的数据时调用'''
        super().save_model(request, obj, form, change)

        # 删除原先的缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        '''删除表中的数据时'''
        super().delete_model(request, obj)

        # 删除原先的缓存
        cache.delete('index_page_data')



class ContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

    class Media:
        js = ('/static/js/tiny_mce.js', 'static/js/textareas.js')

admin.site.register(Content)