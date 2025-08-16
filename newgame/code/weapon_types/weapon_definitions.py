import pygame

class Weapon:
    """武器的基类，定义通用属性。"""
    def __init__(self, name, damage):
        self.name = name
        self.damage = damage

class BasicSword(Weapon):
    """基础近战武器：剑。"""
    def __init__(self):
        super().__init__("Basic Sword", 10)

    def normal_attack(self):
        return {'type': 'melee', 'damage': self.damage, 'range': 60, 'duration': 200, 'color': (255, 255, 0)}

    def skill_attack(self):
        return {'type': 'melee', 'damage': self.damage * 5, 'range': 90, 'duration': 400, 'color': (255, 100, 0)}

class BasicBow(Weapon):
    """基础远程武器：弓。"""
    def __init__(self):
        super().__init__("Basic Bow", 8)

    def normal_attack(self):
        return {'type': 'projectile', 'damage': self.damage, 'speed': 10}

    def skill_attack(self):
        return {'type': 'projectile', 'damage': self.damage * 1.5, 'speed': 15, 'piercing': True}

class Bomb(Weapon):
    """副武器：炸弹。"""
    def __init__(self):
        super().__init__("Bomb", 25)
        self.skill_cooldown = 30000  # 30 seconds in milliseconds

    def normal_attack(self):
        return {'type': 'effect', 'effect_type': 'explosion', 'radius': 100, 'duration': 250, 'damage': self.damage, 'color': (255, 120, 0)}

class HealPotion(Weapon):
    """副武器：治疗药水。"""
    def __init__(self):
        super().__init__("Heal Potion", 0)
        self.max_uses = 3  # Maximum 3 uses
        self.uses_remaining = self.max_uses

    def normal_attack(self):
        if self.uses_remaining > 0:
            self.uses_remaining -= 1
            return {'type': 'effect', 'effect_type': 'full_heal'}
        else:
            return None  # No uses remaining

    def refill_uses(self):
        """Refill the potion uses (for debugging or future items)."""
        self.uses_remaining = self.max_uses

class FireSword(Weapon):
    """稀有武器：火焰剑。"""
    def __init__(self):
        super().__init__("Fire Sword", 25)

    def normal_attack(self):
        return {'type': 'melee', 'damage': self.damage, 'range': 80, 'duration': 300, 'color': (255, 100, 0)}

    def skill_attack(self):
        return {'type': 'effect', 'effect_type': 'explosion', 'radius': 80, 'duration': 400, 'damage': self.damage * 2, 'color': (255, 50, 0)}

class IceBow(Weapon):
    """稀有武器：冰霜弓。"""
    def __init__(self):
        super().__init__("Ice Bow", 15)

    def normal_attack(self):
        return {'type': 'projectile', 'damage': self.damage, 'speed': 12, 'freeze': True}

    def skill_attack(self):
        return {'type': 'effect', 'effect_type': 'freeze_area', 'radius': 100, 'duration': 500, 'damage': self.damage, 'color': (100, 200, 255)}