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
        self.interact_points = [] # For interactive points (door, scroll, chest)
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
        
        # --- 绘制交互点 ---
        for point in self.interact_points:
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
                    world_x = grid_x * self.tile_size
                    world_y = grid_y * self.tile_size
                    screen_x = world_x - camera_x
                    
                    if -self.tile_size <= screen_x < screen_width + self.tile_size:
                        rect = pygame.Rect(screen_x, world_y, self.tile_size, self.tile_size)
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
                grid_x = int(point['pos'][0] // self.tile_size)
                grid_y = int(point['pos'][1] // self.tile_size)
                world_x = grid_x * self.tile_size
                world_y = grid_y * self.tile_size
                screen_x = world_x - camera_x
                
                if -self.tile_size <= screen_x < screen_width + self.tile_size:
                    rect = pygame.Rect(screen_x, world_y, self.tile_size, self.tile_size)
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
        """Removes the nearest enemy, weapon, or interact point to the given world position."""
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
        
        # Check interact points
        closest_interact_point = None
        min_dist_sq_interact = search_radius ** 2
        for point in self.interact_points:
            dist_sq = target_pos.distance_to(pygame.Vector2(point['pos']))
            if dist_sq < min_dist_sq_interact:
                min_dist_sq_interact = dist_sq
                closest_interact_point = point

        # Prioritize removing the absolute closest point
        if closest_enemy_point and min_dist_sq_enemy < min_dist_sq_weapon and min_dist_sq_enemy < min_dist_sq_interact:
            self.spawn_points.remove(closest_enemy_point)
            print(f"Removed {closest_enemy_point['type']} spawn point at {closest_enemy_point['pos']}")
        elif closest_weapon_point and min_dist_sq_weapon < min_dist_sq_interact:
            self.weapon_spawn_points.remove(closest_weapon_point)
            print(f"Removed weapon spawn point at {closest_weapon_point['pos']}")
        elif closest_interact_point:
            self.interact_points.remove(closest_interact_point)
            print(f"Removed {closest_interact_point['type']} interact point at {closest_interact_point['pos']}")
        else:
            print(f"No spawn/interact point found within {search_radius} pixels of {world_pos}")

    def _find_nearby_same_type_points(self, grid_x, grid_y, interact_type):
        """Find nearby points of the same type in all 9 grid cells (3x3 area)."""
        nearby_points = []
        
        # Check all 9 cells (3x3 area centered on current cell)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_grid_x = grid_x + dx
                check_grid_y = grid_y + dy
                
                # Check if there's a point of the same type in this grid cell
                for point in self.interact_points:
                    if point['type'] == interact_type and not point.get('is_collected', False):
                        # For groups, check all positions in the group
                        if point.get('is_group') and 'group_positions' in point:
                            for group_x, group_y in point['group_positions']:
                                if group_x == check_grid_x and group_y == check_grid_y:
                                    nearby_points.append(point)
                                    break  # Found this point, no need to check other positions
                        else:
                            # Single point
                            point_grid_x = int(point['pos'][0] // self.tile_size)
                            point_grid_y = int(point['pos'][1] // self.tile_size)
                            
                            if point_grid_x == check_grid_x and point_grid_y == check_grid_y:
                                nearby_points.append(point)
        
        # Remove duplicates (same point might be found multiple times)
        unique_points = []
        seen_points = set()
        for point in nearby_points:
            point_id = id(point)  # Use object id as unique identifier
            if point_id not in seen_points:
                seen_points.add(point_id)
                unique_points.append(point)
        return unique_points

    def _merge_points_into_group(self, main_point, nearby_points):
        """Create or update a merged group of points."""
        # Get all grid positions in the group
        main_grid_x = int(main_point['pos'][0] // self.tile_size)
        main_grid_y = int(main_point['pos'][1] // self.tile_size)
        
        group_positions = [(main_grid_x, main_grid_y)]
        
        for point in nearby_points:
            grid_x = int(point['pos'][0] // self.tile_size)
            grid_y = int(point['pos'][1] // self.tile_size)
            group_positions.append((grid_x, grid_y))
        
        # For doors, ensure consistent state across the group
        if main_point['type'] == INTERACT_DOOR:
            # Use the state from the main point
            door_state = {
                'is_open': main_point.get('is_open', False),
                'is_broken': main_point.get('is_broken', False)
            }
        
        # Update the main point to mark it as a group
        main_point['is_group'] = True
        main_point['group_positions'] = group_positions
        
        # Remove the nearby points as they're now part of the group
        for point in nearby_points:
            if point in self.interact_points:
                self.interact_points.remove(point)
        
        print(f"Merged {len(nearby_points) + 1} {main_point['type']} points into a group")

    def add_interact_point(self, world_pos, interact_type):
        """Adds a new interactive point (door, scroll, chest) with fixed sizes and auto-merging."""
        # Convert world position to grid coordinates
        grid_x = int(world_pos[0] // self.tile_size)
        grid_y = int(world_pos[1] // self.tile_size)
        
        # Define fixed sizes for each interact type
        if interact_type == INTERACT_DOOR:
            # Door: 1x3 vertical (3 tiles)
            shape_positions = [(grid_x, grid_y), (grid_x, grid_y + 1), (grid_x, grid_y + 2)]
        elif interact_type == INTERACT_CHEST:
            # Chest: 2x2 square (4 tiles)
            shape_positions = [
                (grid_x, grid_y), (grid_x + 1, grid_y),
                (grid_x, grid_y + 1), (grid_x + 1, grid_y + 1)
            ]
        elif interact_type == INTERACT_SCROLL:
            # Scroll: 2x4 vertical (8 tiles)
            shape_positions = [
                (grid_x, grid_y), (grid_x + 1, grid_y),
                (grid_x, grid_y + 1), (grid_x + 1, grid_y + 1),
                (grid_x, grid_y + 2), (grid_x + 1, grid_y + 2),
                (grid_x, grid_y + 3), (grid_x + 1, grid_y + 3)
            ]
        else:
            # Default: single tile
            shape_positions = [(grid_x, grid_y)]
        
        # Calculate center position of the shape
        center_x = sum(pos[0] for pos in shape_positions) // len(shape_positions)
        center_y = sum(pos[1] for pos in shape_positions) // len(shape_positions)
        center_world_pos = (
            center_x * self.tile_size + self.tile_size // 2,
            center_y * self.tile_size + self.tile_size // 2
        )
        
        # Check for nearby points of the same type (using the center position)
        nearby_points = self._find_nearby_same_type_points(center_x, center_y, interact_type)
        
        if nearby_points:
            # If there are nearby points, merge them ALL into ONE group
            main_point = nearby_points[0]
            
            # Create a new merged group that includes ALL points
            all_positions = set()
            
            # Add all positions from all nearby points
            for point in nearby_points:
                if point.get('is_group') and 'group_positions' in point:
                    for group_x, group_y in point['group_positions']:
                        all_positions.add((group_x, group_y))
                else:
                    point_grid_x = int(point['pos'][0] // self.tile_size)
                    point_grid_y = int(point['pos'][1] // self.tile_size)
                    all_positions.add((point_grid_x, point_grid_y))
            
            # Add the new shape positions
            for pos in shape_positions:
                all_positions.add(pos)
            
            # Calculate the center position of the merged group
            center_x = sum(pos[0] for pos in all_positions) // len(all_positions)
            center_y = sum(pos[1] for pos in all_positions) // len(all_positions)
            center_world_pos = (
                center_x * self.tile_size + self.tile_size // 2,
                center_y * self.tile_size + self.tile_size // 2
            )
            
            # Remove all the old points
            for point in nearby_points:
                if point in self.interact_points:
                    self.interact_points.remove(point)
            
            # Create the new merged point
            new_point = {
                'type': interact_type,
                'pos': center_world_pos,
                'is_open': False if interact_type == INTERACT_DOOR else None,
                'is_broken': False,
                'is_collected': False,
                'is_group': True,
                'group_positions': list(all_positions)
            }
            self.interact_points.append(new_point)
            
            print(f"Created merged {interact_type} group with {len(all_positions)} tiles at center ({center_x}, {center_y})")
        else:
            # No nearby points, create new point with its shape
            new_point = {
                'type': interact_type,
                'pos': center_world_pos,
                'is_open': False if interact_type == INTERACT_DOOR else None,
                'is_broken': False,
                'is_collected': False,
                'is_group': True,
                'group_positions': shape_positions
            }
            self.interact_points.append(new_point)
            print(f"Added {interact_type} interact point with {len(shape_positions)} tiles at center ({center_x}, {center_y})")



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

    def get_door_collision_rects(self):
        """
        获取所有门交互点的碰撞体积（仅关闭且未破坏的门）
        :return: 门碰撞体积的矩形列表
        """
        door_rects = []
        
        for point in self.interact_points:
            if point['type'] == INTERACT_DOOR:
                # Only add collision for doors that are closed and not broken
                if point.get('is_open', False) or point.get('is_broken', False):
                    continue
                    
                if point.get('is_group') and 'group_positions' in point:
                    # 如果是门的组合，为每个格子创建碰撞体积
                    for grid_x, grid_y in point['group_positions']:
                        world_x = grid_x * self.tile_size
                        world_y = grid_y * self.tile_size
                        door_rect = pygame.Rect(world_x, world_y, self.tile_size, self.tile_size)
                        door_rects.append(door_rect)
                else:
                    # 单个门，创建碰撞体积
                    grid_x = int(point['pos'][0] // self.tile_size)
                    grid_y = int(point['pos'][1] // self.tile_size)
                    world_x = grid_x * self.tile_size
                    world_y = grid_y * self.tile_size
                    door_rect = pygame.Rect(world_x, world_y, self.tile_size, self.tile_size)
                    door_rects.append(door_rect)
        
        return door_rects

    def toggle_door_at_position(self, world_pos, interaction_range=50):
        """
        在指定位置切换门的开关状态（会打开/关闭所有融合在一起的门）
        :param world_pos: 交互位置
        :param interaction_range: 交互范围
        :return: 是否成功切换了门的状态
        """
        target_pos = pygame.Vector2(world_pos)
        
        for point in self.interact_points:
            if point['type'] == INTERACT_DOOR and not point.get('is_broken', False):
                # Check if interaction point is near any part of this door group
                interaction_found = False
                
                if point.get('is_group') and 'group_positions' in point:
                    # Check all grid positions in the group
                    for grid_x, grid_y in point['group_positions']:
                        group_world_x = grid_x * self.tile_size + self.tile_size // 2
                        group_world_y = grid_y * self.tile_size + self.tile_size // 2
                        group_pos = pygame.Vector2(group_world_x, group_world_y)
                        distance = target_pos.distance_to(group_pos)
                        
                        if distance <= interaction_range:
                            interaction_found = True
                            break
                else:
                    # Single door
                    point_pos = pygame.Vector2(point['pos'])
                    distance = target_pos.distance_to(point_pos)
                    
                    if distance <= interaction_range:
                        interaction_found = True
                
                if interaction_found:
                    new_state = not point.get('is_open', False)
                    point['is_open'] = new_state
                    state_text = "opened" if new_state else "closed"
                    
                    if point.get('is_group') and 'group_positions' in point:
                        print(f"Door group {state_text} with {len(point['group_positions'])} doors")
                    else:
                        print(f"Door {state_text} at {point['pos']}")
                    
                    return True
        
        return False

    def interact_with_chest_or_scroll_at_position(self, world_pos, interaction_range=50):
        """
        在指定位置与宝箱或卷轴交互（按整个交互点给加成）
        :param world_pos: 交互位置
        :param interaction_range: 交互范围
        :return: 交互结果字典，包含类型和详细信息
        """
        target_pos = pygame.Vector2(world_pos)
        
        for point in self.interact_points:
            if point['type'] in [INTERACT_CHEST, INTERACT_SCROLL]:
                # Skip if already collected
                if point.get('is_collected', False):
                    continue
                
                # Check if interaction point is near the center of this item group
                interaction_found = False
                
                # Always use the main point position for interaction detection
                point_pos = pygame.Vector2(point['pos'])
                distance = target_pos.distance_to(point_pos)
                
                if distance <= interaction_range:
                    interaction_found = True
                
                if interaction_found:
                    # Mark as collected
                    point['is_collected'] = True
                    point['collection_time'] = pygame.time.get_ticks()
                    
                    # Calculate group size (1 for single points, actual size for groups)
                    group_size = 1
                    if point.get('is_group') and 'group_positions' in point:
                        group_size = len(point['group_positions'])
                        print(f"Collected {point['type']} group of size {group_size}")
                    else:
                        print(f"Collected {point['type']} at {point['pos']}")
                    
                    # Return interaction result with group size
                    return {
                        'type': point['type'],
                        'pos': point['pos'],
                        'group_size': group_size
                    }
        
        return None

    def damage_door_at_rect(self, damage_rect, damage_amount):
        """
        对指定矩形区域内的门造成伤害（一击破坏）
        :param damage_rect: 伤害矩形
        :param damage_amount: 伤害值（忽略，直接破坏）
        :return: 是否破坏了门
        """
        doors_destroyed = False
        
        for point in self.interact_points:
            if point['type'] == INTERACT_DOOR and not point.get('is_broken', False):
                # Check if damage rect intersects with any part of this door group
                door_hit = False
                
                if point.get('is_group') and 'group_positions' in point:
                    # Check all grid positions in the group
                    for grid_x, grid_y in point['group_positions']:
                        door_world_x = grid_x * self.tile_size
                        door_world_y = grid_y * self.tile_size
                        door_rect = pygame.Rect(door_world_x, door_world_y, self.tile_size, self.tile_size)
                        
                        if damage_rect.colliderect(door_rect):
                            door_hit = True
                            break
                else:
                    # Single door
                    door_grid_x = int(point['pos'][0] // self.tile_size)
                    door_grid_y = int(point['pos'][1] // self.tile_size)
                    door_world_x = door_grid_x * self.tile_size
                    door_world_y = door_grid_y * self.tile_size
                    door_rect = pygame.Rect(door_world_x, door_world_y, self.tile_size, self.tile_size)
                    
                    if damage_rect.colliderect(door_rect):
                        door_hit = True
                
                if door_hit:
                    point['is_broken'] = True
                    point['is_open'] = True  # Broken doors are effectively open
                    doors_destroyed = True
                    
                    if point.get('is_group') and 'group_positions' in point:
                        print(f"Door group destroyed with {len(point['group_positions'])} doors")
                    else:
                        print(f"Door destroyed at {point['pos']}")
        
        return doors_destroyed

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


