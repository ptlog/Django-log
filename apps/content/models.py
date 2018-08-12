from django.db import models
from db.base_model import BaseModel
from tinymce.models import HTMLField
# Create your models here.


class Content(BaseModel):
    '''内容模型类'''
    title = models.CharField(max_length=20, verbose_name='标题')
    content = HTMLField(blank=True, verbose_name='内容')
    user = models.ForeignKey('user.User', verbose_name='所属账号')

    class Meta:
        db_table = 'p_content'
        verbose_name = '内容'
        verbose_name_plural = verbose_name