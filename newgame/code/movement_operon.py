import pygame
import os

# --- Constants ---
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_STRENGTH = -12
ROLL_SPEED = 10
ROLL_DURATION = 300 # in milliseconds

# Animation imports
from code.simple_animation import SimpleFrameAnimation
from code.shooting_animation import ShootingAnimation

class Player:
    """Represents the player character, now with rolling capabilities."""
    def __init__(self, x, y):
        # Collision rectangle (maintain original size for physics)
        self.rect = pygame.Rect(x, y, 32, 64)
        # Visual rectangle (for drawing animations)
        self.visual_rect = pygame.Rect(x, y, 96, 128)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False

        # State management
        self.is_rolling = False
        self.roll_timer = 0
        self.roll_direction = 1
        self.is_invincible = False

        # Death state
        self.is_dead = False
        self.death_timer = 0
        self.death_duration = 2000  # 2 seconds death animation
        self.death_animation_progress = 0

        # Interaction and progression
        self.last_interaction = None
        self.permanent_upgrades = {
            'speed': 1.0,    # Permanent speed multiplier
            'damage': 1.0,   # Permanent damage multiplier
            'jump': 1.0     # Permanent jump multiplier
        }
        self.scroll_collected = 0  # Track total scrolls collected
        self.currency = 0  # Player's currency
        self.upgrade_level = 1  # Current upgrade level
        self.upgrade_cost = 500  # Initial upgrade cost (increases by 500 each time)
        self.can_upgrade = False  # Flag to show upgrade option
        self.notifications = []  # Store active notifications

        # Animation system
        try:
            self.animation_system = SimpleFrameAnimation("12")
            if self.animation_system.get_frame_count() > 0:
                self.animation_system.play()
                print("Simple animation system initialized and playing")
            else:
                print("Failed to load animation frames")
                self.animation_system = None
        except Exception as e:
            print(f"Failed to initialize simple animation system: {e}")
            self.animation_system = None

        # 初始化射击动画系统
        try:
            self.shooting_animation = ShootingAnimation("13")
            print("Shooting animation system initialized")
        except Exception as e:
            print(f"Failed to initialize shooting animation system: {e}")
            self.shooting_animation = None

        self.facing_direction = 1  # 1 for right, -1 for left

  # 移除了射击状态相关变量

        # Visuals
        self.base_color = (173, 216, 230) # Light blue
        self.roll_color = (100, 100, 255) # Blue

    def move(self, direction):
        # 如果正在播放射击动画，不能移动
        if self.shooting_animation and self.shooting_animation.is_playing():
            self.velocity.x = 0
            return

        if not self.is_rolling:
            # Apply permanent speed multiplier
            speed_multiplier = self.get_speed_multiplier()
            self.velocity.x = direction * PLAYER_SPEED * speed_multiplier
            if direction != 0:
                self.roll_direction = direction
                self.facing_direction = direction  # Update facing direction for animation

    def update_visual_rect(self):
        """Update visual rectangle position to match collision rectangle."""
        self.visual_rect.centerx = self.rect.centerx
        self.visual_rect.bottom = self.rect.bottom

    def jump(self):
        if self.on_ground and not self.is_rolling:
            # Apply permanent jump multiplier
            jump_multiplier = self.get_jump_multiplier()
            self.velocity.y = JUMP_STRENGTH * jump_multiplier

    def roll(self):
        if not self.is_rolling:
            # We can add a check here to disable roll in edit mode if needed
            self.is_rolling = True
            self.is_invincible = True
            self.roll_timer = pygame.time.get_ticks()
            self.velocity.x = self.roll_direction * ROLL_SPEED

    def update_state(self):
        self._update_roll_state()

        # Update animation system
        if self.animation_system:
            is_moving = abs(self.velocity.x) > 0.1 and not self.is_rolling
            if is_moving:
                # 角色在移动，确保动画播放
                if not self.animation_system.is_playing:
                    self.animation_system.play()
            else:
                # 角色停止，停止动画播放
                if self.animation_system.is_playing:
                    self.animation_system.stop()
            # 无论是否移动都更新动画，以保持在当前帧
            self.animation_system.update()

        # Update shooting animation
        self.update_shooting_animation()

    def update_physics(self, platforms):
        # Apply gravity only when not rolling
        if not self.is_rolling:
            self.velocity.y += GRAVITY
            if self.velocity.y > 10: self.velocity.y = 10

        # --- Horizontal Collision ---
        self.rect.x += self.velocity.x
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity.x > 0: # Moving right
                    self.rect.right = platform.left
                elif self.velocity.x < 0: # Moving left
                    self.rect.left = platform.right

        # --- Vertical Collision ---
        self.rect.y += self.velocity.y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity.y > 0: # Moving down
                    self.rect.bottom = platform.top
                    self.velocity.y = 0
                    self.on_ground = True
                elif self.velocity.y < 0: # Moving up
                    self.rect.top = platform.bottom
                    self.velocity.y = 0

        # Update visual rectangle to match collision rectangle
        self.update_visual_rect()

    def _update_roll_state(self):
        if self.is_rolling:
            if pygame.time.get_ticks() - self.roll_timer > ROLL_DURATION:
                self.is_rolling = False
                self.is_invincible = False
                self.velocity.x = 0

            else:
                # Maintain roll speed but apply some friction/decay
                self.velocity.x *= 0.95

    def start_ranged_attack(self, direction=1):
        """开始远程攻击，触发射击动画"""
        if self.shooting_animation:
            self.shooting_animation.start_shooting(direction)

    def update_shooting_animation(self):
        """更新射击动画状态"""
        if self.shooting_animation:
            self.shooting_animation.update()

    def add_permanent_upgrade(self, upgrade_type, value):
        """Add a permanent upgrade to the player."""
        old_value = self.permanent_upgrades[upgrade_type]
        self.permanent_upgrades[upgrade_type] += value
        self.scroll_collected += 1
        
        # Add notification
        display_names = {
            'speed': 'Speed',
            'damage': 'Damage', 
            'jump': 'Jump'
        }
        display_name = display_names.get(upgrade_type, upgrade_type.title())
        percent_increase = value * 100
        total_percent = (self.permanent_upgrades[upgrade_type] - 1.0) * 100
        
        notification = {
            'text': f"+{display_name} +{percent_increase:.0f}% (Total: +{total_percent:.0f}%)",
            'start_time': pygame.time.get_ticks(),
            'duration': 4000,  # Show for 4 seconds
            'color': {
                'speed': (100, 200, 255),    # Light blue
                'damage': (255, 100, 100),   # Light red
                'jump': (100, 255, 100)     # Light green
            }.get(upgrade_type, (255, 255, 255))
        }
        self.notifications.append(notification)
        
        print(f"Player received permanent {upgrade_type} upgrade: +{value:.2f} (total: {self.permanent_upgrades[upgrade_type]:.2f}x)")

    def add_currency(self, amount):
        """Add currency to the player."""
        self.currency += amount
        print(f"Player received {amount} currency. Total: {self.currency}")
        
        # Check if player can afford upgrade
        self.check_upgrade_available()
    
    def check_upgrade_available(self):
        """Check if player has enough currency for upgrade."""
        if self.currency >= self.upgrade_cost:
            self.can_upgrade = True
            print(f"Upgrade available! Cost: {self.upgrade_cost}, Currency: {self.currency}")
        else:
            self.can_upgrade = False
    
    def spend_currency_on_upgrade(self):
        """Spend currency for upgrade and increase upgrade cost."""
        if self.currency >= self.upgrade_cost:
            self.currency -= self.upgrade_cost
            self.upgrade_level += 1
            self.upgrade_cost = 500 * self.upgrade_level  # 500, 1000, 1500, 2000...
            self.can_upgrade = False
            print(f"Upgrade purchased! New upgrade cost: {self.upgrade_cost}")
            return True
        return False
    
    def upgrade_attribute(self, attribute_type, value):
        """Upgrade a specific attribute by given value."""
        if attribute_type in self.permanent_upgrades:
            old_value = self.permanent_upgrades[attribute_type]
            self.permanent_upgrades[attribute_type] += value
            self.scroll_collected += 1  # Also count manual upgrades as scrolls
            
            # Add notification
            display_names = {
                'speed': 'Speed',
                'damage': 'Damage', 
                'jump': 'Jump'
            }
            display_name = display_names.get(attribute_type, attribute_type.title())
            total_percent = (self.permanent_upgrades[attribute_type] - 1.0) * 100
            
            notification = {
                'text': f"{display_name} 升级 +{value:.2f}! (总计: +{total_percent:.0f}%)",
                'start_time': pygame.time.get_ticks(),
                'duration': 4000,  # Show for 4 seconds
                'color': {
                    'speed': (100, 200, 255),    # Light blue
                    'damage': (255, 100, 100),   # Light red
                    'jump': (100, 255, 100)     # Light green
                }.get(attribute_type, (255, 255, 0))  # Gold for unknown
            }
            self.notifications.append(notification)
            
            print(f"Upgraded {attribute_type} by {value:.2f} (total: {self.permanent_upgrades[attribute_type]:.2f}x)")
    
    def save_currency(self, save_slot=None, weapon_operon=None):
        """Save player currency to file."""
        import json
        save_data = {
            'currency': self.currency,
            'permanent_upgrades': self.permanent_upgrades,
            'upgrade_level': self.upgrade_level,
            'upgrade_cost': self.upgrade_cost,
            'position': {
                'x': self.rect.x,
                'y': self.rect.y
            },
            'scroll_collected': self.scroll_collected
        }
        
        # Save weapon data if weapon_operon is provided
        if weapon_operon:
            save_data['weapons'] = weapon_operon.get_weapon_data()
        
        # Determine filename based on save slot
        filename = f'save_{save_slot}.json' if save_slot is not None else 'player_save.json'
        try:
            with open(filename, 'w') as f:
                json.dump(save_data, f)
            print(f"Saved player data to {filename}: currency={self.currency}, pos=({self.rect.x}, {self.rect.y})")
        except Exception as e:
            print(f"Failed to save currency: {e}")
    
    def load_currency(self, save_slot=None, weapon_operon=None):
        """Load player currency from file."""
        import json
        # Determine filename based on save slot
        filename = f'save_{save_slot}.json' if save_slot is not None else 'player_save.json'
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            self.currency = save_data.get('currency', 0)
            
            # Load upgrade system data
            self.upgrade_level = save_data.get('upgrade_level', 1)
            self.upgrade_cost = save_data.get('upgrade_cost', 500)
            self.scroll_collected = save_data.get('scroll_collected', 0)
            
            # Load permanent upgrades if available
            if 'permanent_upgrades' in save_data:
                self.permanent_upgrades.update(save_data['permanent_upgrades'])
            
            # Load player position if available
            if 'position' in save_data:
                pos = save_data['position']
                self.rect.x = pos.get('x', 100)
                self.rect.y = pos.get('y', 500)
            
            # Load weapon data if available and weapon_operon is provided
            if 'weapons' in save_data and weapon_operon:
                weapon_operon.load_weapon_data(save_data['weapons'])
            
            # Check if upgrade is available after loading
            self.check_upgrade_available()
            
            print(f"Loaded player data from {filename}: currency={self.currency}, pos=({self.rect.x}, {self.rect.y})")
            return True
        except FileNotFoundError:
            print(f"No save file {filename} found, starting with default values")
            return False
        except Exception as e:
            print(f"Failed to load currency: {e}")
            return False

    def update_notifications(self):
        """Update and remove expired notifications."""
        current_time = pygame.time.get_ticks()
        self.notifications = [
            notif for notif in self.notifications 
            if current_time - notif['start_time'] < notif['duration']
        ]

    def get_speed_multiplier(self):
        """Get the current speed multiplier from permanent upgrades."""
        return self.permanent_upgrades['speed']

    def get_jump_multiplier(self):
        """Get the current jump multiplier from permanent upgrades."""
        return self.permanent_upgrades['jump']

    def get_damage_multiplier(self):
        """Get the current damage multiplier from permanent upgrades."""
        return self.permanent_upgrades['damage'] 

    def trigger_death(self):
        """Trigger death state and animation"""
        if not self.is_dead:
            self.is_dead = True
            self.death_timer = pygame.time.get_ticks()
            self.death_animation_progress = 0
            self.velocity = pygame.Vector2(0, 0)

    def update_death_state(self):
        """Update death animation state"""
        if self.is_dead:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.death_timer
            self.death_animation_progress = min(1.0, elapsed / self.death_duration)

    def get_health(self):
        """Get health data from combat system if available"""
        # This will be populated by the combat system reference
        if hasattr(self, '_combat_operon') and self._combat_operon:
            health_system = self._combat_operon.health_systems.get(self)
            if health_system:
                return {
                    'current': health_system.current_hp,
                    'max': health_system.max_hp
                }
        # Default health values
        return {'current': 100, 'max': 100}

    def respawn(self, spawn_x=100, spawn_y=500):
        """Respawn player at given position"""
        self.rect.x = spawn_x
        self.rect.y = spawn_y
        self.velocity = pygame.Vector2(0, 0)
        self.is_dead = False
        self.death_timer = 0
        self.death_animation_progress = 0
        self.is_rolling = False
        self.is_invincible = False
        self.on_ground = False

    def draw(self, screen, camera_x=0):
        # Adjust player's drawing position based on the camera
        adjusted_collision_rect = self.rect.copy()
        adjusted_collision_rect.x -= camera_x
        adjusted_visual_rect = self.visual_rect.copy()
        adjusted_visual_rect.x -= camera_x

        if self.is_dead:
            # Death animation: gradually fade and fall
            alpha = 1.0 - self.death_animation_progress
            fall_offset = int(self.death_animation_progress * 20)

            # Calculate color with fade effect
            fade_color = tuple(int(c * alpha) for c in self.base_color)

            # Draw falling/fading rectangle
            death_rect = adjusted_visual_rect.copy()
            death_rect.y += fall_offset

            # Create surface with alpha for transparency
            death_surface = pygame.Surface((death_rect.width, death_rect.height), pygame.SRCALPHA)
            death_surface.fill((*fade_color, int(255 * alpha)))
            screen.blit(death_surface, death_rect)
        else:
            # Use animation if available, otherwise use colored rectangle
            # 优先显示射击动画
            if self.shooting_animation and self.shooting_animation.is_playing():
                frame = self.shooting_animation.get_current_frame(self.facing_direction)
                if frame:
                    # Position frame at the center of the visual rect
                    frame_rect = frame.get_rect()
                    frame_rect.centerx = adjusted_visual_rect.centerx
                    frame_rect.centery = adjusted_visual_rect.centery
                    screen.blit(frame, frame_rect)
            elif self.animation_system:
                frame = self.animation_system.get_current_frame(self.facing_direction)
                if frame:
                    # Position frame at the center of the visual rect for better visibility
                    frame_rect = frame.get_rect()
                    frame_rect.centerx = adjusted_visual_rect.centerx
                    frame_rect.centery = adjusted_visual_rect.centery  # 居中显示
                    screen.blit(frame, frame_rect)
                else:
                    # Fallback to colored rectangle using visual rect
                    color = self.roll_color if self.is_rolling else self.base_color
                    pygame.draw.rect(screen, color, adjusted_visual_rect)
            else:
                # Fallback to colored rectangle using collision rect
                color = self.roll_color if self.is_rolling else self.base_color
                pygame.draw.rect(screen, color, adjusted_collision_rect)

