import pygame
import os

class SimpleFrameAnimation:
    """简单的帧动画类，用于循环播放一系列图片"""

    def __init__(self, frame_folder, frame_prefix="frame_", frame_extension=".png"):
        """
        初始化帧动画

        Args:
            frame_folder: 帧图片所在的文件夹
            frame_prefix: 帧文件名前缀
            frame_extension: 帧文件扩展名
        """
        self.frames = []
        self.current_frame_index = 0
        self.last_frame_time = 0
        self.frame_duration = 30  # 每帧持续时间(毫秒) - 更快速度
        self.is_playing = True  # 默认保持播放状态
        self.last_direction = 1  # 记录最后的朝向，1为右，-1为左

        # 加载所有帧
        self._load_frames(frame_folder, frame_prefix, frame_extension)

    def _load_frames(self, frame_folder, frame_prefix, frame_extension):
        """加载所有帧图片"""
        print(f"Loading frames from {frame_folder}")

        # 按顺序加载帧(从1到29)
        for i in range(1, 30):
            frame_filename = f"{frame_prefix}{i}{frame_extension}"
            frame_path = os.path.join(frame_folder, frame_filename)

            if os.path.exists(frame_path):
                try:
                    frame = pygame.image.load(frame_path).convert_alpha()
                    # 等比例放大图片，使其比碰撞体积稍大一点
                    # 碰撞体积是32x64，我们将其放大到更合适的尺寸
                    original_width, original_height = frame.get_size()
                    # 计算放大比例，使图片更大更清晰
                    scale_factor = max(64 / original_width, 128 / original_height)
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)
                    frame = pygame.transform.scale(frame, (new_width, new_height))
                    self.frames.append(frame)
                    print(f"Loaded frame: {frame_filename} with size {frame.get_size()}")
                except pygame.error as e:
                    print(f"Failed to load frame {frame_filename}: {e}")
            else:
                print(f"Frame file not found: {frame_path}")

        print(f"Total frames loaded: {len(self.frames)}")

    # 移除了上半身帧加载功能

    # 移除了_combine_frames方法，因为我们现在在实时绘制时组合帧

    def play(self):
        """开始播放动画"""
        self.is_playing = True
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()

    def stop(self):
        """停止播放动画"""
        self.is_playing = False

    def update(self):
        """更新动画帧"""
        if not self.is_playing or not self.frames:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_time > self.frame_duration:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.last_frame_time = current_time

    def get_current_frame(self, direction=1):
        """获取当前帧图片，支持方向翻转"""
        # 更新最后的方向
        if direction != 0:
            self.last_direction = direction

        frame = None

        # 获取当前帧
        if self.frames:
            frame_index = self.current_frame_index % len(self.frames)
            frame = self.frames[frame_index]

        # 如果方向为左(-1)，翻转图片
        if frame and self.last_direction < 0:
            frame = pygame.transform.flip(frame, True, False)

        return frame

    # 移除了所有射击相关的方法

    def get_frame_count(self):
        """获取帧总数"""
        return len(self.frames)