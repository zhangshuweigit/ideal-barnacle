import pygame

class Weapon:
    """武器的基类，定义通用属性。"""
    def __init__(self, name, damage):
        self.name = name
        self.damage = damage
        self.skill_cooldown = 1000  # Default 1 second cooldown for skills

class BasicSword(Weapon):
    """基础近战武器：剑。"""
    def __init__(self):
        super().__init__("Basic Sword", 10)
        self.skill_cooldown = 2000  # 2 seconds cooldown for sword skill

    def normal_attack(self):
        return {'type': 'melee', 'damage': self.damage, 'range': 60, 'duration': 200, 'color': (255, 255, 0)}

    def skill_attack(self):
        return {'type': 'melee', 'damage': self.damage * 5, 'range': 90, 'duration': 400, 'color': (255, 100, 0)}

class BasicBow(Weapon):
    """基础远程武器：弓。"""
    def __init__(self):
        super().__init__("Basic Bow", 8)
        self.skill_cooldown = 1500  # 1.5 seconds cooldown for bow skill

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
        self.skill_cooldown = 60000  # 60 seconds cooldown for heal potion

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
            'main_1': 0,  # Main weapon 1 cooldown
            'main_2': 0,  # Main weapon 2 cooldown
            'sub_1': 0,   # Bomb cooldown end time
            'sub_2': 0    # HealPotion cooldown end time
        }

        # 移除了射击相关变量

    def get_weapon_data(self):
        """获取当前武器槽位数据用于保存"""
        weapon_data = {}
        for slot, weapon in self.slots.items():
            if weapon:
                weapon_data[slot] = {
                    'name': weapon.name,
                    'class': weapon.__class__.__name__
                }
        return weapon_data
    
    def load_weapon_data(self, weapon_data):
        """从保存的数据加载武器"""
        weapon_classes = {
            'BasicSword': BasicSword,
            'BasicBow': BasicBow,
            'Bomb': Bomb,
            'HealPotion': HealPotion,
            'FireSword': FireSword,
            'IceBow': IceBow
        }
        
        for slot, data in weapon_data.items():
            if slot in self.slots and 'class' in data:
                weapon_class_name = data['class']
                if weapon_class_name in weapon_classes:
                    self.slots[slot] = weapon_classes[weapon_class_name]()
        
        # --- 状态管理 ---
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 0
        self.attack_hitbox = None
        
        # 核心：此类自己维护和"记忆"瞄准方向，1为右，-1为左。
        self.aiming_direction = 1

        # 重置射击序列状态
        self.shot_count = 0
        self.last_shot_sequence_time = 0
        self.is_rapid_shot_sequence = False

        # 技能冷却时间管理
        self.skill_cooldowns = {
            'main_1': 0,  # Main weapon 1 cooldown
            'main_2': 0,  # Main weapon 2 cooldown
            'sub_1': 0,   # Bomb cooldown end time
            'sub_2': 0    # HealPotion cooldown end time
        } 

    def attack(self, actions):
        """
        处理攻击输入。所有方向逻辑都在此函数内完成，不再依赖外部计算。
        """
        # --- 攻击前置检查 ---
        # 只检查是否正在攻击，允许快速射击
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

        # --- 冷却检查 (技能攻击和有冷却的普通攻击) ---
        current_time = pygame.time.get_ticks()
        if slot in self.skill_cooldowns and current_time < self.skill_cooldowns[slot]:
            # Weapon is on cooldown
            return None

        # --- 生成攻击数据 ---
        attack_data = weapon.skill_attack() if is_skill else weapon.normal_attack()
        if not attack_data:
            return None

        # --- 设置冷却 (技能攻击和有冷却的普通攻击) ---
        if slot in self.skill_cooldowns and hasattr(weapon, 'skill_cooldown'):
            # For sub weapons, use cooldown on both normal and skill attacks
            if slot.startswith('sub_'):
                self.skill_cooldowns[slot] = current_time + weapon.skill_cooldown
            # For main weapons, only use cooldown on skill attacks
            elif is_skill:
                self.skill_cooldowns[slot] = current_time + weapon.skill_cooldown

        attack_data['direction'] = direction_vector

      # 移除了射击状态触发逻辑

        # --- 处理近战攻击的特殊状态 ---
        if attack_data.get('type') == 'melee':
            self.is_attacking = True
            self.attack_duration = attack_data.get('duration', 200)
            self.attack_color = attack_data.get('color', (255, 255, 0))
            self.attack_range = attack_data.get('range', 60)
            # 近战攻击的方向也使用计算好的瞄准方向
            self.attack_direction = direction_vector
            self.attack_timer = pygame.time.get_ticks()

            # 根据鼠标位置确定攻击方向
            mouse_screen_x = mouse_pos[0] + camera_x if camera_x else mouse_pos[0]
            attack_direction = 1 if player_rect.centerx < mouse_screen_x else -1

            # 创建攻击hitbox，绑定在角色身上
            self.attack_hitbox = pygame.Rect(
                player_rect.centerx if attack_direction > 0 else player_rect.centerx - self.attack_range,
                player_rect.centery - 20,
                self.attack_range,
                40
            )

            # 保存攻击方向用于后续更新
            self.attack_direction = attack_direction

        return attack_data

    def update(self, player_rect, mouse_pos):
        """更新近战攻击和射击状态。"""
        current_time = pygame.time.get_ticks()

        # 更新近战攻击状态
        if self.is_attacking:
            if current_time - self.attack_timer > self.attack_duration:
                self.is_attacking = False
                self.attack_hitbox = None
            else:
                # 更新攻击hitbox位置，使其跟随角色移动
                if hasattr(self, 'attack_direction'):
                    self.attack_hitbox = pygame.Rect(
                        player_rect.centerx if self.attack_direction > 0 else player_rect.centerx - self.attack_range,
                        player_rect.centery - 20,
                        self.attack_range,
                        40
                    )

        # 移除了射击状态更新逻辑

    def draw(self, screen, camera_x=0):
        """绘制近战攻击的可视化效果。"""
        if self.is_attacking and self.attack_hitbox:
            adjusted_hitbox = self.attack_hitbox.copy()
            adjusted_hitbox.x -= camera_x
            pygame.draw.rect(screen, self.attack_color, adjusted_hitbox)

    def get_shot_interval_info(self):
        """获取射击间隔信息，用于动画系统决定播放哪一帧"""
        current_time = pygame.time.get_ticks()
        time_since_last_shot = current_time - self.last_shot_time

        # 如果距离上次射击不到1秒，返回True表示应该播放最后一张图片
        return time_since_last_shot < 1000

    # 移除了快速射击检查方法

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
