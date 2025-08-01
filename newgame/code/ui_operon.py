import pygame

class UIOperon:
    """
    独立的UI渲染模块。
    负责在屏幕上绘制所有用户界面元素，如生命条。
    """
    def __init__(self, font_size=18):
        self.font = pygame.font.Font(None, font_size)
        self.health_bar_height = 5
        self.health_bar_y_offset = 10

    def draw_health_bars(self, screen, entities, combat_operon, camera_x=0):
        """
        为所有注册在战斗系统中的实体绘制生命条，并根据摄像头位置调整。
        """
        for entity in entities:
            if entity in combat_operon.health_systems:
                health_system = combat_operon.health_systems[entity]
                
                # Adjust position based on camera_x
                adjusted_x = entity.rect.left - camera_x
                
                # Health bar background (red)
                bg_rect = pygame.Rect(
                    adjusted_x,
                    entity.rect.top - self.health_bar_y_offset,
                    entity.rect.width,
                    self.health_bar_height
                )
                pygame.draw.rect(screen, (255, 0, 0), bg_rect)
                
                # Current health (green)
                health_percentage = health_system.current_hp / health_system.max_hp
                current_health_width = entity.rect.width * health_percentage
                fg_rect = pygame.Rect(
                    adjusted_x,
                    entity.rect.top - self.health_bar_y_offset,
                    current_health_width,
                    self.health_bar_height
                )
                pygame.draw.rect(screen, (0, 255, 0), fg_rect)
