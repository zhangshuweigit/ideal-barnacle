import pygame

class Projectile(pygame.sprite.Sprite):
    """Represents a projectile (e.g., an arrow)."""
    def __init__(self, x, y, direction, speed, damage, owner):
        super().__init__()
        self.image = pygame.Surface((15, 5))
        self.image.fill((200, 200, 200))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed * direction
        self.damage = damage
        self.owner = owner

    def update(self):
        self.rect.x += self.speed

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
            hitbox_x = attacker.rect.centerx if direction == 1 else attacker.rect.centerx - hitbox_range
            hitbox = pygame.Rect(hitbox_x, attacker.rect.centery - 20, hitbox_range, 40)
            for entity in all_entities:
                if entity is not attacker and hitbox.colliderect(entity.rect):
                    self.apply_damage(entity, attack_data['damage'])
        
        elif attack_type == 'projectile':
            px, py = attacker.rect.center
            proj = Projectile(px, py, direction, attack_data['speed'], attack_data['damage'], attacker)
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

    def update(self, all_entities):
        self.projectiles.update()
        self.effects.update()
        for proj in self.projectiles:
            if not pygame.display.get_surface().get_rect().colliderect(proj.rect):
                proj.kill()
                continue
            for entity in all_entities:
                if entity is not proj.owner and proj.rect.colliderect(entity.rect):
                    self.apply_damage(entity, proj.damage)
                    proj.kill()
                    break

    def draw(self, screen):
        self.projectiles.draw(screen)
        self.effects.draw(screen)

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