class MovementOperon:
    """Manages player movement, now including rolling and map collision."""
    def __init__(self, screen_width, screen_height, map_operon=None, interact_point_operon=None):
        # The player's starting position is now fixed, relative to the centered map content
        initial_x = 100
        self.player = Player(initial_x, 500)
        self.map_operon = map_operon
        self.interact_point_operon = interact_point_operon
        self.platforms = [pygame.Rect(0, screen_height - 40, screen_width, 40)] # Legacy platform

    def update(self, actions):
        # Update death state and animation
        self.player.update_death_state()
        
        # Don't process normal updates if player is dead
        if self.player.is_dead:
            return
        
        if actions.get('roll'):
            self.player.roll()

        self.player.update_state()
        self.player.update_notifications()
        
        if not self.player.is_rolling:
            self.player.move(actions.get('move_dir', 0))
            if actions.get('jump'):
                self.player.jump()
        
        # Handle interactions
        if actions.get('interact') and self.map_operon:
            player_world_pos = (self.player.rect.centerx, self.player.rect.centery)
            
            # Try to interact with chest/scroll first
            if self.interact_point_operon:
                interact_result = self.interact_point_operon.interact_with_chest_or_scroll_at_position(player_world_pos)
                if interact_result:
                    # Store the interaction result for processing by other systems
                    self.player.last_interaction = interact_result
                    print(f"Player collected {interact_result['type']}")
                else:
                    # Try to interact with doors
                    self.interact_point_operon.toggle_door_at_position(player_world_pos)
        
        # Use map for collision detection
        self.player.update_physics(self.get_collision_rects())

    def get_collision_rects(self):
        """Get all collision tiles from the map around the player."""
        if not self.map_operon:
            return self.platforms # Fallback to default platform
        
        collision_rects = []
        player_gx = int(self.player.rect.centerx // self.map_operon.tile_size)
        player_gy = int(self.player.rect.centery // self.map_operon.tile_size)

        # Get tile collision rects
        for x_offset in range(-2, 3):
            for y_offset in range(-2, 3):
                world_x = (player_gx + x_offset) * self.map_operon.tile_size
                world_y = (player_gy + y_offset) * self.map_operon.tile_size
                
                tile_type = self.map_operon.get_tile(world_x, world_y)
                if tile_type == 1: # COLLISION tile
                    collision_rects.append(pygame.Rect(world_x, world_y, self.map_operon.tile_size, self.map_operon.tile_size))
        
        # Get door collision rects from the interact point operon if available
        if self.interact_point_operon:
            door_rects = self.interact_point_operon.get_door_collision_rects()
            collision_rects.extend(door_rects)
        
        return collision_rects

    def respawn_player(self, spawn_x=100, spawn_y=500):
        """Respawn player at specified position"""
        self.player.respawn(spawn_x, spawn_y)
        # Reset camera to follow respawned player
        return spawn_x

    def draw(self, screen, camera_x=0):
        self.player.draw(screen, camera_x)
