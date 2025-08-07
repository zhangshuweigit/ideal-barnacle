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

class WeaponOperon:
    """
    全新重构的武器操纵子 (射击系统)。
    此类独立负责所有攻击方向的计算，确保射击逻辑的绝对正确性。
    """
    def __init__(self):
        self.slots = {
            'main_1': BasicSword(), 'main_2': BasicBow(),
            'sub_1': Bomb(), 'sub_2': HealPotion()
        }
        
        # --- 状态管理 ---
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 0
        self.attack_hitbox = None
        
        # 核心：此类自己维护和"记忆"瞄准方向，1为右，-1为左。
        self.aiming_direction = 1
        
        # 技能冷却时间管理
        self.skill_cooldowns = {
            'sub_1': 0,  # Bomb cooldown end time
            'sub_2': 0   # HealPotion cooldown end time
        } 

    def attack(self, actions):
        """
        处理攻击输入。所有方向逻辑都在此函数内完成，不再依赖外部计算。
        """
        # --- 攻击前置检查 ---
        if self.is_attacking or not actions.get('active_slot'):
            return None

        slot = actions.get('active_slot')
        weapon = self.slots.get(slot)
        if not weapon:
            return None
            
        is_skill = actions.get('is_skill', False)
        if 'sub' in slot and is_skill:
            return None

        # --- 核心方向计算逻辑 ---
        mouse_pos = actions.get('mouse_pos')
        player_rect = actions.get('player_rect')
        camera_x = actions.get('camera_x', 0)

        # 1. 只有当鼠标在窗口内时，才更新瞄准方向
        if mouse_pos and player_rect:
            # 使用屏幕坐标进行比较，这是确保正确的关键
            player_screen_x = player_rect.centerx - camera_x
            if mouse_pos[0] < player_screen_x:
                self.aiming_direction = -1
            else:
                self.aiming_direction = 1
        
        # 2. 如果鼠标不在窗口内，aiming_direction会保持上一次的值（实现记忆）
        
        direction_vector = pygame.Vector2(self.aiming_direction, 0)

        # --- 技能冷却检查 (只对技能攻击) ---
        current_time = pygame.time.get_ticks()
        if is_skill and slot in self.skill_cooldowns and current_time < self.skill_cooldowns[slot]:
            # Skill is on cooldown
            return None
            
        # --- 生成攻击数据 ---
        attack_data = weapon.skill_attack() if is_skill else weapon.normal_attack()
        if not attack_data:
            return None
            
        # --- 设置技能冷却 ---
        if slot in self.skill_cooldowns and hasattr(weapon, 'skill_cooldown'):
            self.skill_cooldowns[slot] = current_time + weapon.skill_cooldown
            
        attack_data['direction'] = direction_vector
        
        # --- 处理近战攻击的特殊状态 ---
        if attack_data.get('type') == 'melee':
            self.is_attacking = True
            self.attack_duration = attack_data.get('duration', 200)
            self.attack_color = attack_data.get('color', (255, 255, 0))
            self.attack_range = attack_data.get('range', 60)
            # 近战攻击的方向也使用计算好的瞄准方向
            self.attack_direction = direction_vector
            self.attack_timer = pygame.time.get_ticks()
            
            # 直接创建攻击hitbox
            hitbox_start_x = player_rect.centerx if self.aiming_direction > 0 else player_rect.centerx - self.attack_range
            self.attack_hitbox = pygame.Rect(
                hitbox_start_x, 
                player_rect.centery - 20,  # Center vertically on player
                self.attack_range, 
                40
            )
        
        return attack_data

    def update(self, player_rect, mouse_pos):
        """更新近战攻击的动画和 hitbox。"""
        if self.is_attacking:
            if pygame.time.get_ticks() - self.attack_timer > self.attack_duration:
                self.is_attacking = False
                self.attack_hitbox = None
            else:
                # 使用 attack_direction (在 attack 方法中设置) 来更新 hitbox
                hitbox_start_x = player_rect.centerx if self.attack_direction.x > 0 else player_rect.centerx - self.attack_range
                self.attack_hitbox = pygame.Rect(hitbox_start_x, player_rect.centery - 20, self.attack_range, 40)

    def draw(self, screen, camera_x=0):
        """绘制近战攻击的可视化效果。"""
        if self.is_attacking and self.attack_hitbox:
            adjusted_hitbox = self.attack_hitbox.copy()
            adjusted_hitbox.x -= camera_x
            pygame.draw.rect(screen, self.attack_color, adjusted_hitbox)

    def update(self, player_rect, mouse_pos):
        """Update weapon state (currently just for attack timing)."""
        # Update attack state
        if self.is_attacking:
            if pygame.time.get_ticks() - self.attack_timer > self.attack_duration:
                self.is_attacking = False
                self.attack_hitbox = None

    def handle_chest_reward(self, chest_info):
        """处理宝箱奖励，随机给予玩家新武器。"""
        rare_weapons = [FireSword(), IceBow()]
        
        # Randomly select a rare weapon
        new_weapon = rare_weapons[pygame.time.get_ticks() % len(rare_weapons)]
        
        # Replace a random weapon slot
        slot_keys = list(self.slots.keys())
        random_slot = slot_keys[pygame.time.get_ticks() % len(slot_keys)]
        
        old_weapon = self.slots[random_slot]
        self.slots[random_slot] = new_weapon
        
        print(f"Chest reward: Replaced {old_weapon.name if old_weapon else 'empty'} with {new_weapon.name} in {random_slot}")
        
        # Add chest notification to player (will be handled by main.py)
        return {
            'slot': random_slot,
            'old_weapon': old_weapon.name if old_weapon else None,
            'new_weapon': new_weapon.name,
            'notification_text': f"New Weapon: {new_weapon.name}!",
            'notification_color': (255, 215, 0)  # Gold color
        }
