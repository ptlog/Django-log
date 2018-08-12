from django.contrib.auth.decorators import login_required

class LoginRequired(object):
    @classmethod
    def as_view(cls, **initkwargs):
        '''动用父类的as_view'''

        view = super(LoginRequired, cls).as_view(**initkwargs)  # 这里继承的是View 里面的那个as_view()方法
        return login_required(view)