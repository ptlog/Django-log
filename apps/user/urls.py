from django.conf.urls import url
from user.views import LoginView, RegisterView, UserCenterView, ActiveView, LogoutView
from user import views
urlpatterns = [
    url(r'^login$', LoginView.as_view(), name='login'),  # 登录页
    # url(r'^identify_code$', views.identify_code, name='identify_code'),  # 验证码
    url(r'^register$', RegisterView.as_view(), name='register'),  # 注册页
    url(r'^user_center$', UserCenterView.as_view(), name='user_center'),  # 用户中心
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),  # 邮箱激活处理

    url(r'^logout$', LogoutView.as_view(), name='logout'),  # 退出
]
