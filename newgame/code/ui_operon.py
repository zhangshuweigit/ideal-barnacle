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

    def draw_upgrades(self, screen, player):
        """
        绘制玩家的永久升级信息。
        """
        if hasattr(player, 'permanent_upgrades'):
            upgrades = player.permanent_upgrades
            scroll_count = getattr(player, 'scroll_collected', 0)
            
            # Starting position for upgrade display
            start_x = 10
            start_y = 60
            line_height = 25
            
            # Draw scroll count
            scroll_text = self.font.render(f"Scrolls: {scroll_count}", True, (255, 255, 255))
            screen.blit(scroll_text, (start_x, start_y))
            
            # Draw upgrade information
            upgrade_y = start_y + line_height
            
            for upgrade_type, value in upgrades.items():
                if value != 1.0:  # Only show if different from base value
                    # Format upgrade type for display
                    display_names = {
                        'speed': 'Speed',
                        'damage': 'Damage', 
                        'jump': 'Jump'
                    }
                    display_name = display_names.get(upgrade_type, upgrade_type.title())
                    
                    # Calculate percentage increase
                    percent_increase = (value - 1.0) * 100
                    
                    # Choose color based on upgrade type
                    colors = {
                        'speed': (100, 200, 255),    # Light blue
                        'damage': (255, 100, 100),   # Light red
                        'jump': (100, 255, 100)     # Light green
                    }
                    color = colors.get(upgrade_type, (255, 255, 255))
                    
                    # Render upgrade text
                    upgrade_text = self.font.render(f"{display_name}: +{percent_increase:.0f}%", True, color)
                    screen.blit(upgrade_text, (start_x, upgrade_y))
                    
                    upgrade_y += line_height

    def draw_notifications(self, screen, player):
        """
        绘制玩家的通知。
        """
        if hasattr(player, 'notifications') and player.notifications:
            screen_width, screen_height = screen.get_size()
            
            for i, notification in enumerate(player.notifications):
                # Calculate position (center top of screen)
                text = notification['text']
                color = notification['color']
                
                # Create text surface
                text_surface = self.font.render(text, True, color)
                text_rect = text_surface.get_rect()
                
                # Center horizontally, position from top
                text_rect.centerx = screen_width // 2
                text_rect.y = 20 + i * 30
                
                # Draw text with shadow for better visibility
                shadow_offset = 2
                shadow_surface = self.font.render(text, True, (0, 0, 0))
                shadow_rect = shadow_surface.get_rect()
                shadow_rect.x = text_rect.x + shadow_offset
                shadow_rect.y = text_rect.y + shadow_offset
                screen.blit(shadow_surface, shadow_rect)
                
                screen.blit(text_surface, text_rect)

    def draw_skill_info(self, screen, weapon_operon):
        """
        绘制技能冷却和药水数量信息。
        """
        current_time = pygame.time.get_ticks()
        start_x = 10
        start_y = screen.get_height() - 100
        line_height = 25
        
        # Draw Bomb (sub_1) cooldown
        if 'sub_1' in weapon_operon.skill_cooldowns:
            cooldown_end = weapon_operon.skill_cooldowns['sub_1']
            if current_time < cooldown_end:
                remaining_time = (cooldown_end - current_time) / 1000  # Convert to seconds
                text = f"Bomb CD: {remaining_time:.1f}s"
                color = (255, 100, 100)  # Red when on cooldown
            else:
                text = "Bomb: Ready"
                color = (100, 255, 100)  # Green when ready
            
            cooldown_surface = self.font.render(text, True, color)
            screen.blit(cooldown_surface, (start_x, start_y))
            start_y += line_height
        
        # Draw HealPotion (sub_2) uses
        if 'sub_2' in weapon_operon.slots:
            heal_potion = weapon_operon.slots['sub_2']
            if hasattr(heal_potion, 'uses_remaining'):
                uses = heal_potion.uses_remaining
                max_uses = heal_potion.max_uses
                text = f"Heal Potions: {uses}/{max_uses}"
                
                # Color based on remaining uses
                if uses == 0:
                    color = (255, 100, 100)  # Red when empty
                elif uses <= max_uses // 3:
                    color = (255, 255, 100)  # Yellow when low
                else:
                    color = (100, 255, 100)  # Green when plenty
                
                potion_surface = self.font.render(text, True, color)
                screen.blit(potion_surface, (start_x, start_y))
