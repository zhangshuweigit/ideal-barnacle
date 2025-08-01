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

class MapOperon:
    """
    地图操纵子 - 管理地图数据、绘制和编辑
    """
    def __init__(self, map_width, map_height, tile_size):
        """
        初始化地图操纵子
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
        # Add a default ground line across the entire map width
        ground_y = map_height - 2
        for x in range(map_width):
            self.map_data[ground_y][x] = COLLISION
            
        self.font = pygame.font.SysFont('Arial', 12)

    def draw_grid(self, surface, camera_x):
        """
        在屏幕上绘制地图网格，实现无限滚动效果
        :param surface: 绘制的目标 Surface
        :param camera_x: 摄像机水平偏移量
        """
        screen_width, _ = surface.get_size()
        
        # 计算可见的格子范围
        start_col = int(camera_x // self.tile_size)
        end_col = start_col + (screen_width // self.tile_size) + 2

        for x_idx in range(start_col, end_col):
            for y in range(self.map_height):
                # Map is now a long strip, no horizontal looping
                map_x = x_idx

                rect = pygame.Rect(
                    x_idx * self.tile_size - camera_x,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )

                if not (0 <= map_x < self.map_width):
                    # For performance, just draw a simple border for tiles outside the defined map
                    pygame.draw.rect(surface, (50, 50, 50), rect, 1)
                    continue
                
                tile_type = self.map_data[y][map_x]
                color = (50, 50, 50) # 网格颜色
                fill_color = None

                if tile_type == COLLISION:
                    fill_color = (100, 100, 100) # 填充灰色
                elif tile_type == NPC:
                    fill_color = (50, 50, 200)   # 填充蓝色

                if fill_color:
                    pygame.draw.rect(surface, fill_color, rect)
                
                pygame.draw.rect(surface, color, rect, 1) # 绘制边框

        # --- 绘制生成点 ---
        for point in self.spawn_points:
            world_x, world_y, spawn_type = point['pos'][0], point['pos'][1], point['type']
            
            # 只绘制在屏幕可视范围内的生成点
            screen_x = world_x - camera_x
            if 0 <= screen_x < screen_width:
                color = (255, 0, 0) if spawn_type == SPAWN_MELEE else (0, 255, 0)
                # 在生成点的世界坐标中心绘制一个小圆点作为标记
                pygame.draw.circle(surface, color, (int(screen_x), int(world_y)), 5)
        
        # --- 绘制武器生成点 ---
        for point in self.weapon_spawn_points:
            world_x, world_y = point['pos']
            screen_x = world_x - camera_x
            if 0 <= screen_x < screen_width:
                color = (255, 255, 0) # Yellow for weapons
                pygame.draw.rect(surface, color, (int(screen_x) - 4, int(world_y) - 4, 8, 8)) # Square for weapons



    def edit_tile(self, mouse_pos, camera_x, mark_type):
        """
        编辑指定位置的格子，支持无限地图
        :param mouse_pos: 鼠标在屏幕上的位置
        :param camera_x: 摄像机水平偏移量
        :param mark_type: 要标记的类型 (COLLISION, NPC, EMPTY)
        """
        # 将屏幕坐标转换为世界坐标，再转换为地图格子坐标
        world_x = mouse_pos[0] + camera_x
        map_x = int(world_x // self.tile_size)
        map_y = int(mouse_pos[1] // self.tile_size)

        if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
            self.map_data[map_y][map_x] = mark_type
            print(f"标记格子 ({map_x}, {map_y}) 为 {mark_type}")

    def add_spawn_point(self, world_pos, spawn_type):
        """Adds a new enemy or weapon spawn point."""
        if spawn_type == SPAWN_WEAPON:
            new_point = {'type': spawn_type, 'pos': world_pos}
            self.weapon_spawn_points.append(new_point)
            print(f"Added weapon spawn point at {world_pos}")
        else: # Enemy spawns
            new_point = {'type': spawn_type, 'pos': world_pos}
            self.spawn_points.append(new_point)
            print(f"Added {spawn_type} spawn point at {world_pos}")

    def remove_spawn_point_at(self, world_pos, search_radius=15):
        """Removes the nearest enemy or weapon spawn point to the given world position."""
        target_pos = pygame.Vector2(world_pos)
        
        # Check enemy spawn points first
        closest_enemy_point = None
        min_dist_sq_enemy = search_radius ** 2
        for point in self.spawn_points:
            dist_sq = target_pos.distance_to(pygame.Vector2(point['pos']))
            if dist_sq < min_dist_sq_enemy:
                min_dist_sq_enemy = dist_sq
                closest_enemy_point = point
        
        # Check weapon spawn points
        closest_weapon_point = None
        min_dist_sq_weapon = search_radius ** 2
        for point in self.weapon_spawn_points:
            dist_sq = target_pos.distance_to(pygame.Vector2(point['pos']))
            if dist_sq < min_dist_sq_weapon:
                min_dist_sq_weapon = dist_sq
                closest_weapon_point = point

        # Prioritize removing the absolute closest point
        if closest_enemy_point and min_dist_sq_enemy < min_dist_sq_weapon:
            self.spawn_points.remove(closest_enemy_point)
            print(f"Removed {closest_enemy_point['type']} spawn point at {closest_enemy_point['pos']}")
        elif closest_weapon_point:
            self.weapon_spawn_points.remove(closest_weapon_point)
            print(f"Removed weapon spawn point at {closest_weapon_point['pos']}")
        else:
            print(f"No spawn point found within {search_radius} pixels of {world_pos}")



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
        """Saves the current state of the entire map and spawn points."""
        data_to_save = {
            'map_layout': self.map_data,
            'spawn_points': self.spawn_points,
            'weapon_spawn_points': self.weapon_spawn_points
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
            
            # Update map dimensions based on loaded data
            self.map_height = len(self.map_data)
            self.map_width = len(self.map_data[0]) if self.map_height > 0 else 0
            
            print(f"Full map data from {filename} loaded successfully.")
        except FileNotFoundError:
            print(f"Map file '{filename}' not found. Using default empty map.")
        except Exception as e:
            print(f"An error occurred while loading map: {e}")


