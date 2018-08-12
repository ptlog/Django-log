
import re

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from itsdangerous import TimedJSONWebSignatureSerializer  as TJS, SignatureExpired
# Create your views here.
from django.views import View
from PIL import Image, ImageDraw, ImageFont
from django.utils.six import BytesIO
from user.models import User, Info
from content.models import Content
from Plog import settings
from celery_tasks.tasks import send_register_active_email
from utils.loginrequired import LoginRequired

# 验证码
# /user/identify_code
# def identify_code(request):
#     # 引入随机函数模块
#     import random
#     # 定义变量，用于画面的背景色、宽、高
#     bgcolor = (random.randrange(20, 100), random.randrange(
#         20, 100), 255)
#     width = 100
#     height = 25
#     # 创建画面对象
#     im = Image.new('RGB', (width, height), bgcolor)
#     # 创建画笔对象
#     draw = ImageDraw.Draw(im)
#     # 调用画笔的point()函数绘制噪点
#     for i in range(0, 100):
#         xy = (random.randrange(0, width), random.randrange(0, height))
#         fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
#         draw.point(xy, fill=fill)
#     # 定义验证码的备选值
#     str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
#     # 随机选取4个值作为验证码
#     rand_str = ''
#     for i in range(0, 4):
#         rand_str += str1[random.randrange(0, len(str1))]
#     # 构造字体对象，ubuntu的字体路径为“/usr/share/fonts/truetype/freefont”
#     font = ImageFont.truetype('FreeMono.ttf', 23)
#     # 构造字体颜色
#     fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
#     # 绘制4个字
#     draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
#     draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
#     draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
#     draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
#     # 释放画笔
#     del draw
#     # 存入session，用于做进一步验证
#     request.session['identify_code'] = rand_str
#     # 内存文件操作
#     buf = BytesIO()
#     # 将图片保存在内存中，文件类型为png
#     im.save(buf, 'png')
#     # 将内存中的图片数据返回给客户端，MIME类型为图片png
#     return HttpResponse(buf.getvalue(), 'image/png')






# /user/register

class RegisterView(View):
    '''注册页'''

    def get(self, request):
        '''注册页'''
        return render(request, 'register.html')

    def post(self, request):
        '''处理注册'''

        '''获取数据'''
        username = request.POST.get('username')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        email = request.POST.get('email')
        last_name = request.POST.get('name')
        # yzm = request.POST.get('identify_code')
        allow = request.POST.get('allow')
        print(username)

        '''校验数据'''
        # 判断数据完整性
        if not all([username, password, email,cpassword, last_name]):

           return render(request, 'register.html', {'err_msg':'请正确并完整的输入每行信息'})


        if cpassword != password:
            #判断密码是否相同
            return render(request, 'register.html', {'err_msg':'请输入两次相同的密码'})
        # 判断邮箱是否合法
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'err_msg': '邮箱格式不正确'})

        # # 判断验证码是否正确
        # identi_code = request.session.get('identify_code')
        # if  yzm != identi_code:
        #     return render(request, 'register.html', {'err_msg':'请输入正确的验证码'})

        # 判断是否同意协议
        if allow != 'on':
            return render(request, 'register.html', {'err_msg': '请同意使用协议'})

        # 判断用户名是否被注册过了
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 如果模型类获取不到username会跑出异常，这个异常是DoesNotExist
            # 用户名不存在
            user = None

        if user:
            '''用户已存在'''
            return render(request, 'register.html', {'err_msg': '用户已存在'})
        try:
            res = User.objects.get(last_name=last_name)
        except User.DoesNotExist :
            res = None

        if res:
            return render(request, 'register.html', {'err_msg': '此昵称已被使用'})


        '''进行业务处理，对用户进行注册'''
        user = User.objects.create_user(username, email, password, last_name=last_name)
        user.is_active = 0  # django 默认是激活的， 这里修改成未激活
        user.save()

        # 发送激活邮件， 包含激活链接：http://127.0.0.1:8000/user/active/user_id
        # 激活链接中需要包含用户的身份信息，并且要把身份信息进行加密
        tjs = TJS(settings.SECRET_KEY, 3600)  # settings.SECRET_KEY 是django自带的秘钥，后面的3600为过期时间

        # 设置加密的用户id，通过id来对注册信息进行激活
        info = {'confirm': user.id}

        # 加密用户的信息，生成激活的口令为token
        token = tjs.dumps(info)  # 这个是byte类型，需要给这个token进行解码
        token = token.decode()

        send_register_active_email.delay(email, token)

        return render(request, 'success.html')
        # return HttpResponse(name)


