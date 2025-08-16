import pygame
from .map_data_operon import EMPTY, COLLISION, NPC, SPAWN_MELEE, SPAWN_RANGED, SPAWN_WEAPON, INTERACT_DOOR, INTERACT_SCROLL, INTERACT_CHEST

class MapRenderOperon:
    """
    地图渲染操作子 - 负责地图的可视化渲染
    """
    def __init__(self, map_data_operon):
        """
        初始化地图渲染操作子
        :param map_data_operon: 地图数据操作子实例
        """
        self.map_data = map_data_operon
        self.font = pygame.font.SysFont('Arial', 12)

    def draw_grid(self, surface, camera_x):
        """
        在屏幕上绘制地图网格，实现无限滚动效果
        :param surface: 绘制的目标 Surface
        :param camera_x: 摄像机水平偏移量
        """
        screen_width, _ = surface.get_size()
        
        # 计算可见的格子范围
        start_col = int(camera_x // self.map_data.tile_size)
        end_col = start_col + (screen_width // self.map_data.tile_size) + 2

        for x_idx in range(start_col, end_col):
            for y in range(self.map_data.map_height):
                # Map is now a long strip, no horizontal looping
                map_x = x_idx

                rect = pygame.Rect(
                    x_idx * self.map_data.tile_size - camera_x,
                    y * self.map_data.tile_size,
                    self.map_data.tile_size,
                    self.map_data.tile_size
                )

                if not (0 <= map_x < self.map_data.map_width):
                    # For performance, just draw a simple border for tiles outside the defined map
                    pygame.draw.rect(surface, (50, 50, 50), rect, 1)
                    continue
                
                tile_type = self.map_data.map_data[y][map_x]
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
        self._draw_spawn_points(surface, camera_x, screen_width)
        
        # --- 绘制武器生成点 ---
        self._draw_weapon_spawn_points(surface, camera_x, screen_width)
        
        # --- 绘制交互点 ---
        self._draw_interact_points(surface, camera_x, screen_width)

    def _draw_spawn_points(self, surface, camera_x, screen_width):
        """绘制敌人生成点"""
        for point in self.map_data.spawn_points:
            world_x, world_y, spawn_type = point['pos'][0], point['pos'][1], point['type']
            
            # 只绘制在屏幕可视范围内的生成点
            screen_x = world_x - camera_x
            if 0 <= screen_x < screen_width:
                color = (255, 0, 0) if spawn_type == 'melee' else (0, 255, 0)
                # 在生成点的世界坐标中心绘制一个小圆点作为标记
                pygame.draw.circle(surface, color, (int(screen_x), int(world_y)), 5)

    def _draw_weapon_spawn_points(self, surface, camera_x, screen_width):
        """绘制武器生成点"""
        for point in self.map_data.weapon_spawn_points:
            world_x, world_y = point['pos']
            screen_x = world_x - camera_x
            if 0 <= screen_x < screen_width:
                color = (255, 255, 0) # Yellow for weapons
                pygame.draw.rect(surface, color, (int(screen_x) - 4, int(world_y) - 4, 8, 8)) # Square for weapons

    def _draw_interact_points(self, surface, camera_x, screen_width):
        """绘制交互点"""
        for point in self.map_data.interact_points:
            interact_type = point['type']
            
            # Skip drawing collected chests and scrolls (they disappear)
            if interact_type in [INTERACT_CHEST, INTERACT_SCROLL] and point.get('is_collected', False):
                continue
            
            # Set color based on type and state
            if interact_type == INTERACT_DOOR:
                is_open = point.get('is_open', False)
                is_broken = point.get('is_broken', False)
                
                if is_broken:
                    color = (80, 80, 80)  # Dark gray for broken doors
                elif is_open:
                    color = (160, 82, 45)  # Light brown for open doors
                else:
                    color = (139, 69, 19)  # Brown for closed doors
            elif interact_type == INTERACT_SCROLL:
                color = (138, 43, 226)  # Blue-violet for scrolls
            elif interact_type == INTERACT_CHEST:
                color = (255, 140, 0)    # Dark orange for chests
            
            # Check if this is a merged group
            if point.get('is_group') and 'group_positions' in point:
                # Draw filled blocks for all grid positions in the group
                for grid_x, grid_y in point['group_positions']:
                    world_x = grid_x * self.map_data.tile_size
                    world_y = grid_y * self.map_data.tile_size
                    screen_x = world_x - camera_x
                    
                    if -self.map_data.tile_size <= screen_x < screen_width + self.map_data.tile_size:
                        rect = pygame.Rect(screen_x, world_y, self.map_data.tile_size, self.map_data.tile_size)
                        pygame.draw.rect(surface, color, rect)
                        
                        # For doors, add state visualization
                        if interact_type == INTERACT_DOOR:
                            if is_broken:
                                # Draw X for broken doors
                                pygame.draw.line(surface, (255, 0, 0), 
                                               (rect.left, rect.top), 
                                               (rect.right, rect.bottom), 3)
                                pygame.draw.line(surface, (255, 0, 0), 
                                               (rect.right, rect.top), 
                                               (rect.left, rect.bottom), 3)
                            elif is_open:
                                # Draw open door indicator (green border)
                                pygame.draw.rect(surface, (0, 255, 0), rect, 2)
                            else:
                                # Draw closed door indicator (red border)
                                pygame.draw.rect(surface, (255, 0, 0), rect, 2)
            else:
                # For single points, always draw as filled block
                grid_x = int(point['pos'][0] // self.map_data.tile_size)
                grid_y = int(point['pos'][1] // self.map_data.tile_size)
                world_x = grid_x * self.map_data.tile_size
                world_y = grid_y * self.map_data.tile_size
                screen_x = world_x - camera_x
                
                if -self.map_data.tile_size <= screen_x < screen_width + self.map_data.tile_size:
                    rect = pygame.Rect(screen_x, world_y, self.map_data.tile_size, self.map_data.tile_size)
                    pygame.draw.rect(surface, color, rect)
                    
                    # For doors, add state visualization
                    if interact_type == INTERACT_DOOR:
                        if is_broken:
                            # Draw X for broken doors
                            pygame.draw.line(surface, (255, 0, 0), 
                                           (rect.left, rect.top), 
                                           (rect.right, rect.bottom), 3)
                            pygame.draw.line(surface, (255, 0, 0), 
                                           (rect.right, rect.top), 
                                           (rect.left, rect.bottom), 3)
                        elif is_open:
                            # Draw open door indicator (green border)
                            pygame.draw.rect(surface, (0, 255, 0), rect, 2)
                        else:
                            # Draw closed door indicator (red border)
                            pygame.draw.rect(surface, (255, 0, 0), rect, 2)