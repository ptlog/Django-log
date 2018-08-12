from django.template import Library

register = Library()

'''
statement:  这个过滤器适用于剪切和清洗数据库中的数据，在开发的前一段时间，数据库中的数据有不干净的现象，单后来才知道把元组存进去了，所以现在暂时用不着这几个过滤器了
'''
@register.filter
def si_title(val):
    '''清洗数据'''
    val = str(val)
    val = val[2:-3]
    return val

@register.filter
def si_content(val):
    '''剪切数据'''
    val  = str(val)
    l = len(val)
    if l>300:
        val = val[0:300]
        val = val+'。。。。。。'
        return val
    else:
        val = val+'。。。。。。'
        return val