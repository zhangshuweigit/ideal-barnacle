import pygame
from .map_data_operon import INTERACT_DOOR, INTERACT_SCROLL, INTERACT_CHEST

class InteractPointOperon:
    """
    交互点操作子 - 管理地图上的交互点（门、卷轴、宝箱）
    """
    def __init__(self, map_data_operon):
        """
        初始化交互点操作子
        :param map_data_operon: 地图数据操作子实例
        """
        self.map_data = map_data_operon
        self.door_health = {}  # 用于存储门的血量

    def _find_nearby_same_type_points(self, grid_x, grid_y, interact_type):
        """Find nearby points of the same type in all 9 grid cells (3x3 area)."""
        nearby_points = []
        
        # Check all 9 cells (3x3 area centered on current cell)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_grid_x = grid_x + dx
                check_grid_y = grid_y + dy
                
                # Check if there's a point of the same type in this grid cell
                for point in self.map_data.interact_points:
                    if point['type'] == interact_type and not point.get('is_collected', False):
                        # For groups, check all positions in the group
                        if point.get('is_group') and 'group_positions' in point:
                            for group_x, group_y in point['group_positions']:
                                if group_x == check_grid_x and group_y == check_grid_y:
                                    nearby_points.append(point)
                                    break  # Found this point, no need to check other positions
                        else:
                            # Single point
                            point_grid_x = int(point['pos'][0] // self.map_data.tile_size)
                            point_grid_y = int(point['pos'][1] // self.map_data.tile_size)
                            
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
        main_grid_x = int(main_point['pos'][0] // self.map_data.tile_size)
        main_grid_y = int(main_point['pos'][1] // self.map_data.tile_size)
        
        group_positions = [(main_grid_x, main_grid_y)]
        
        for point in nearby_points:
            grid_x = int(point['pos'][0] // self.map_data.tile_size)
            grid_y = int(point['pos'][1] // self.map_data.tile_size)
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
            if point in self.map_data.interact_points:
                self.map_data.interact_points.remove(point)
        
        print(f"Merged {len(nearby_points) + 1} {main_point['type']} points into a group")

    def add_interact_point(self, world_pos, interact_type):
        """Adds a new interactive point (door, scroll, chest) with fixed sizes and auto-merging."""
        # Convert world position to grid coordinates
        grid_x = int(world_pos[0] // self.map_data.tile_size)
        grid_y = int(world_pos[1] // self.map_data.tile_size)
        
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
            center_x * self.map_data.tile_size + self.map_data.tile_size // 2,
            center_y * self.map_data.tile_size + self.map_data.tile_size // 2
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
                    point_grid_x = int(point['pos'][0] // self.map_data.tile_size)
                    point_grid_y = int(point['pos'][1] // self.map_data.tile_size)
                    all_positions.add((point_grid_x, point_grid_y))
            
            # Add the new shape positions
            for pos in shape_positions:
                all_positions.add(pos)
            
            # Calculate the center position of the merged group
            center_x = sum(pos[0] for pos in all_positions) // len(all_positions)
            center_y = sum(pos[1] for pos in all_positions) // len(all_positions)
            center_world_pos = (
                center_x * self.map_data.tile_size + self.map_data.tile_size // 2,
                center_y * self.map_data.tile_size + self.map_data.tile_size // 2
            )
            
            # Remove all the old points
            for point in nearby_points:
                if point in self.map_data.interact_points:
                    self.map_data.interact_points.remove(point)
            
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
            self.map_data.interact_points.append(new_point)
            
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
            self.map_data.interact_points.append(new_point)
            print(f"Added {interact_type} interact point with {len(shape_positions)} tiles at center ({center_x}, {center_y})")

    def get_door_collision_rects(self):
        """
        获取所有门交互点的碰撞体积（仅关闭且未破坏的门）
        :return: 门碰撞体积的矩形列表
        """
        door_rects = []
        
        for point in self.map_data.interact_points:
            if point['type'] == INTERACT_DOOR:
                # Only add collision for doors that are closed and not broken
                if point.get('is_open', False) or point.get('is_broken', False):
                    continue
                    
                if point.get('is_group') and 'group_positions' in point:
                    # 如果是门的组合，为每个格子创建碰撞体积
                    for grid_x, grid_y in point['group_positions']:
                        world_x = grid_x * self.map_data.tile_size
                        world_y = grid_y * self.map_data.tile_size
                        door_rect = pygame.Rect(world_x, world_y, self.map_data.tile_size, self.map_data.tile_size)
                        door_rects.append(door_rect)
                else:
                    # 单个门，创建碰撞体积
                    grid_x = int(point['pos'][0] // self.map_data.tile_size)
                    grid_y = int(point['pos'][1] // self.map_data.tile_size)
                    world_x = grid_x * self.map_data.tile_size
                    world_y = grid_y * self.map_data.tile_size
                    door_rect = pygame.Rect(world_x, world_y, self.map_data.tile_size, self.map_data.tile_size)
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
        
        for point in self.map_data.interact_points:
            if point['type'] == INTERACT_DOOR and not point.get('is_broken', False):
                # Check if interaction point is near any part of this door group
                interaction_found = False
                
                if point.get('is_group') and 'group_positions' in point:
                    # Check all grid positions in the group
                    for grid_x, grid_y in point['group_positions']:
                        group_world_x = grid_x * self.map_data.tile_size + self.map_data.tile_size // 2
                        group_world_y = grid_y * self.map_data.tile_size + self.map_data.tile_size // 2
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
        
        for point in self.map_data.interact_points:
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
        :param damage_amount: 伤害值
        :return: 是否破坏了门
        """
        doors_destroyed = False
        
        for point in self.map_data.interact_points:
            if point['type'] == INTERACT_DOOR and not point.get('is_broken', False):
                # 为每个门设置唯一的ID
                door_id = id(point)
                
                # 初始化门的血量（如果还没有的话）
                if door_id not in self.door_health:
                    self.door_health[door_id] = 30  # 默认30点血量
                
                # Check if damage rect intersects with any part of this door group
                door_hit = False
                
                if point.get('is_group') and 'group_positions' in point:
                    # Check all grid positions in the group
                    for grid_x, grid_y in point['group_positions']:
                        door_world_x = grid_x * self.map_data.tile_size
                        door_world_y = grid_y * self.map_data.tile_size
                        door_rect = pygame.Rect(door_world_x, door_world_y, self.map_data.tile_size, self.map_data.tile_size)
                        
                        if damage_rect.colliderect(door_rect):
                            door_hit = True
                            break
                else:
                    # Single door
                    door_grid_x = int(point['pos'][0] // self.map_data.tile_size)
                    door_grid_y = int(point['pos'][1] // self.map_data.tile_size)
                    door_world_x = door_grid_x * self.map_data.tile_size
                    door_world_y = door_grid_y * self.map_data.tile_size
                    door_rect = pygame.Rect(door_world_x, door_world_y, self.map_data.tile_size, self.map_data.tile_size)
                    
                    if damage_rect.colliderect(door_rect):
                        door_hit = True
                
                if door_hit:
                    # 减少门的血量
                    self.door_health[door_id] -= damage_amount
                    
                    # 如果血量降到0或以下，破坏门
                    if self.door_health[door_id] <= 0:
                        point['is_broken'] = True
                        point['is_open'] = True  # Broken doors are effectively open
                        doors_destroyed = True
                        
                        # 移除门的血量记录
                        if door_id in self.door_health:
                            del self.door_health[door_id]
                        
                        if point.get('is_group') and 'group_positions' in point:
                            print(f"Door group destroyed with {len(point['group_positions'])} doors")
                        else:
                            print(f"Door destroyed at {point['pos']}")
        
        return doors_destroyed