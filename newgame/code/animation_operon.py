import pygame
import os

class Animation:
    """Handles sprite animation with frame sequencing and timing."""

    def __init__(self, frame_files, frame_duration=100, target_size=None):
        """
        Initialize animation with frame files.

        Args:
            frame_files: List of file paths to animation frames
            frame_duration: Time in milliseconds to display each frame
            target_size: Tuple (width, height) to resize frames to
        """
        self.frames = []
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.last_frame_time = 0
        self.is_playing = False
        self.loop = True
        self.hold_last_frame = True  # Whether to hold on the last frame when stopping

        # Load all frames
        for file_path in frame_files:
            try:
                frame = pygame.image.load(file_path).convert_alpha()
                # Resize frame if target_size is specified
                if target_size:
                    frame = pygame.transform.scale(frame, target_size)
                self.frames.append(frame)
            except pygame.error as e:
                print(f"Failed to load frame {file_path}: {e}")

        if not self.frames:
            raise ValueError("No frames loaded for animation")

    def play(self):
        """Start playing the animation."""
        self.is_playing = True
        self.current_frame = 0
        self.last_frame_time = pygame.time.get_ticks()

    def stop(self):
        """Stop playing the animation."""
        self.is_playing = False
        # If holding last frame, keep current frame; otherwise reset to first frame
        if not self.hold_last_frame:
            self.current_frame = 0

    def update(self):
        """Update animation frame based on timing."""
        if not self.is_playing:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_time > self.frame_duration:
            self.current_frame += 1
            self.last_frame_time = current_time

            # Handle animation loop
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.is_playing = False

    def get_current_frame(self):
        """Get the current frame surface."""
        if self.frames:
            return self.frames[self.current_frame]
        return None

    def get_frame_count(self):
        """Get the total number of frames."""
        return len(self.frames)

class PlayerAnimationSystem:
    """Manages all player animations including walking, idle, etc."""

    def __init__(self, frame_folder="12", frame_size=(32, 64)):
        """
        Initialize player animation system.

        Args:
            frame_folder: Folder containing animation frame images
            frame_size: Target size to resize frames to (width, height)
        """
        self.frame_folder = frame_folder
        self.frame_size = frame_size
        self.animations = {}
        self.current_animation = None

        # Load walking animation
        self._load_walking_animation()

        # Set default animation
        if 'walk' in self.animations:
            self.current_animation = self.animations['walk']
            self.current_animation.play()

    def _load_walking_animation(self):
        """Load walking animation frames from the frame folder."""
        try:
            # Get all frame files in order
            frame_files = []
            for i in range(1, 30):  # frame_1.png to frame_29.png
                frame_path = os.path.join(self.frame_folder, f"frame_{i}.png")
                if os.path.exists(frame_path):
                    frame_files.append(frame_path)
                else:
                    print(f"Warning: Missing frame file {frame_path}")

            if frame_files:
                # Create walking animation with 50ms per frame for smooth playback
                # hold_last_frame is already set to True in Animation constructor
                walk_animation = Animation(frame_files, frame_duration=50, target_size=self.frame_size)
                walk_animation.loop = True  # Ensure animation loops during movement
                self.animations['walk'] = walk_animation
                print(f"Loaded walking animation with {len(frame_files)} frames")
            else:
                print("No walking animation frames found")

        except Exception as e:
            print(f"Failed to load walking animation: {e}")

    def update(self, is_moving=False):
        """
        Update animation state.

        Args:
            is_moving: Whether the player is currently moving
        """
        # Switch to appropriate animation
        if is_moving and 'walk' in self.animations:
            if self.current_animation != self.animations['walk']:
                self.current_animation = self.animations['walk']
                self.current_animation.play()
        elif not is_moving and self.current_animation:
            # Stop the animation when not moving
            if self.current_animation.is_playing:
                self.current_animation.stop()

        # Update current animation
        if self.current_animation:
            self.current_animation.update()

    def get_current_frame(self):
        """Get the current animation frame."""
        if self.current_animation:
            frame = self.current_animation.get_current_frame()
            return frame
        return None