import pygame
import os

class ShootingAnimation:
    """远程射击动画系统"""

    def __init__(self, frame_folder="13", frame_prefix="processed_frame_", frame_extension=".png"):
        """
        初始化射击动画

        Args:
            frame_folder: 射击动画帧所在的文件夹
            frame_prefix: 帧文件名前缀
            frame_extension: 帧文件扩展名
        """
        self.frames = []
        self.current_frame_index = 0
        self.last_frame_time = 0
        self.frame_duration = 25  # 每帧持续时间(毫秒) - 加快播放速度
        self.is_active = False
        self.use_last_frame_only = False
        self.last_direction = 1  # 1为右，-1为左

        # 射击状态跟踪
        self.last_shot_time = 0
        self.shot_count = 0
        self.last_shot_sequence_time = 0

        # 加载动画帧
        self._load_frames(frame_folder, frame_prefix, frame_extension)

    def _load_frames(self, frame_folder, frame_prefix, frame_extension):
        """加载射击动画帧"""
        print(f"Loading shooting animation frames from {frame_folder}")

        # 按顺序加载帧(从1到25)
        for i in range(1, 26):
            frame_filename = f"{frame_prefix}{i}{frame_extension}"
            frame_path = os.path.join(frame_folder, frame_filename)

            if os.path.exists(frame_path):
                try:
                    frame = pygame.image.load(frame_path).convert_alpha()
                    # 调整图片大小
                    original_width, original_height = frame.get_size()
                    scale_factor = max(64 / original_width, 128 / original_height)
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)
                    frame = pygame.transform.scale(frame, (new_width, new_height))
                    self.frames.append(frame)
                    print(f"Loaded shooting frame: {frame_filename}")
                except pygame.error as e:
                    print(f"Failed to load shooting frame {frame_filename}: {e}")
            else:
                print(f"Shooting frame file not found: {frame_path}")

        print(f"Total shooting frames loaded: {len(self.frames)}")

    def start_shooting(self, direction=1):
        """开始射击动画"""
        current_time = pygame.time.get_ticks()
        time_since_last_shot = current_time - self.last_shot_time
        time_since_last_sequence = current_time - self.last_shot_sequence_time

        # 更新射击序列
        if time_since_last_sequence > 1000:  # 超过1秒，重置序列
            self.shot_count = 0
            self.use_last_frame_only = False

        self.shot_count += 1
        self.last_shot_sequence_time = current_time
        self.last_shot_time = current_time

        # 检查是否为快速射击序列
        if self.shot_count >= 2 and time_since_last_shot < 1000:
            self.use_last_frame_only = True
            # 快速射击：直接显示最后一帧，避免抽搐
            self.current_frame_index = len(self.frames) - 1 if self.frames else 0
        else:
            self.use_last_frame_only = False
            # 正常射击：从第一帧开始
            self.current_frame_index = 0

        # 重置动画状态
        self.is_active = True
        self.last_frame_time = current_time
        self.last_direction = direction

        # 返回结果
        result = {'direction': direction}

        # 如果是快速射击，立即发射子弹
        if self.use_last_frame_only:
            result['fire_immediately'] = True
        else:
            # 正常射击，动画播放完成后发射子弹
            result['fire_immediately'] = False
            # 记录需要发射子弹
            self.pending_shot = True

        print(f"Started shooting animation: shot_count={self.shot_count}, use_last_frame_only={self.use_last_frame_only}")
        return result

    def update(self):
        """更新动画状态"""
        if not self.is_active:
            return

        current_time = pygame.time.get_ticks()

        # 检查是否超过1秒没有射击，如果是则停止动画
        time_since_last_shot = current_time - self.last_shot_time
        if time_since_last_shot > 1000:
            self.is_active = False
            return

        if current_time - self.last_frame_time > self.frame_duration:
            if not self.use_last_frame_only:
                # 正常射击：播放完整动画
                self.current_frame_index += 1
                self.last_frame_time = current_time

                # 动画播放完成
                if self.current_frame_index >= len(self.frames):
                    self.current_frame_index = len(self.frames) - 1  # 停在最后一帧
                    # 如果有待发射的子弹，现在发射
                    if hasattr(self, 'pending_shot') and self.pending_shot:
                        self.should_fire_shot = True
                        self.pending_shot = False
            else:
                # 快速射击：直接显示最后一帧
                self.current_frame_index = len(self.frames) - 1

    def get_current_frame(self, direction=1):
        """获取当前动画帧"""
        if not self.is_active or not self.frames:
            return None

        # 更新方向
        if direction != 0:
            self.last_direction = direction

        frame = self.frames[self.current_frame_index]

        # 如果方向为左，翻转图片
        if self.last_direction < 0:
            frame = pygame.transform.flip(frame, True, False)

        return frame

    def is_playing(self):
        """检查动画是否正在播放"""
        return self.is_active

    def should_fire_now(self):
        """检查是否现在应该发射子弹"""
        should_fire = hasattr(self, 'should_fire_shot') and self.should_fire_shot
        if should_fire:
            # 重置发射标志
            self.should_fire_shot = False
        return should_fire

    def stop(self):
        """停止动画"""
        self.is_active = False

    def should_stop_movement(self):
        """检查是否应该停止移动"""
        if not self.is_active:
            return False

        current_time = pygame.time.get_ticks()
        time_since_last_shot = current_time - self.last_shot_time

        # 只有在最后一次射击后1秒内才停止移动
        return time_since_last_shot < 1000