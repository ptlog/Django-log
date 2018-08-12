from django.contrib.auth.models import AbstractUser
from django.db import models
from db.base_model import BaseModel
# Create your models here.


class User(AbstractUser, BaseModel):
    '''用户模型类'''

    class Meta:
        db_table = 'p_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

class Info(BaseModel):
    '''个人信息模型类'''
    user = models.ForeignKey('User', verbose_name='所属账号', on_delete=models.CASCADE)
    like = models.IntegerField(null=True, default='', verbose_name='收藏')
    class Meta:
        db_table = 'user_info'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name