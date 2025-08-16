import pygame
import json

# --- 地图元素常量 ---
EMPTY = 0
COLLISION = 1
NPC = 2

# --- 生成点类型常量 ---
SPAWN_MELEE = 'melee'
SPAWN_RANGED = 'ranged'
SPAWN_WEAPON = 'weapon'

# --- 交互点类型常量 ---
INTERACT_DOOR = 'door'
INTERACT_SCROLL = 'scroll'
INTERACT_CHEST = 'chest'

class MapDataOperon:
    """
    地图数据操作子 - 管理地图数据和保存/加载功能
    """
    def __init__(self, map_width, map_height, tile_size):
        """
        初始化地图数据操作子
        :param map_width: 地图宽度 (格子数)
        :param map_height: 地图高度 (格子数)
        :param tile_size: 每个格子的像素大小
        """
        self.map_width = map_width
        self.map_height = map_height
        self.tile_size = tile_size
        self.map_data = [[EMPTY for _ in range(map_width)] for _ in range(map_height)]
        self.spawn_points = [] # For enemies
        self.weapon_spawn_points = [] # For weapons
        self.interact_points = [] # For interactive points (door, scroll, chest)
        # Add a default ground line across the entire map width
        ground_y = map_height - 2
        for x in range(map_width):
            self.map_data[ground_y][x] = COLLISION

    def get_tile(self, world_x, world_y):
        """
        根据世界坐标获取格子类型
        :param world_x: 世界 x 坐标
        :param world_y: 世界 y 坐标
        :return: 格子类型
        """
        map_x = int(world_x // self.tile_size)
        map_y = int(world_y // self.tile_size)
        
        if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
            return self.map_data[map_y][map_x]
        return None

    def save_to_file(self, filename):
        """Saves the current state of the entire map and all points."""
        data_to_save = {
            'map_layout': self.map_data,
            'spawn_points': self.spawn_points,
            'weapon_spawn_points': self.weapon_spawn_points,
            'interact_points': self.interact_points
        }
        try:
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print(f"Full map data saved to {filename}")
        except IOError as e:
            print(f"Error saving map data to {filename}: {e}")

    def load_from_file(self, filename):
        """
        Loads the entire map state from a saved file.
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.map_data = data.get('map_layout', self.map_data)
            self.spawn_points = data.get('spawn_points', [])
            self.weapon_spawn_points = data.get('weapon_spawn_points', [])
            self.interact_points = data.get('interact_points', [])
            
            # Update map dimensions based on loaded data
            self.map_height = len(self.map_data)
            self.map_width = len(self.map_data[0]) if self.map_height > 0 else 0
            
            print(f"Full map data from {filename} loaded successfully.")
        except FileNotFoundError:
            print(f"Map file '{filename}' not found. Using default empty map.")
        except Exception as e:
            print(f"An error occurred while loading map: {e}")