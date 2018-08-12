from django.db import models

class BaseModel(models.Model):
    '''应用模型类基类'''
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_update = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')

    class Meta:
        abstract = True  # 指定它是抽象模型类
