from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class EntityState:
    """实体状态标准化数据结构"""
    position: tuple  # x, y坐标
    health: int
    max_health: int
    is_alive: bool
    entity_id: str

@dataclass
class PlayerAction:
    """玩家动作标准化数据结构"""
    move_direction: int = 0  # -1左移, 0静止, 1右移
    jump: bool = False
    attack: bool = False
    skill: bool = False
    interact: bool = False
    roll: bool = False
    active_slot: Optional[str] = None  # 'main_1', 'main_2', 'sub_1', 'sub_2'

@dataclass
class AttackData:
    """攻击数据标准化数据结构"""
    attack_type: str  # 'melee', 'projectile', 'effect'
    damage: int
    direction: tuple  # x, y方向向量
    source_id: str
    position: tuple  # 攻击发起位置

@dataclass
class InteractionData:
    """交互数据标准化数据结构"""
    interaction_type: str  # 'chest', 'scroll', 'door', 'npc'
    entity_id: str
    position: tuple  # 交互位置
    data: Dict[str, Any]  # 额外数据

@dataclass
class NotificationData:
    """通知数据标准化数据结构"""
    message: str
    notification_type: str  # 'info', 'warning', 'error', 'success'
    duration: int = 3000  # 持续时间(毫秒)
    data: Dict[str, Any]  # 额外数据