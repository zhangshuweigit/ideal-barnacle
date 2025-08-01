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
    """A visual effect that disappears after a duration, like an explosion."""
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

class HealthSystem:
    """Manages health for a game entity."""
    def __init__(self, max_hp):
        self.max_hp = max_hp
        self.current_hp = max_hp

    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp < 0:
            self.current_hp = 0

    def is_dead(self):
        return self.current_hp <= 0

class CombatOperon:
    """Handles all combat-related logic."""
    def __init__(self):
        self.health_systems = {}
        self.projectiles = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()

    def register_entity(self, entity, max_hp):
        if entity not in self.health_systems:
            self.health_systems[entity] = HealthSystem(max_hp)

    def process_attack(self, attack_data, all_entities, attacker):
        if not attack_data:
            return

        attack_type = attack_data.get('type')
        direction = attack_data.get('direction', 1)

        if attack_type == 'melee':
            hitbox_range = attack_data.get('range', 60)
            
            direction_vector = attack_data.get('direction', pygame.Vector2(1, 0))
            if not isinstance(direction_vector, pygame.Vector2):
                direction_vector = pygame.Vector2(direction_vector, 0)
            if direction_vector.length() == 0:
                direction_vector = pygame.Vector2(1, 0)
            else:
                direction_vector.normalize_ip()

            hitbox_start_pos = pygame.Vector2(attacker.rect.center) + direction_vector * 10 
            
            hitbox_size = (hitbox_range, 40)
            hitbox_surface = pygame.Surface(hitbox_size, pygame.SRCALPHA)
            hitbox_rect = hitbox_surface.get_rect(center=hitbox_start_pos + direction_vector * (hitbox_range / 2))
            
            for entity in all_entities:
                if entity is not attacker and hitbox_rect.colliderect(entity.rect):
                    self.apply_damage(entity, attack_data['damage'])
        
        elif attack_type == 'projectile':
            px, py = attacker.rect.center
            direction_vector = attack_data.get('direction', pygame.Vector2(1, 0))
            proj = Projectile(px, py, direction_vector, attack_data['speed'], attack_data['damage'], attacker)
            self.projectiles.add(proj)
        
        elif attack_type == 'effect':
            effect_type = attack_data.get('effect_type')
            if effect_type == 'explosion':
                pos = attacker.rect.center
                explosion = TimedEffect(pos[0], pos[1], attack_data['radius'] * 2, attack_data['duration'], attack_data['color'])
                self.effects.add(explosion)
                for entity in all_entities:
                    if entity is not attacker and explosion.rect.colliderect(entity.rect):
                        self.apply_damage(entity, attack_data['damage'])
            elif effect_type == 'heal':
                self.apply_heal(attacker, attack_data['amount'])

    def update(self, all_entities, camera_x=0):
        self.projectiles.update()
        self.effects.update()
        
        # Correctly define the screen rectangle for culling
        screen_rect = pygame.display.get_surface().get_rect()
        screen_rect.x += camera_x

        for proj in self.projectiles:
            # The projectile's rect is in world coordinates.
            # We check if it's outside the camera's view.
            if not screen_rect.colliderect(proj.rect):
                proj.kill()
                continue
            
            for entity in all_entities:
                if entity is not proj.owner and proj.rect.colliderect(entity.rect):
                    self.apply_damage(entity, proj.damage)
                    proj.kill()
                    break

    def draw(self, screen, camera_x=0):
        # Adjust projectile and effect positions for camera
        for proj in self.projectiles:
            adjusted_rect = proj.rect.copy()
            adjusted_rect.x -= camera_x
            screen.blit(proj.image, adjusted_rect)
        for effect in self.effects:
            adjusted_rect = effect.rect.copy()
            adjusted_rect.x -= camera_x
            screen.blit(effect.image, adjusted_rect)

    def apply_damage(self, target_entity, damage):
        # Check for invincibility frames before applying damage
        if getattr(target_entity, 'is_invincible', False):
            return

        if target_entity in self.health_systems:
            health = self.health_systems[target_entity]
            health.take_damage(damage)
            if health.is_dead():
                if hasattr(target_entity, 'kill'): target_entity.kill()
                self.health_systems.pop(target_entity, None)
    
    def apply_heal(self, target_entity, amount):
        if target_entity in self.health_systems:
            health = self.health_systems[target_entity]
            health.current_hp = min(health.max_hp, health.current_hp + amount)
