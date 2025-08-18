import pygame
import math

class EnhancedUIOperon:
    """
    增强型UI操作子 - 实现极简、高效的游戏UI系统
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
            for font_name in chinese_fonts:
                try:
                    self.font = pygame.font.SysFont(font_name, 24)
                    break
                except:
                    continue
            
            # 如果中文字体都不可用，使用默认字体
            if self.font is None:
                self.font = pygame.font.Font(None, 24)
                
            # 加载其他尺寸字体
            self.small_font = pygame.font.Font(None, 18) if self.font is None else pygame.font.SysFont(chinese_fonts[0] if any(f in pygame.font.get_fonts() for f in chinese_fonts) else None, 18)
            self.large_font = pygame.font.Font(None, 48) if self.font is None else pygame.font.SysFont(chinese_fonts[0] if any(f in pygame.font.get_fonts() for f in chinese_fonts) else None, 48)
            
        except:
            # 任何异常都回退到默认字体
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
            self.large_font = pygame.font.Font(None, 48)
        
        # UI state
        self.low_health_flash = 0
        self.screen_shake_intensity = 0
        self.screen_shake_duration = 0
        self.damage_numbers = []
        self.interaction_prompts = []
        self.item_notifications = []
        self.fade_alpha = 0
        self.fade_direction = 0  # 1 for fade out, -1 for fade in
        
        # Colors
        self.colors = {
            'health_full': (0, 255, 0),
            'health_low': (255, 0, 0),
            'health_background': (50, 50, 50),
            'ui_background': (30, 30, 40, 180),
            'text_normal': (255, 255, 255),
            'text_shadow': (0, 0, 0),
            'warning': (255, 100, 100),
            'success': (100, 255, 100),
            'info': (100, 200, 255)
        }
    
    def update(self, delta_time):
        """Update UI animations and effects"""
        # Update low health flash
        if self.low_health_flash > 0:
            self.low_health_flash -= delta_time * 5
            if self.low_health_flash < 0:
                self.low_health_flash = 0
        
        # Update screen shake
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= delta_time
            if self.screen_shake_duration <= 0:
                self.screen_shake_intensity = 0
        
        # Update damage numbers
        for dmg in self.damage_numbers[:]:
            dmg['lifetime'] -= delta_time
            if dmg['lifetime'] <= 0:
                self.damage_numbers.remove(dmg)
            else:
                # Move upward
                dmg['y'] -= delta_time * 30
        
        # Update item notifications
        for notification in self.item_notifications[:]:
            notification['lifetime'] -= delta_time
            if notification['lifetime'] <= 0:
                self.item_notifications.remove(notification)
        
        # Update fade effect
        if self.fade_direction != 0:
            self.fade_alpha += delta_time * 200 * self.fade_direction
            if self.fade_alpha >= 255 and self.fade_direction > 0:
                self.fade_alpha = 255
                self.fade_direction = -1  # Start fading back in
            elif self.fade_alpha <= 0 and self.fade_direction < 0:
                self.fade_alpha = 0
                self.fade_direction = 0  # Stop fading
    
    def trigger_low_health(self):
        """Trigger low health visual effect"""
        self.low_health_flash = 1.0
    
    def trigger_hit_effect(self, intensity=5.0, duration=0.2):
        """Trigger hit feedback effect"""
        self.screen_shake_intensity = intensity
        self.screen_shake_duration = duration
    
    def add_damage_number(self, amount, x, y, is_critical=False):
        """Add a damage number to display"""
        color = (255, 215, 0) if is_critical else (255, 255, 255)  # Gold for critical
        self.damage_numbers.append({
            'amount': amount,
            'x': x,
            'y': y,
            'color': color,
            'lifetime': 1.0,  # 1 second
            'is_critical': is_critical
        })
    
    def add_item_notification(self, item_name):
        """Add item pickup notification"""
        self.item_notifications.append({
            'text': f"获得: {item_name}",
            'lifetime': 2.0,  # 2 seconds
            'start_time': pygame.time.get_ticks()
        })
    
    def start_fade_transition(self):
        """Start room transition fade effect"""
        self.fade_direction = 1  # Start fading out
    
    def get_screen_shake_offset(self):
        """Get current screen shake offset"""
        if self.screen_shake_intensity > 0 and self.screen_shake_duration > 0:
            offset_x = pygame.time.get_ticks() % 10 - 5
            offset_y = pygame.time.get_ticks() % 10 - 5
            return (offset_x * self.screen_shake_intensity / 10, 
                   offset_y * self.screen_shake_intensity / 10)
        return (0, 0)
    
    def draw_core_status(self, screen, player_health, max_health, currency=0):
        """绘制核心状态区"""
        # 1. 顶部中央血条
        self._draw_health_bar(screen, player_health, max_health)
        
        # 2. 右上角货币显示
        self._draw_currency(screen, currency)
    
    def _draw_health_bar(self, screen, current_hp, max_hp):
        """绘制玩家血条"""
        # Position at top center
        bar_width = 300
        bar_height = 20
        x = (self.screen_width - bar_width) // 2
        y = 20
        
        # Background
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(screen, self.colors['health_background'], bg_rect)
        pygame.draw.rect(screen, (0, 0, 0), bg_rect, 2)
        
        # Health fill
        health_percentage = current_hp / max_hp
        fill_width = int(bar_width * health_percentage)
        fill_rect = pygame.Rect(x, y, fill_width, bar_height)
        
        # Color based on health percentage
        if health_percentage > 0.5:
            color = self.colors['health_full']
        elif health_percentage > 0.25:
            color = (255, 165, 0)  # Orange
        else:
            color = self.colors['health_low']
            
        # Flash effect when low health
        if self.low_health_flash > 0:
            flash_intensity = int(255 * self.low_health_flash)
            color = (
                min(255, color[0] + flash_intensity),
                max(0, color[1] - flash_intensity),
                max(0, color[2] - flash_intensity)
            )
        
        pygame.draw.rect(screen, color, fill_rect)
        
        # Health text
        health_text = f"{int(current_hp)}/{int(max_hp)}"
        text_surface = self.small_font.render(health_text, True, self.colors['text_normal'])
        text_rect = text_surface.get_rect(center=(x + bar_width // 2, y + bar_height // 2))
        screen.blit(text_surface, text_rect)
    
    def _draw_currency(self, screen, currency):
        """绘制货币显示"""
        text = str(currency)
        text_surface = self.font.render(text, True, self.colors['text_normal'])
        shadow_surface = self.font.render(text, True, self.colors['text_shadow'])
        
        # Position at top right
        x = self.screen_width - 20
        y = 20
        
        # Draw shadow
        screen.blit(shadow_surface, (x - text_surface.get_width() + 2, y + 2))
        # Draw text
        screen.blit(text_surface, (x - text_surface.get_width(), y))
    
    def draw_weapon_slots(self, screen, weapon_operon):
        """绘制武器/技能快捷栏"""
        slot_size = 60
        slot_padding = 10
        total_width = 3 * slot_size + 2 * slot_padding
        start_x = (self.screen_width - total_width) // 2
        y = self.screen_height - 100
        
        slots = ['main_1', 'main_2', 'sub_1']  # We'll show 3 slots for now
        
        for i, slot_key in enumerate(slots):
            x = start_x + i * (slot_size + slot_padding)
            self._draw_weapon_slot(screen, x, y, slot_size, slot_key, weapon_operon)
    
    def _draw_weapon_slot(self, screen, x, y, size, slot_key, weapon_operon):
        """绘制单个武器槽位"""
        rect = pygame.Rect(x, y, size, size)
        
        # Slot background
        pygame.draw.rect(screen, self.colors['ui_background'], rect, border_radius=8)
        pygame.draw.rect(screen, (80, 80, 100), rect, 2, border_radius=8)
        
        # Weapon icon placeholder
        if slot_key in weapon_operon.slots and weapon_operon.slots[slot_key]:
            weapon = weapon_operon.slots[slot_key]
            # Draw weapon name initial
            initial = weapon.name[0] if weapon.name else "?"
            text_surface = self.font.render(initial, True, self.colors['text_normal'])
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
        
        # Cooldown overlay
        if slot_key in weapon_operon.skill_cooldowns:
            current_time = pygame.time.get_ticks()
            cooldown_end = weapon_operon.skill_cooldowns[slot_key]
            
            if current_time < cooldown_end:
                # Calculate cooldown progress
                cooldown_duration = getattr(weapon_operon.slots[slot_key], 'skill_cooldown', 1000) if slot_key in weapon_operon.slots else 1000
                elapsed = cooldown_end - current_time
                progress = min(1.0, elapsed / cooldown_duration)
                
                # Draw cooldown overlay
                overlay_height = int(size * progress)
                overlay_rect = pygame.Rect(x, y, size, overlay_height)
                overlay_surface = pygame.Surface((size, overlay_height), pygame.SRCALPHA)
                overlay_surface.fill((0, 0, 0, 180))
                screen.blit(overlay_surface, (x, y))
                
                # Draw cooldown text
                if progress > 0.1:
                    seconds = elapsed / 1000
                    time_text = f"{seconds:.1f}"
                    time_surface = self.small_font.render(time_text, True, self.colors['text_normal'])
                    time_rect = time_surface.get_rect(center=rect.center)
                    screen.blit(time_surface, time_rect)
    
    def draw_combat_feedback(self, screen):
        """绘制战斗反馈效果"""
        # Draw damage numbers
        for dmg in self.damage_numbers:
            font = self.font if not dmg['is_critical'] else self.large_font
            text = str(dmg['amount'])
            text_surface = font.render(text, True, dmg['color'])
            shadow_surface = font.render(text, True, (0, 0, 0))
            
            # Position with floating effect
            x = dmg['x']
            y = dmg['y']
            
            # Draw shadow
            screen.blit(shadow_surface, (x + 2, y + 2))
            # Draw text
            screen.blit(text_surface, (x, y))
    
    def draw_interaction_prompts(self, screen, nearby_interactable=None):
        """绘制交互提示"""
        if nearby_interactable:
            # Determine prompt text based on interactable type
            prompt_text = self._get_interaction_prompt(nearby_interactable)
            if prompt_text:
                self._draw_center_prompt(screen, prompt_text)
    
    def _get_interaction_prompt(self, interactable):
        """获取交互提示文本"""
        # This would need to be adapted based on your interactable types
        if hasattr(interactable, 'name'):
            if 'door' in interactable.name.lower():
                return "按 E 开门"
            elif 'chest' in interactable.name.lower():
                return "按 E 打开宝箱"
            elif 'scroll' in interactable.name.lower():
                return "按 E 收集卷轴"
        
        # Default interaction
        return "按 E 交互"
    
    def _draw_center_prompt(self, screen, text):
        """在屏幕中央下方绘制提示文本"""
        text_surface = self.font.render(text, True, self.colors['text_normal'])
        shadow_surface = self.font.render(text, True, self.colors['text_shadow'])
        
        x = self.screen_width // 2 - text_surface.get_width() // 2
        y = self.screen_height - 50
        
        # Draw shadow
        screen.blit(shadow_surface, (x + 2, y + 2))
        # Draw text
        screen.blit(text_surface, (x, y))
    
    def draw_item_notifications(self, screen):
        """绘制物品获取通知"""
        for notification in self.item_notifications:
            text = notification['text']
            alpha = min(1.0, notification['lifetime'])  # Fade out at the end
            
            # Create surface with alpha
            text_surface = self.small_font.render(text, True, self.colors['text_normal'])
            
            # Position at top left corner
            x = 20
            y = 60 + self.item_notifications.index(notification) * 30
            
            screen.blit(text_surface, (x, y))
    
    def draw_pause_menu(self, screen, is_paused):
        """绘制暂停菜单"""
        if not is_paused:
            return
            
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Menu title
        title_surface = self.large_font.render("暂停", True, self.colors['text_normal'])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        screen.blit(title_surface, title_rect)
        
        # Menu options
        options = ["继续游戏", "重新开始", "退出"]
        for i, option in enumerate(options):
            y_pos = self.screen_height // 2 + i * 60
            option_surface = self.font.render(option, True, self.colors['text_normal'])
            option_rect = option_surface.get_rect(center=(self.screen_width // 2, y_pos))
            screen.blit(option_surface, option_rect)
    
    def draw_death_screen(self, screen, is_dead):
        """绘制死亡界面"""
        if not is_dead:
            return
            
        # Black background
        screen.fill((0, 0, 0))
        
        # Death text
        death_surface = self.large_font.render("死亡", True, self.colors['text_normal'])
        death_rect = death_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        screen.blit(death_surface, death_rect)
        
        # Restart prompt
        restart_surface = self.font.render("按 R 重来", True, self.colors['text_normal'])
        restart_rect = restart_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        screen.blit(restart_surface, restart_rect)
    
    def draw_upgrade_screen(self, screen, player):
        """绘制升级界面"""
        if not getattr(player, 'can_upgrade', False):
            return
            
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Upgrade title
        title_surface = self.large_font.render("升级选择", True, self.colors['text_normal'])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Currency info
        currency_text = f"金币: {player.currency} / 需要: {player.upgrade_cost}"
        currency_surface = self.font.render(currency_text, True, self.colors['text_normal'])
        currency_rect = currency_surface.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(currency_surface, currency_rect)
        
        # Upgrade options
        upgrades = [
            {'key': '1', 'name': '移动速度', 'attr': 'speed', 'value': 0.15, 'color': (100, 200, 255)},
            {'key': '2', 'name': '攻击伤害', 'attr': 'damage', 'value': 0.15, 'color': (255, 100, 100)},
            {'key': '3', 'name': '跳跃高度', 'attr': 'jump', 'value': 0.15, 'color': (100, 255, 100)}
        ]
        
        for i, upgrade in enumerate(upgrades):
            y_pos = 250 + i * 80
            
            # Upgrade box
            box_rect = pygame.Rect(self.screen_width // 2 - 150, y_pos - 25, 300, 60)
            pygame.draw.rect(screen, upgrade['color'], box_rect, border_radius=8)
            pygame.draw.rect(screen, self.colors['text_normal'], box_rect, 2, border_radius=8)
            
            # Upgrade text
            upgrade_text = f"{upgrade['key']} - {upgrade['name']} +{upgrade['value']:.0f}%"
            upgrade_surface = self.font.render(upgrade_text, True, self.colors['text_normal'])
            upgrade_text_rect = upgrade_surface.get_rect(center=(self.screen_width // 2, y_pos))
            screen.blit(upgrade_surface, upgrade_text_rect)
        
        # Instructions
        instructions = self.small_font.render("按数字键选择升级", True, self.colors['info'])
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        screen.blit(instructions, instructions_rect)
    
    def draw_fade_effect(self, screen):
        """绘制淡入淡出效果"""
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, int(self.fade_alpha)))
            screen.blit(fade_surface, (0, 0))
    
    def draw_inventory(self, screen, player, weapon_operon):
        """绘制简化版背包界面"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Inventory title
        title_surface = self.font.render("背包", True, self.colors['text_normal'])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Weapon section
        weapon_title = self.small_font.render("武器", True, self.colors['text_normal'])
        screen.blit(weapon_title, (100, 150))
        
        # Draw weapon slots
        y_offset = 180
        for slot_key, weapon in weapon_operon.slots.items():
            if weapon:
                weapon_text = f"{slot_key}: {weapon.name}"
                weapon_surface = self.small_font.render(weapon_text, True, self.colors['text_normal'])
                screen.blit(weapon_surface, (120, y_offset))
                y_offset += 30
        
        # Currency display
        currency_text = f"金币: {getattr(player, 'currency', 0)}"
        currency_surface = self.small_font.render(currency_text, True, self.colors['text_normal'])
        screen.blit(currency_surface, (100, y_offset + 20))
        
        # Instructions
        instructions = self.small_font.render("按 I 关闭背包", True, self.colors['info'])
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        screen.blit(instructions, instructions_rect)
    
    def draw(self, screen, player, weapon_operon, is_paused=False, is_dead=False, nearby_interactable=None, show_inventory=False):
        """主绘制函数 - 绘制所有UI元素"""
        # Apply screen shake offset
        shake_offset = self.get_screen_shake_offset()
        
        # Create a temporary surface for UI with offset
        ui_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Draw core status (health bar, currency) - get health from player directly
        current_hp = getattr(player, 'current_hp', 100)
        max_hp = getattr(player, 'max_hp', 100)
        
        # Try to get health from combat system if available on player
        if hasattr(player, 'get_health'):
            health_data = player.get_health()
            current_hp = health_data.get('current', current_hp)
            max_hp = health_data.get('max', max_hp)
        
        self.draw_core_status(ui_surface, current_hp, max_hp, getattr(player, 'currency', 0))
        
        # Draw weapon slots
        self.draw_weapon_slots(ui_surface, weapon_operon)
        
        # Draw combat feedback
        self.draw_combat_feedback(ui_surface)
        
        # Draw interaction prompts
        self.draw_interaction_prompts(ui_surface, nearby_interactable)
        
        # Draw item notifications
        self.draw_item_notifications(ui_surface)
        
        # Draw fade effect
        self.draw_fade_effect(ui_surface)
        
        # Apply shake offset and blit to screen
        screen.blit(ui_surface, shake_offset)
        
        # Draw overlays that should not be affected by shake
        self.draw_pause_menu(screen, is_paused)
        self.draw_death_screen(screen, is_dead)
        self.draw_upgrade_screen(screen, player)
        
        # Draw inventory if requested
        if show_inventory:
            self.draw_inventory(screen, player, weapon_operon)