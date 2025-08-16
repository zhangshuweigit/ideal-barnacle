import pygame
import random

class Enemy(pygame.sprite.Sprite):
    """Base class for all enemy types."""
    def __init__(self, x, y, color, size=(30, 50)):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.attack_cooldown = 2000
        self.last_attack_time = 0
        self.is_attacking = False
        self.attack_duration = 0
        self.attack_timer = 0
        self.attack_hitbox = None

    def can_attack(self):
        return pygame.time.get_ticks() - self.last_attack_time > self.attack_cooldown

    def perform_attack(self, player):
        return None

    def update(self, player):
        if self.is_attacking:
            if pygame.time.get_ticks() - self.attack_timer > self.attack_duration:
                self.is_attacking = False
                self.attack_hitbox = None
            else:
                self._update_hitbox(player)

    def _update_hitbox(self, player):
        pass

    def draw(self, screen, camera_x=0):
        # Adjust drawing position based on camera
        adjusted_rect = self.rect.copy()
        adjusted_rect.x -= camera_x
        screen.blit(self.image, adjusted_rect)

    def draw_attack(self, screen, camera_x=0):
        if self.is_attacking and self.attack_hitbox:
            adjusted_hitbox = self.attack_hitbox.copy()
            adjusted_hitbox.x -= camera_x
            pygame.draw.rect(screen, (255, 0, 0, 150), adjusted_hitbox)

class MeleeEnemy(Enemy):
    """Enemy that moves towards the player to attack."""
    def __init__(self, x, y):
        super().__init__(x, y, (255, 100, 100))
        self.speed = 2
        self.attack_range = 50
        self.damage = 10
        self.attack_duration = 300

    def update(self, player):
        super().update(player)
        if not self.is_attacking:
            if self.rect.centerx < player.rect.centerx - 5:
                self.rect.x += self.speed
            elif self.rect.centerx > player.rect.centerx + 5:
                self.rect.x -= self.speed

    def perform_attack(self, player):
        if self.can_attack() and not self.is_attacking and self.rect.colliderect(player.rect.inflate(self.attack_range, self.attack_range)):
            self.last_attack_time = pygame.time.get_ticks()
            self.is_attacking = True
            self.attack_timer = pygame.time.get_ticks()
            direction = pygame.Vector2(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery).normalize()
            return {'type': 'melee', 'damage': self.damage, 'range': self.attack_range, 'direction': direction}
        return None

    def _update_hitbox(self, player):
        direction = 1 if player.rect.centerx > self.rect.centerx else -1
        hitbox_x = self.rect.centerx if direction == 1 else self.rect.centerx - self.attack_range
        self.attack_hitbox = pygame.Rect(hitbox_x, self.rect.centery - 10, self.attack_range, 20)

class RangedEnemy(Enemy):
    """Enemy that keeps a distance and shoots projectiles."""
    def __init__(self, x, y):
        super().__init__(x, y, (100, 255, 100))
        self.speed = 1
        self.optimal_distance = 250
        self.damage = 5

    def update(self, player):
        super().update(player)
        if not self.is_attacking:
            distance = self.rect.centerx - player.rect.centerx
            if abs(distance) < self.optimal_distance - 20:
                self.rect.x += self.speed if distance > 0 else -self.speed
            elif abs(distance) > self.optimal_distance + 20:
                self.rect.x -= self.speed if distance > 0 else -self.speed
            
    def perform_attack(self, player):
        if self.can_attack() and not self.is_attacking:
            self.last_attack_time = pygame.time.get_ticks()
            
            # Calculate the precise direction vector towards the player
            player_pos = pygame.Vector2(player.rect.center)
            enemy_pos = pygame.Vector2(self.rect.center)
            direction = (player_pos - enemy_pos).normalize() if (player_pos - enemy_pos).length() > 0 else pygame.Vector2(1, 0)

            return {'type': 'projectile', 'damage': self.damage, 'speed': 8, 'direction': direction}
        return None

class ShieldEnemy(Enemy):
    """Enemy with a shield that blocks attacks."""
    def __init__(self, x, y):
        super().__init__(x, y, (100, 100, 255), size=(50, 50))
        self.is_shielding = False

    def update(self, player):
        super().update(player)
        if not self.is_attacking:
            if random.random() < 0.01:
                self.is_shielding = not self.is_shielding
            
            if self.is_shielding:
                self.image.fill((50, 50, 150))
            else:
                self.image.fill((100, 100, 255))