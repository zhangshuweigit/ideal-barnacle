import pygame
import json
import os

class SaveSelectOperon:
    """
    存档选择操作子 - 实现存档选择界面
    遵循细菌代码原则：小巧、模块化、独立自足
    """
    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.selected_save = None
        
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
                    self.large_font = pygame.font.SysFont(font_name, 48)
                    self.small_font = pygame.font.SysFont(font_name, 24)
                    break
                except:
                    continue
            
            # 如果中文字体都不可用，使用默认字体
            if self.font is None:
                self.font = pygame.font.Font(None, 36)
                self.large_font = pygame.font.Font(None, 48)
                self.small_font = pygame.font.Font(None, 24)
                
        except:
            # 任何异常都回退到默认字体
            self.font = pygame.font.Font(None, 36)
            self.large_font = pygame.font.Font(None, 48)
            self.small_font = pygame.font.Font(None, 24)
        
        # 颜色定义
        self.colors = {
            'background': (20, 20, 30),
            'save_slot': (70, 70, 90),
            'save_slot_hover': (100, 100, 120),
            'save_slot_empty': (50, 50, 70),
            'button': (70, 70, 90),
            'button_hover': (100, 100, 120),
            'ui_background': (30, 30, 40),
            'text': (255, 255, 255),
            'text_shadow': (0, 0, 0),
            'accent': (100, 200, 255),
            'warning': (255, 100, 100)
        }
        
        # 存档槽位定义
        self.save_slots = {
            1: {
                'rect': pygame.Rect(0, 0, 300, 120),
                'hovered': False,
                'data': None,
                'has_map': False
            },
            2: {
                'rect': pygame.Rect(0, 0, 300, 120),
                'hovered': False,
                'data': None,
                'has_map': False
            },
            3: {
                'rect': pygame.Rect(0, 0, 300, 120),
                'hovered': False,
                'data': None,
                'has_map': False
            }
        }
        
        # 删除按钮定义
        self.delete_buttons = {
            1: {
                'text': '删除',
                'rect': pygame.Rect(0, 0, 60, 30),
                'hovered': False
            },
            2: {
                'text': '删除',
                'rect': pygame.Rect(0, 0, 60, 30),
                'hovered': False
            },
            3: {
                'text': '删除',
                'rect': pygame.Rect(0, 0, 60, 30),
                'hovered': False
            }
        }
        
        # 确认删除对话框
        self.confirm_delete = {
            'active': False,
            'slot': None,
            'rect': pygame.Rect(0, 0, 400, 200),
            'yes_button': pygame.Rect(0, 0, 100, 40),
            'no_button': pygame.Rect(0, 0, 100, 40),
            'yes_hovered': False,
            'no_hovered': False
        }
        
        # 返回按钮
        self.back_button = {
            'text': '返回',
            'rect': pygame.Rect(50, 50, 100, 40),
            'hovered': False
        }
        
        # 初始化位置
        self._position_elements()
        
        # 加载存档数据
        self._load_save_data()
    
    def _position_elements(self):
        """计算并设置元素位置"""
        # 设置存档槽位位置
        start_y = self.screen_height // 3
        spacing = 140
        
        for i, (slot_num, slot) in enumerate(self.save_slots.items(), 1):
            slot['rect'].centerx = self.screen_width // 2
            slot['rect'].y = start_y + (i - 1) * spacing
            
            # 设置删除按钮位置
            delete_button = self.delete_buttons[slot_num]
            delete_button['rect'].x = slot['rect'].right - 70
            delete_button['rect'].centery = slot['rect'].y + 20
        
        # 设置返回按钮位置
        self.back_button['rect'].x = 50
        self.back_button['rect'].y = 50
        
        # 设置确认删除对话框位置
        self.confirm_delete['rect'].centerx = self.screen_width // 2
        self.confirm_delete['rect'].centery = self.screen_height // 2
        self.confirm_delete['yes_button'].x = self.confirm_delete['rect'].centerx - 120
        self.confirm_delete['yes_button'].centery = self.confirm_delete['rect'].centery + 80
        self.confirm_delete['no_button'].x = self.confirm_delete['rect'].centerx + 20
        self.confirm_delete['no_button'].centery = self.confirm_delete['rect'].centery + 80
    
    def _load_save_data(self):
        """加载存档数据"""
        for slot_num in self.save_slots:
            save_file = f'save_{slot_num}.json'
            
            # Load player data
            if os.path.exists(save_file):
                try:
                    with open(save_file, 'r') as f:
                        self.save_slots[slot_num]['data'] = json.load(f)
                except:
                    self.save_slots[slot_num]['data'] = None
            else:
                self.save_slots[slot_num]['data'] = None
                
            # Check if map file exists for this slot
            # For now, we'll show that all slots can have map data since they share the same base map
            self.save_slots[slot_num]['has_map'] = True
            
    def _delete_save_file(self, slot_num):
        """删除指定存档的所有相关文件"""
        import os
        files_to_delete = [
            f'save_{slot_num}.json',
            f'enemies_save_{slot_num}.json',
            f'interact_state_{slot_num}.json',
            f'map_save_{slot_num}.json'
        ]
        
        for filename in files_to_delete:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    print(f"Deleted {filename}")
                except Exception as e:
                    print(f"Failed to delete {filename}: {e}")
        
        # 重新加载存档数据
        self._load_save_data()
    
    def handle_events(self, events, mouse_pos):
        """处理存档选择事件"""
        # 检查鼠标悬停
        for slot_num, slot in self.save_slots.items():
            slot['hovered'] = slot['rect'].collidepoint(mouse_pos)
        
        # 检查删除按钮悬停
        for slot_num, button in self.delete_buttons.items():
            button['hovered'] = button['rect'].collidepoint(mouse_pos)
        
        # 检查返回按钮悬停
        self.back_button['hovered'] = self.back_button['rect'].collidepoint(mouse_pos)
        
        # 检查确认删除对话框按钮悬停
        if self.confirm_delete['active']:
            self.confirm_delete['yes_hovered'] = self.confirm_delete['yes_button'].collidepoint(mouse_pos)
            self.confirm_delete['no_hovered'] = self.confirm_delete['no_button'].collidepoint(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 如果确认删除对话框是激活的，处理对话框按钮点击
                if self.confirm_delete['active']:
                    if self.confirm_delete['yes_button'].collidepoint(mouse_pos):
                        # 确认删除
                        slot_to_delete = self.confirm_delete['slot']
                        self._delete_save_file(slot_to_delete)
                        self.confirm_delete['active'] = False
                        self.confirm_delete['slot'] = None
                        return f"deleted_save_{slot_to_delete}"
                    elif self.confirm_delete['no_button'].collidepoint(mouse_pos):
                        # 取消删除
                        self.confirm_delete['active'] = False
                        self.confirm_delete['slot'] = None
                    continue
                
                # 检查删除按钮点击优先于存档槽位点击
                delete_clicked = False
                for slot_num, button in self.delete_buttons.items():
                    if button['rect'].collidepoint(mouse_pos):
                        # 激活确认删除对话框
                        self.confirm_delete['active'] = True
                        self.confirm_delete['slot'] = slot_num
                        delete_clicked = True
                        break
                
                # 如果没有点击删除按钮，检查存档槽位点击
                if not delete_clicked:
                    for slot_num, slot in self.save_slots.items():
                        if slot['rect'].collidepoint(mouse_pos):
                            self.selected_save = slot_num
                            return f"select_save_{slot_num}"
                
                # 检查返回按钮点击
                if self.back_button['rect'].collidepoint(mouse_pos):
                    return "back_to_menu"
        
        return None
    
    def draw(self, screen):
        """绘制存档选择界面"""
        # 绘制背景
        screen.fill(self.colors['background'])
        
        # 绘制标题
        self._draw_title(screen)
        
        # 绘制存档槽位
        self._draw_save_slots(screen)
        
        # 绘制返回按钮
        self._draw_back_button(screen)
        
        # 绘制确认删除对话框（如果激活）
        if self.confirm_delete['active']:
            self._draw_confirm_delete_dialog(screen)
    
    def _draw_confirm_delete_dialog(self, screen):
        """绘制确认删除对话框"""
        rect = self.confirm_delete['rect']
        
        # 绘制对话框背景
        pygame.draw.rect(screen, self.colors['ui_background'], rect, border_radius=10)
        pygame.draw.rect(screen, self.colors['text'], rect, 3, border_radius=10)
        
        # 绘制确认文本
        confirm_text = f"确定要删除存档 {self.confirm_delete['slot']} 吗？"
        text_surface = self.font.render(confirm_text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=(rect.centerx, rect.centery - 30))
        screen.blit(text_surface, text_rect)
        
        # 绘制说明文本
        hint_text = "此操作不可撤销"
        hint_surface = self.small_font.render(hint_text, True, self.colors['warning'])
        hint_rect = hint_surface.get_rect(center=(rect.centerx, rect.centery))
        screen.blit(hint_surface, hint_rect)
        
        # 绘制确认按钮
        self._draw_dialog_button(screen, self.confirm_delete['yes_button'], 
                                "确定", self.confirm_delete['yes_hovered'])
        
        # 绘制取消按钮
        self._draw_dialog_button(screen, self.confirm_delete['no_button'], 
                                "取消", self.confirm_delete['no_hovered'])
    
    def _draw_dialog_button(self, screen, rect, text, hovered):
        """绘制对话框按钮"""
        button_color = self.colors['button_hover'] if hovered else self.colors['button']
        
        # 绘制按钮背景
        pygame.draw.rect(screen, button_color, rect, border_radius=5)
        pygame.draw.rect(screen, self.colors['text'], rect, 2, border_radius=5)
        
        # 绘制按钮文字
        text_surface = self.small_font.render(text, True, self.colors['text'])
        text_x = rect.centerx - text_surface.get_width() // 2
        text_y = rect.centery - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def _draw_title(self, screen):
        """绘制界面标题"""
        title_text = "选择存档"
        title_surface = self.large_font.render(title_text, True, self.colors['accent'])
        shadow_surface = self.large_font.render(title_text, True, self.colors['text_shadow'])
        
        # 计算位置（居中偏上）
        title_x = self.screen_width // 2 - title_surface.get_width() // 2
        title_y = self.screen_height // 6
        
        # 绘制阴影
        screen.blit(shadow_surface, (title_x + 3, title_y + 3))
        # 绘制标题
        screen.blit(title_surface, (title_x, title_y))
    
    def _draw_save_slots(self, screen):
        """绘制存档槽位"""
        for slot_num, slot in self.save_slots.items():
            rect = slot['rect']
            hovered = slot['hovered']
            data = slot['data']
            
            # 选择颜色
            if data is None:
                slot_color = self.colors['save_slot_empty']
            else:
                slot_color = self.colors['save_slot_hover'] if hovered else self.colors['save_slot']
            
            # 绘制槽位背景
            pygame.draw.rect(screen, slot_color, rect, border_radius=10)
            pygame.draw.rect(screen, self.colors['text'], rect, 3, border_radius=10)
            
            # 绘制槽位信息
            if data is None:
                self._draw_empty_slot(screen, rect, slot_num)
            else:
                self._draw_populated_slot(screen, rect, slot_num, data)
            
            # 绘制删除按钮（仅对已存在的存档）
            if data is not None:
                self._draw_delete_button(screen, slot_num)
    
    def _draw_delete_button(self, screen, slot_num):
        """绘制删除按钮"""
        button = self.delete_buttons[slot_num]
        rect = button['rect']
        hovered = button['hovered']
        
        # 选择颜色
        button_color = self.colors['button_hover'] if hovered else self.colors['button']
        
        # 绘制按钮背景
        pygame.draw.rect(screen, button_color, rect, border_radius=5)
        pygame.draw.rect(screen, self.colors['text'], rect, 2, border_radius=5)
        
        # 绘制按钮文字
        text_surface = self.small_font.render(button['text'], True, self.colors['text'])
        text_x = rect.centerx - text_surface.get_width() // 2
        text_y = rect.centery - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def _draw_empty_slot(self, screen, rect, slot_num):
        """绘制空存档槽位"""
        # 存档编号
        number_text = f"存档 {slot_num}"
        number_surface = self.font.render(number_text, True, self.colors['text'])
        number_x = rect.centerx - number_surface.get_width() // 2
        number_y = rect.centery - number_surface.get_height() // 2
        screen.blit(number_surface, (number_x, number_y))
        
        # 提示信息
        hint_text = "空存档"
        hint_surface = self.small_font.render(hint_text, True, self.colors['text'])
        hint_x = rect.centerx - hint_surface.get_width() // 2
        hint_y = rect.centery + 20
        screen.blit(hint_surface, (hint_x, hint_y))
    
    def _draw_populated_slot(self, screen, rect, slot_num, data):
        """绘制已有存档的槽位"""
        has_map = self.save_slots[slot_num]['has_map']
        
        # 存档编号
        number_text = f"存档 {slot_num}"
        number_surface = self.font.render(number_text, True, self.colors['text'])
        number_x = rect.centerx - number_surface.get_width() // 2
        number_y = rect.y + 15
        screen.blit(number_surface, (number_x, number_y))
        
        # 角色等级
        level = data.get('level', 1)
        level_text = f"等级: {level}"
        level_surface = self.small_font.render(level_text, True, self.colors['text'])
        level_x = rect.x + 20
        level_y = rect.y + 60
        screen.blit(level_surface, (level_x, level_y))
        
        # 金币数量
        currency = data.get('currency', 0)
        currency_text = f"金币: {currency}"
        currency_surface = self.small_font.render(currency_text, True, self.colors['text'])
        currency_x = rect.x + 150
        currency_y = rect.y + 60
        screen.blit(currency_surface, (currency_x, currency_y))
        
        # 永久加成
        upgrades = data.get('permanent_upgrades', {})
        if upgrades:
            upgrades_count = len([v for v in upgrades.values() if v > 1.0])
            upgrades_text = f"加成: {upgrades_count}"
            upgrades_surface = self.small_font.render(upgrades_text, True, self.colors['text'])
            upgrades_x = rect.x + 20
            upgrades_y = rect.y + 90
            screen.blit(upgrades_surface, (upgrades_x, upgrades_y))
        
        # 地图状态
        map_text = "地图: 有" if has_map else "地图: 无"
        map_color = self.colors['text'] if has_map else self.colors['warning']
        map_surface = self.small_font.render(map_text, True, map_color)
        map_x = rect.x + 150
        map_y = rect.y + 90
        screen.blit(map_surface, (map_x, map_y))
    
    def _draw_back_button(self, screen):
        """绘制返回按钮"""
        rect = self.back_button['rect']
        hovered = self.back_button['hovered']
        
        # 选择颜色
        button_color = self.colors['save_slot_hover'] if hovered else self.colors['save_slot']
        
        # 绘制按钮背景
        pygame.draw.rect(screen, button_color, rect, border_radius=5)
        pygame.draw.rect(screen, self.colors['text'], rect, 2, border_radius=5)
        
        # 绘制按钮文字
        text_surface = self.small_font.render(self.back_button['text'], True, self.colors['text'])
        text_x = rect.centerx - text_surface.get_width() // 2
        text_y = rect.centery - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def get_selected_save(self):
        """获取选中的存档编号"""
        return self.selected_save