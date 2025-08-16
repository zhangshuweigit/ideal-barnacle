from dataclasses import dataclass
from typing import Dict, List, Callable, Any
import json

@dataclass
class EventData:
    """标准化事件数据结构"""
    event_type: str
    data: Dict[str, Any]
    source: str = ""

class EventSystem:
    """简单的事件系统，实现发布/订阅模式"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable[[EventData], None]):
        """订阅指定类型的事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def publish(self, event: EventData):
        """发布事件给所有订阅者"""
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                callback(event)
    
    def unsubscribe(self, event_type: str, callback: Callable[[EventData], None]):
        """取消订阅指定类型的事件"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

# 全局事件总线实例
event_bus = EventSystem()

# 使用示例:
# def on_player_move(event: EventData):
#     print(f"Player moved to {event.data['x']}, {event.data['y']}")
#
# event_bus.subscribe("player_move", on_player_move)
# event_bus.publish(EventData("player_move", {"x": 100, "y": 200}, "movement_operon"))