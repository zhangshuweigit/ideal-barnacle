import pygame

class Weapon:
    """Base class for all weapons."""
    def __init__(self, name, damage):
        self.name = name
        self.damage = damage

class BasicSword(Weapon):
    """A simple sword weapon."""
    def __init__(self):
        super().__init__("Basic Sword", 10)

    def normal_attack(self):
        return {'type': 'melee', 'damage': self.damage, 'range': 60, 'duration': 200, 'color': (255, 255, 0)}

    def skill_attack(self):
        return {'type': 'melee', 'damage': self.damage * 5, 'range': 90, 'duration': 400, 'color': (255, 100, 0)}

class BasicBow(Weapon):
    """A simple bow weapon."""
    def __init__(self):
        super().__init__("Basic Bow", 8)

    def normal_attack(self):
        return {'type': 'projectile', 'damage': self.damage, 'speed': 10}

    def skill_attack(self):
        return {'type': 'projectile', 'damage': self.damage * 1.5, 'speed': 15, 'piercing': True}

class Bomb(Weapon):
    """A sub-weapon that creates an explosion."""
    def __init__(self):
        super().__init__("Bomb", 25)

    def normal_attack(self):
        return {'type': 'effect', 'effect_type': 'explosion', 'radius': 100, 'duration': 250, 'damage': self.damage, 'color': (255, 120, 0)}

class HealPotion(Weapon):
    """A sub-weapon that heals the player."""
    def __init__(self):
        super().__init__("Heal Potion", 0)

    def normal_attack(self):
        return {'type': 'effect', 'effect_type': 'heal', 'amount': 20}

class WeaponOperon:
    """武器操纵子 - 管理4个武器槽位。"""
    def __init__(self):
        self.slots = {
            'main_1': BasicSword(),
            'main_2': BasicBow(),
            'sub_1': Bomb(),
            'sub_2': HealPotion()
        }
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 0
        self.attack_hitbox = None
        self.attack_direction = 1
        self.attack_color = (255, 255, 0)
        self.attack_range = 0

    def attack(self, actions):
        """Processes attack actions based on the new input system."""
        if self.is_attacking or not actions.get('active_slot'):
            return None

        slot = actions.get('active_slot')
        is_skill = actions.get('is_skill', False)
        
        weapon = self.slots.get(slot)
        if not weapon:
            return None
        
        if 'sub' in slot and is_skill:
             return None

        attack_data = weapon.skill_attack() if is_skill else weapon.normal_attack()
        
        if attack_data:
            attack_type = attack_data.get('type')
            
            direction = 1
            if actions.get('mouse_pos') and actions.get('player_pos'):
                mouse_x, _ = actions['mouse_pos']
                player_center_x, _ = actions['player_pos']
                direction = 1 if mouse_x > player_center_x else -1
            attack_data['direction'] = direction
            
            if attack_type == 'melee':
                self.is_attacking = True
                self.attack_duration = attack_data.get('duration', 200)
                self.attack_color = attack_data.get('color', (255, 255, 0))
                self.attack_range = attack_data.get('range', 60)
                self.attack_direction = direction
                self.attack_timer = pygame.time.get_ticks()
        
        return attack_data

    def update(self, player_rect, mouse_pos):
        """Update melee attack animation state."""
        if self.is_attacking:
            if pygame.time.get_ticks() - self.attack_timer > self.attack_duration:
                self.is_attacking = False
                self.attack_hitbox = None
            else:
                hitbox_x = player_rect.centerx if self.attack_direction == 1 else player_rect.centerx - self.attack_range
                self.attack_hitbox = pygame.Rect(hitbox_x, player_rect.centery - 20, self.attack_range, 40)
            
    def draw(self, screen):
        """Draw the visual representation of the melee attack."""
        if self.is_attacking and self.attack_hitbox:
            pygame.draw.rect(screen, self.attack_color, self.attack_hitbox)
