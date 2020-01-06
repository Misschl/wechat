from django.conf import settings

from datetime import datetime
import os
import requests


class BaseHandle:
    def __init__(self, robot=None, message=None, **kwargs):
        self.robot = robot
        self.message = message
        self.kwargs = kwargs

    def get_avatar(self, *args, **kwargs):
        raise NotImplemented()

    def save_message_picture(self, *args, **kwargs):
        raise NotImplemented()

    def save_message_video(self, *args, **kwargs):
        raise NotImplemented()

    def save_message_recording(self, *args, **kwargs):
        raise NotImplemented()

    def save_message_file(self, *args, **kwargs):
        raise NotImplemented()


class FileHandle(BaseHandle):
    DEFAULT_ACATAR_PATH = r'media/image/avatar'
    DEFAULT_IMAGE_PATH = r'media/image'
    DEFAULT_VIDEO_PATH = r'media/video'
    DEFAULT_RECORDING_PATH = r'media/recording'
    DEFAULT_FILE_PATH = r'media/file'

    def get_avatar(self, instance):
        """存储头像"""
        content = instance.get_avatar()
        file_name = f'{instance.puid}.jpg'
        avatar_path = self.get_save_path(self.DEFAULT_ACATAR_PATH)
        path = os.path.join(avatar_path, file_name)
        with open(f'{path}', 'wb+') as f:
            f.write(content)
        return f'/{self.DEFAULT_ACATAR_PATH}/{file_name}'

    def get_file_attr(self):
        """获取文件名和内容"""
        assert self.message is not None, 'message can not be None'
        return self.get_file_name(), self.message.get_file()

    def save_media(self, default_path):
        """通用保存文件"""
        file_name, content = self.get_file_attr()
        save_path = os.path.join(self.get_save_path(default_path), file_name)
        with open(save_path, 'wb+') as f:
            f.write(content)
        return f'/{default_path}/{file_name}'

    @staticmethod
    def get_save_path(path):
        save_path = os.path.join(settings.BASE_DIR, path)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        return save_path

    def get_file_name(self):
        """如果要自定义名字,请重写该方法"""
        file_name = getattr(self.message, 'file_name', '')
        return file_name

    def save_message_picture(self):
        """本地保存图片"""
        return self.save_media(self.DEFAULT_IMAGE_PATH)

    def save_message_video(self):
        """本地保存视频"""
        return self.save_media(self.DEFAULT_VIDEO_PATH)

    def save_message_recording(self):
        """本地存储录音"""
        return self.save_media(self.DEFAULT_RECORDING_PATH)

    def save_message_file(self):
        """本地存储文件"""
        return self.save_media(self.DEFAULT_FILE_PATH)

    def save_send_media(self, default_path, default_extension_name):
        attr = self.kwargs
        url = attr.get('url')
        file_name = f'{datetime.now().strftime("%Y%m%d-%H%M%S")[2:]}.{default_extension_name}'
        save_path = os.path.join(self.get_save_path(default_path), file_name)
        r = self.download(url)
        with open(save_path, 'wb+') as f:
            for chunk in r.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)
        return f'/{default_path}/{file_name}', save_path

    def download(self, url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, stream=True, headers=headers)
        return r

    def save_send_image(self):
        return self.save_send_media(self.DEFAULT_IMAGE_PATH, 'jpg')

    def save_send_video(self):
        return self.save_send_media(self.DEFAULT_VIDEO_PATH, 'mp4')

    def save_send_file(self):
        return self.save_send_media(self.DEFAULT_FILE_PATH, '')

    def save_send_recording(self):
        return self.save_send_media(self.DEFAULT_RECORDING_PATH, 'mp3')
