from django.core.paginator import Paginator
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core.cache import  cache  # 导入django中的cache模块,用于从底层实现缓存借口

from utils.loginrequired import LoginRequired
# Create your views here.
from django.views import View
from content.models import Content
from user.models import Info


# /index/?page
class IndexView(View):

    def get(self, request, pindex):
        '''首页'''

        # cache.delete('index_page_data')
        ca_con = cache.get('index_page_data')
        # 获取所有Content的对象，并按降序排列，查到的是一个查询集
        if ca_con == None:

            con = Content.objects.all().order_by('-id')

            ca_con = {'con':con}
            cache.set('index_page_data', ca_con, 3600)
        con = ca_con['con']
        print(con)
        # 将内容按每页30条数据显示
        p = Paginator(con, 30)
        # 测试传过来的位置参数是什么类型
        print(type(pindex))

        if pindex == '':
            # 如果为空，那么设它的页码为1。
            pindex = 1

        try:
            # 把数据转换成整形
            pindex = int(pindex)
        except Exception as e:
            return render(request, 'fail.html')

        if pindex >= 15:
            pindex = 15

        # 获取第pindex页的数据
        page = p.page(pindex)

        context ={
            'page': page
        }

            # 设置首页缓存，并保存时间为1小时，一小时之后就更新数据

        # # 定义上下文
        # context.update(pindex=pindex)
        return render(request, 'index.html', context)


# /profile
class ProfileView(View):
    '''网站简介'''
    def get(self, request):
        '''网站简介'''
        return render(request, 'profile.html')


# /editor
class EditorView(LoginRequired,View):
    '''编辑页'''

    def get(self, request):
        '''编辑页'''
        return render(request, 'editor.html')

    def post(self, request):
        '''处理编辑页'''
        # 获取数据
        title = request.POST.get('title'),  # 标题
        title = title[0]
        print(type(title))
        print(title)
        # return HttpResponse(title, type(title))

        gcontent = request.POST.get('gcontent')  # 获取传递过来的数据

        # 数据校验
        if not all([gcontent, title]):
            return render(request, 'editor.html', {'err_msg':'请不要提交空文件'})

        # 业务处理： 添加数据
        # title = title[2:-3]
        user = request.user
        con = Content()
        con.content = gcontent
        con.title = title
        # return HttpResponse(title)
        con.user = user
        con.save()
        return redirect(reverse('content:show', args=(con.id,)))


# /show/?id
class ShowView(View):
    '''内容展示'''
    def get(self, request, id):
        '''内容展示'''
        try:
            # 如果不能获取到相应的信息，那么就返回fail界面
            con = Content.objects.get(id=id)
        except Content.DoesNotExist:
            return render(request, 'fail.html')
        title = con.title

        return render(request, 'show.html', {'con':con, 'title':title})
        # return HttpResponse(title)


# /like
class LikeView(LoginRequired, View):
    '''收藏处理'''
    # def get(self, request, id):
    #     user = request.user
    #     try:
    #         info =  Info.objects.filter(user=user).filter(like=id)
    #     except Info.DoesNotExist:
    #         return render(request, 'fail.html')
    #
    #     return

    def post(self, request):
        '''实现收藏功能'''
        # 获取用户
        user = request.user
        # 获取需要收藏内容的id
        colec = request.POST.get('id')
        print(colec)

        '''查询是否存在这个用户'''
        try:
            info = Info.objects.get(user=user)
        except Exception as e:
            # 如果没有，那么创建一个对象
            info = Info()
            info.user = user
            info.like = colec
            info.save()
            return JsonResponse({'res':1})
        # return JsonResponse({'res':2})

        '''如果存在用户,那么判断他是否收藏过了这个内容'''
        try:
            res =  info.filter(like=colec)

        except Exception as a :
            info = Info()
            info.like = colec
            info.user = user
            info.save()
            return JsonResponse({'res':1})

        return JsonResponse({'res':1})


# /dellike/?id
def dellike(request, id):
    '''取消收藏'''
    try:
        print(type(id))
        print(id)
        id = int(id)
        user = request.user
        info = Info.objects.filter(user=user).get(like=id)

    except Info.DoesNotExist:
        # 返回失败页面
        return render(request, 'fail.html')

    # 删除成功
    info.delete()
    return redirect(reverse('user:user_center'))













