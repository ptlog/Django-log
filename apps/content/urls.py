
from django.conf.urls import url
from content import views
from content.views import  ProfileView, EditorView, ShowView, LikeView, IndexView
urlpatterns = [
    url(r'^index/(\d*)$', IndexView.as_view(), name='index'),  # 首页
    url(r'^profile$', ProfileView.as_view(), name='profile'),  # 网站简介
    url(r'^editor$', EditorView.as_view(), name='editor'),  # 编辑

    url(r'^show/(\d+)$', ShowView.as_view(), name='show'),  # 内容展示

    url(r'^like$', LikeView.as_view(), name='like'),  # 收藏夹处理

    url(r'^dellike/(\d+)$', views.dellike, name='dellike')  # 删除收藏


]
