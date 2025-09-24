import pygame

class MenuOperon:
    """
    菜单操作子 - 实现游戏主菜单界面
    遵循细菌代码原则：小巧、模块化、独立自足
    """
    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 尝试加载中文字体，如果失败则使用默认字体
        try:
            # 优先使用simhei（黑体），然后simsun（宋体）
            chinese_fonts = ['simhei', 'simsun']
            self.font = None
            self.large_font = None
            self.small_font = None
            
            for font_name in chinese_fonts:
                try:
                    self.font = pygame.font.SysFont(font_name, 36)
                    self.large_font = pygame.font.SysFont(font_name, 72)
                    self.small_font = pygame.font.SysFont(font_name, 24)
                    break
                except:
                    continue
            
            # 如果中文字体都不可用，使用默认字体
            if self.font is None:
                self.font = pygame.font.Font(None, 36)
                self.large_font = pygame.font.Font(None, 72)
                self.small_font = pygame.font.Font(None, 24)
                
        except:
            # 任何异常都回退到默认字体
            self.font = pygame.font.Font(None, 36)
            self.large_font = pygame.font.Font(None, 72)
            self.small_font = pygame.font.Font(None, 24)
        
        # 颜色定义
        self.colors = {
            'background': (20, 20, 30),
            'button': (70, 70, 90),
            'button_hover': (100, 100, 120),
            'text': (255, 255, 255),
            'text_shadow': (0, 0, 0),
            'accent': (100, 200, 255)
        }
        
        # 按钮定义
        self.buttons = {
            'start': {
                'text': '开始游戏',
                'rect': pygame.Rect(0, 0, 300, 60),
                'hovered': False
            },
            'exit': {
                'text': '退出游戏',
                'rect': pygame.Rect(0, 0, 300, 60),
                'hovered': False
            }
        }
        
        # 初始化按钮位置
        self._position_buttons()
    
    def _position_buttons(self):
        """计算并设置按钮位置"""
        start_y = self.screen_height // 2
        
        # 开始游戏按钮
        self.buttons['start']['rect'].centerx = self.screen_width // 2
        self.buttons['start']['rect'].centery = start_y
        
        # 退出游戏按钮
        self.buttons['exit']['rect'].centerx = self.screen_width // 2
        self.buttons['exit']['rect'].centery = start_y + 100
    
    def handle_events(self, events, mouse_pos):
        """处理菜单事件"""
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                # 检查鼠标悬停
                for button in self.buttons.values():
                    button['hovered'] = button['rect'].collidepoint(mouse_pos)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 检查按钮点击
                if self.buttons['start']['rect'].collidepoint(mouse_pos):
                    return "start_game"
                elif self.buttons['exit']['rect'].collidepoint(mouse_pos):
                    return "exit_game"
        
        return None
    
    def draw(self, screen):
        """绘制菜单界面"""
        # 绘制背景
        screen.fill(self.colors['background'])
        
        # 绘制标题
        self._draw_title(screen)
        
        # 绘制按钮
        self._draw_buttons(screen)
        
        # 绘制版本信息
        self._draw_version_info(screen)
    
    def _draw_title(self, screen):
        """绘制游戏标题"""
        title_text = "BACTERIAL ROGUELITE"
        title_surface = self.large_font.render(title_text, True, self.colors['accent'])
        shadow_surface = self.large_font.render(title_text, True, self.colors['text_shadow'])
        
        # 计算位置（居中偏上）
        title_x = self.screen_width // 2 - title_surface.get_width() // 2
        title_y = self.screen_height // 4
        
        # 绘制阴影
        screen.blit(shadow_surface, (title_x + 3, title_y + 3))
        # 绘制标题
        screen.blit(title_surface, (title_x, title_y))
    
    def _draw_buttons(self, screen):
        """绘制菜单按钮"""
        for key, button in self.buttons.items():
            rect = button['rect']
            hovered = button['hovered']
            
            # 选择颜色
            button_color = self.colors['button_hover'] if hovered else self.colors['button']
            
            # 绘制按钮背景
            pygame.draw.rect(screen, button_color, rect, border_radius=10)
            pygame.draw.rect(screen, self.colors['text'], rect, 3, border_radius=10)
            
            # 绘制按钮文字
            text_surface = self.font.render(button['text'], True, self.colors['text'])
            shadow_surface = self.font.render(button['text'], True, self.colors['text_shadow'])
            
            # 计算文字位置（居中）
            text_x = rect.centerx - text_surface.get_width() // 2
            text_y = rect.centery - text_surface.get_height() // 2
            
            # 绘制阴影
            screen.blit(shadow_surface, (text_x + 2, text_y + 2))
            # 绘制文字
            screen.blit(text_surface, (text_x, text_y))
    
    def _draw_version_info(self, screen):
        """绘制版本信息"""
        version_text = "Version 0.1.0"
        version_surface = self.small_font.render(version_text, True, self.colors['text'])
        screen.blit(version_surface, (20, self.screen_height - 30))