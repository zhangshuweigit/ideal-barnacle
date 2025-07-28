import pygame
import os

class ResourceOperon:
    """资源操纵子 - 管理图片和地图资源"""
    def __init__(self, base_path='..'):
        """
        初始化资源管理器。
        :param base_path: 资源文件夹相对于执行脚本的根路径。
        """
        self.base_paths = {
            'images': os.path.join(base_path, 'images'),
            'maps': os.path.join(base_path, 'maps')
        }
        self.fonts = {}
        self.images = {}
        self.maps = {}

    def _get_path(self, resource_type, *subpaths):
        """构建资源的完整路径。"""
        return os.path.join(self.base_paths[resource_type], *subpaths)

    def load_image(self, *subpaths):
        """加载图片资源，带缓存机制。"""
        path_key = os.path.join(*subpaths)
        if path_key not in self.images:
            full_path = self._get_path('images', *subpaths)
            try:
                image = pygame.image.load(full_path).convert_alpha()
                self.images[path_key] = image
            except pygame.error as e:
                print(f"Error loading image: {full_path} - {e}")
                self.images[path_key] = None # Cache failure to avoid retries
        return self.images[path_key]

    def load_map_path(self, map_name):
        """加载地图文件路径，返回路径字符串。"""
        if map_name not in self.maps:
            full_path = self._get_path('maps', map_name)
            if not os.path.exists(full_path):
                print(f"Error: Map file not found at {full_path}")
                self.maps[map_name] = None
            else:
                self.maps[map_name] = full_path
        return self.maps[map_name]

    def get_font(self, size):
        """加载字体，带缓存机制。"""
        if size not in self.fonts:
            self.fonts[size] = pygame.font.Font(None, size)
        return self.fonts[size]
