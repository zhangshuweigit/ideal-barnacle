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

        # Visuals
        self.base_color = (173, 216, 230) # Light blue
        self.roll_color = (100, 100, 255) # Blue

    def move(self, direction):
        if not self.is_rolling:
            self.velocity.x = direction * PLAYER_SPEED
            if direction != 0:
                self.roll_direction = direction

    def jump(self):
        if self.on_ground and not self.is_rolling:
            self.velocity.y = JUMP_STRENGTH

    def roll(self):
        if not self.is_rolling:
            self.is_rolling = True
            self.is_invincible = True
            self.roll_timer = pygame.time.get_ticks()
            self.velocity.x = self.roll_direction * ROLL_SPEED

    def update_state(self):
        self._update_roll_state()

    def update_physics(self, platforms):
        
        if not self.is_rolling:
            self.velocity.y += GRAVITY
            if self.velocity.y > 10: self.velocity.y = 10
        
        self.rect.x += self.velocity.x
        # X-axis collision logic would go here
        
        self.rect.y += self.velocity.y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform) and self.velocity.y > 0:
                self.rect.bottom = platform.top
                self.velocity.y = 0
                self.on_ground = True

    def _update_roll_state(self):
        if self.is_rolling:
            if pygame.time.get_ticks() - self.roll_timer > ROLL_DURATION:
                self.is_rolling = False
                self.is_invincible = False
                self.velocity.x = 0

            else:
                # Maintain roll speed but apply some friction/decay
                self.velocity.x *= 0.95 

    def draw(self, screen):
        color = self.roll_color if self.is_rolling else self.base_color
        pygame.draw.rect(screen, color, self.rect)

class MovementOperon:
    """Manages player movement, now including rolling."""
    def __init__(self, screen_width, screen_height):
        self.player = Player(100, 500)
        self.platforms = [pygame.Rect(0, screen_height - 40, screen_width, 40)]

    def update(self, actions):
        if actions.get('roll'):
            self.player.roll()

        self.player.update_state()

        # Movement inputs are ignored during roll
        if not self.player.is_rolling:
            self.player.move(actions.get('move_dir', 0))
            if actions.get('jump'):
                self.player.jump()
        
        self.player.update_physics(self.platforms)

    def draw(self, screen):
        self.player.draw(screen)
        for platform in self.platforms:
            pygame.draw.rect(screen, (100, 100, 100), platform)
