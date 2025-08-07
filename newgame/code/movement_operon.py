import pygame

# --- Constants ---
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_STRENGTH = -12
ROLL_SPEED = 10
ROLL_DURATION = 300 # in milliseconds

class Player:
    """Represents the player character, now with rolling capabilities."""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 64)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        
        # State management
        self.is_rolling = False
        self.roll_timer = 0
        self.roll_direction = 1
        self.is_invincible = False

        # Interaction and progression
        self.last_interaction = None
        self.permanent_upgrades = {
            'speed': 1.0,    # Permanent speed multiplier
            'damage': 1.0,   # Permanent damage multiplier  
            'jump': 1.0     # Permanent jump multiplier
        }
        self.scroll_collected = 0  # Track total scrolls collected
        self.notifications = []  # Store active notifications

        # Visuals
        self.base_color = (173, 216, 230) # Light blue
        self.roll_color = (100, 100, 255) # Blue

    def move(self, direction):
        if not self.is_rolling:
            # Apply permanent speed multiplier
            speed_multiplier = self.get_speed_multiplier()
            self.velocity.x = direction * PLAYER_SPEED * speed_multiplier
            if direction != 0:
                self.roll_direction = direction

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

    def _update_roll_state(self):
        if self.is_rolling:
            if pygame.time.get_ticks() - self.roll_timer > ROLL_DURATION:
                self.is_rolling = False
                self.is_invincible = False
                self.velocity.x = 0

            else:
                # Maintain roll speed but apply some friction/decay
                self.velocity.x *= 0.95

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

    def draw(self, screen, camera_x=0):
        # Adjust player's drawing position based on the camera
        adjusted_rect = self.rect.copy()
        adjusted_rect.x -= camera_x
        
        color = self.roll_color if self.is_rolling else self.base_color
        pygame.draw.rect(screen, color, adjusted_rect)

class MovementOperon:
    """Manages player movement, now including rolling and map collision."""
    def __init__(self, screen_width, screen_height, map_operon=None):
        # The player's starting position is now fixed, relative to the centered map content
        initial_x = 100
        self.player = Player(initial_x, 500)
        self.map_operon = map_operon
        self.platforms = [pygame.Rect(0, screen_height - 40, screen_width, 40)] # Legacy platform

    def update(self, actions):
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
            interact_result = self.map_operon.interact_with_chest_or_scroll_at_position(player_world_pos)
            if interact_result:
                # Store the interaction result for processing by other systems
                self.player.last_interaction = interact_result
                print(f"Player collected {interact_result['type']}")
            else:
                # Try to interact with doors
                self.map_operon.toggle_door_at_position(player_world_pos)
        
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
        
        # Get door collision rects
        door_rects = self.map_operon.get_door_collision_rects()
        collision_rects.extend(door_rects)
        
        return collision_rects

    def draw(self, screen, camera_x=0):
        self.player.draw(screen, camera_x)
