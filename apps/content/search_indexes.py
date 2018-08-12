from haystack import indexes

from content.models import  Content


'''
: 指定对于某个类的某些数据建立索引
:format : 模型类名 加 Index
'''
class ContentIndex(indexes.SearchIndex, indexes.Indexable):
    '''模型索引'''

    # text 是所以里面的字段, use_template=True指定根据表中的哪些字段建立索引文件的说明会放在一个文件中.
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):

        # 返回你的模型类
        return Content

    def index_queryset(self, using=None):
        # 返回模型类中的而所有数据的对象
        return self.get_model().objects.all()


