import pygame
from .map_data_operon import COLLISION, NPC, EMPTY, SPAWN_MELEE, SPAWN_RANGED, SPAWN_WEAPON, INTERACT_DOOR, INTERACT_SCROLL, INTERACT_CHEST

class MapEditOperon:
    """
    地图编辑操作子 - 处理地图编辑功能
    """
    def __init__(self, map_data_operon):
        """
        初始化地图编辑操作子
        :param map_data_operon: 地图数据操作子实例
        """
        self.map_data = map_data_operon

    def edit_tile(self, mouse_pos, camera_x, mark_type):
        """
        编辑指定位置的格子，支持无限地图
        :param mouse_pos: 鼠标在屏幕上的位置
        :param camera_x: 摄像机水平偏移量
        :param mark_type: 要标记的类型 (COLLISION, NPC, EMPTY)
        """
        # 将屏幕坐标转换为世界坐标，再转换为地图格子坐标
        world_x = mouse_pos[0] + camera_x
        map_x = int(world_x // self.map_data.tile_size)
        map_y = int(mouse_pos[1] // self.map_data.tile_size)

        if 0 <= map_x < self.map_data.map_width and 0 <= map_y < self.map_data.map_height:
            self.map_data.map_data[map_y][map_x] = mark_type
            print(f"标记格子 ({map_x}, {map_y}) 为 {mark_type}")

    def add_spawn_point(self, world_pos, spawn_type):
        """Adds a new enemy or weapon spawn point."""
        if spawn_type == SPAWN_WEAPON:
            new_point = {'type': spawn_type, 'pos': world_pos}
            self.map_data.weapon_spawn_points.append(new_point)
            print(f"Added weapon spawn point at {world_pos}")
        else: # Enemy spawns
            new_point = {'type': spawn_type, 'pos': world_pos}
            self.map_data.spawn_points.append(new_point)
            print(f"Added {spawn_type} spawn point at {world_pos}")

    def remove_spawn_point_at(self, world_pos, search_radius=15):
        """Removes the nearest enemy, weapon, or interact point to the given world position."""
        target_pos = pygame.Vector2(world_pos)
        
        # Check enemy spawn points first
        closest_enemy_point = None
        min_dist_sq_enemy = search_radius ** 2
        for point in self.map_data.spawn_points:
            dist_sq = target_pos.distance_to(pygame.Vector2(point['pos']))
            if dist_sq < min_dist_sq_enemy:
                min_dist_sq_enemy = dist_sq
                closest_enemy_point = point
        
        # Check weapon spawn points
        closest_weapon_point = None
        min_dist_sq_weapon = search_radius ** 2
        for point in self.map_data.weapon_spawn_points:
            dist_sq = target_pos.distance_to(pygame.Vector2(point['pos']))
            if dist_sq < min_dist_sq_weapon:
                min_dist_sq_weapon = dist_sq
                closest_weapon_point = point
        
        # Check interact points
        closest_interact_point = None
        min_dist_sq_interact = search_radius ** 2
        for point in self.map_data.interact_points:
            dist_sq = target_pos.distance_to(pygame.Vector2(point['pos']))
            if dist_sq < min_dist_sq_interact:
                min_dist_sq_interact = dist_sq
                closest_interact_point = point

        # Prioritize removing the absolute closest point
        if closest_enemy_point and min_dist_sq_enemy < min_dist_sq_weapon and min_dist_sq_enemy < min_dist_sq_interact:
            self.map_data.spawn_points.remove(closest_enemy_point)
            print(f"Removed {closest_enemy_point['type']} spawn point at {closest_enemy_point['pos']}")
        elif closest_weapon_point and min_dist_sq_weapon < min_dist_sq_interact:
            self.map_data.weapon_spawn_points.remove(closest_weapon_point)
            print(f"Removed weapon spawn point at {closest_weapon_point['pos']}")
        elif closest_interact_point:
            self.map_data.interact_points.remove(closest_interact_point)
            print(f"Removed {closest_interact_point['type']} interact point at {closest_interact_point['pos']}")
        else:
            print(f"No spawn/interact point found within {search_radius} pixels of {world_pos}")