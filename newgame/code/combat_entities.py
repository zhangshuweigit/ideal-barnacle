import pygame

class Projectile(pygame.sprite.Sprite):
    """Represents a projectile (e.g., an arrow) that moves in a straight line."""
    def __init__(self, x, y, direction_vector, speed, damage, owner):
        super().__init__()
        self.original_image = pygame.Surface((15, 5), pygame.SRCALPHA)
        self.original_image.fill((200, 200, 200))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        
        self.pos = pygame.Vector2(x, y)
        
        # Ensure the direction vector is normalized
        if direction_vector.length() > 0:
            self.velocity = direction_vector.normalize() * speed
        else:
            # Default to moving right if direction is a zero vector
            self.velocity = pygame.Vector2(speed, 0)

        self.damage = damage
        self.owner = owner

        # Rotate image to match direction
        angle = self.velocity.angle_to(pygame.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.original_image, -angle)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        """Move the projectile in a straight line without gravity."""
        self.pos += self.velocity
        self.rect.center = self.pos

class TimedEffect(pygame.sprite.Sprite):
    """A visual effect that disappears after a duration, like an explosion MAGIC."""
    def __init__(self, x, y, size, duration, color=(255, 0, 0)):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.image.set_alpha(150)
        self.rect = self.image.get_rect(center=(x, y))
        self.spawn_time = pygame.time.get_ticks()
        self.duration = duration

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()