# /user/active/token
class ActiveView(View):
    '''邮箱激活处理'''
    def get(self, request, token):
        '''进行用户激活'''
        # 解密， 获取要激活用户信息, 秘钥和过期时间
        tjs = TJS(settings.SECRET_KEY, 3600)

        try:
            # 获取待激活的id
            info = tjs.loads(token)
            user_id = info['confirm']

            #对相应的id进行设置激活状态
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


# /user/user_center
class UserCenterView(LoginRequired, View):
    '''用户中心'''
    def get(self, request):
        '''用户中心'''
        user = request.user
        try:
            # 获取用户相应的信息的查询集
            user_info = Info.objects.filter(user=user)
        except Info.DoesNotExist:
            user_info = None
        try:
            # 获取用户相应的作品的查询集
            user_con = Content.objects.filter(user=user)
        except Content.DoesNotExist:
            user_con = None

        # 获取用户的收藏信息
        # try:
        #     like_info = Info.objects.filter(id=user_info.like)
        # except Info.DoesNotExist:
        #     like_info =None
        like_info = list()
        try:
            for i in user_info:
                info = Content.objects.filter(id=i.like)
                # i.info = info
                print(type(info))
                # print(type(info))
                for a in info:
                    like_info.append(a)

        except Info.DoesNotExist:
            pass
        for i in like_info:
            print(i.title)
            print(i.user.last_name)
        # #
        return render(request, 'user_center.html', {'user_info':user_info, 'user_con':user_con, 'like_info':like_info})


# /user/login
class LoginView(View):
    '''登录页'''
    def get(self, request):
        '''登录页面'''

        return render(request, 'login.html')


    def post(self, request):
        '''处理用post提交的数据'''
        # 获取数据
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 校验数据
        if not all([username, password]):
        # 业务处理：返回json
            return render(request, 'login.html', {'err_msg':'输入框内不能为空'})
        # from django.contrib.auth import authenticate,
        #  通过django认证系统中的authenticate方法进行用户名和密码的校验
        #  返回　User 对象
        user = authenticate(username=username, password=password)
        if user is not None:
            '''如果用户认证正确'''
            if user.is_active:
                # 判断用户是否激活

                # 记录用户的登录状态
                # login()使用django的session框架讲用户的id保存在session中，也就是sessionId
                login(request, user)

                # 获取登录后要跳转的地址
                # http: // 127.0.0.1: 8000 / user / login?next = / user / user_center
                # 跳转到首页
                # 如果next的值为空，那么使用默认的地址goods:index,
                # 若next的值不为空，那么登录后跳转至next的值的地址
                next_url = request.GET.get('next', reverse('content:index', args=(1,) ))
                # 重定向返回到首页，同时接受一个redirect的对象
                return  redirect(next_url)



            else:
                # 用户未激活
                return render(request, 'login.html', {'err_msg': '账户未激活'})

        else:
            # 账号或密码错误
            return render(request, 'login.html', {'err_msg': '账号或密码错误'})
            # return JsonResponse({'res':3})



# /user/loginout
class LogoutView(View):
    '''退出登录'''
    def get(self, request):

        # 清除用户的session信息
        logout(request)  # django的认证系统中的logout方法

        # 跳转到首页
        return redirect(reverse('content:index', args=(1,)))