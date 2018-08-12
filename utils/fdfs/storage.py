from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


# 自定义的存储系统必须是django.core.files.storage.Storage的子类
class FDFSStorage(Storage):
    '''fast dfs文件存储类'''
    '''
    自定义存储系统必须要重写_open,_save方法，而且要重写其他的方法，比如exists(),如果不重写他们，        会产生异常
    '''
    def __init__(self, client_conf=None, base_url=None):
        '''初始化'''
        '''
        params:client_conf是客户端配置文件的路径，默认为None
                base_url 是fdfs-nginx服务器的ip和port, 默认为None
        '''
        if client_conf is None:
            # 如果client_conf为None,那么客户端配置文件的地址为settings中配置的地址
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf
        if base_url is None:
            # 如果base_url为None， 那么fdfs-nginx服务器的ip和port为settings中配置好的ip和port
            base_url = settings.FDFS_SERVER_URL
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        '''打开文件'''
        pass

    def _save(self, name, content):
        '''保存文件时使用'''
        # name :你选择上传文件的名字
        # content: 包含你上传文件内容的File类的对象

        # 创建一个Fdfs_client的对象，括号内就是这个客户端的配置文件
        client = Fdfs_client(self.client_conf)

        # 上传文件到fastdfs 文件存储系统中,并返回一个字典
        res = client.upload_by_buffer(content.read())

        # @return dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # } if success else None

        # 判断上传的状态
        if res.get('Status') != 'Upload successed.':
            # 如果上传失败那么就抛出一个异常
            raise Exception('上传文件失败')

        # 上传成功，获取file_id
        file_id = res.get('Remote file_id')

        # 返回file_id
        return file_id

    def exists(self, name):
        '''Django 判断文件名是否可用于新文件'''

        # 由于我们的文件内容是存储在fastdfs文件存储服务器中的,
        # 返回来的是一个文件描述符，因此，这个name是可用于新文件

        # 可用于新文件时返回False
        # 不可用于新文件时返回True
        return False

    def url(self, name):
        '''返回文件的名称'''
        # 这里的name是fdfs-nginx返回的文件描述符
        return self.base_url+name

