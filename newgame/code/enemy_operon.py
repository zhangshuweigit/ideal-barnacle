import pygame
import random

class Enemy(pygame.sprite.Sprite):
    """Base class for all enemy types."""
    def __init__(self, x, y, color, size=(30, 50)):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Combat properties
        self.attack_cooldown = 2000
        self.last_attack_time = 0
        self.is_attacking = False
        self.attack_duration = 0
        self.attack_timer = 0
        self.attack_hitbox = None
        
        # Physics properties (same as player)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.speed = 2
        
        # AI properties
        self.detection_range = 300  # Detection range for player
        self.has_detected_player = False
        self.is_aggressive = False  # Becomes aggressive when attacked
        self.aggressive_timer = 0  # Timer for aggressive state
        self.aggressive_duration = 5000  # 5 seconds of aggressive behavior
        
        # Patrol properties
        self.patrol_center = pygame.Vector2(self.rect.center)  # Center of patrol area
        self.patrol_radius = 150  # Patrol radius around center
        self.patrol_speed = 1  # Slower speed when patrolling
        self.patrol_direction = 1  # 1 for right, -1 for left
        self.patrol_wait_timer = 0  # Timer for waiting at patrol endpoints
        self.patrol_wait_duration = 2000  # 2 seconds wait at endpoints

    def can_attack(self):
        return pygame.time.get_ticks() - self.last_attack_time > self.attack_cooldown

    def perform_attack(self, player):
        return None

    def update(self, player, map_operon=None):
        # --- Physics Update ---
        self.update_physics(map_operon)
        
        # --- AI Update ---
        self.update_ai(player)
        
        # --- Combat Update ---
        if self.is_attacking:
            if pygame.time.get_ticks() - self.attack_timer > self.attack_duration:
                self.is_attacking = False
                self.attack_hitbox = None
            else:
                self._update_hitbox(player)

    def _update_hitbox(self, player):
        pass
    
    def update_physics(self, map_operon):
        """Update enemy physics - gravity and collision detection"""
        # Apply gravity
        self.velocity.y += 0.5  # Same gravity as player
        if self.velocity.y > 10: 
            self.velocity.y = 10
        
        # Horizontal collision
        self.rect.x += self.velocity.x
        if map_operon:
            collision_rects = self._get_collision_rects(map_operon)
            for rect in collision_rects:
                if self.rect.colliderect(rect):
                    if self.velocity.x > 0:
                        self.rect.right = rect.left
                    elif self.velocity.x < 0:
                        self.rect.left = rect.right
                    self.velocity.x = 0
        
        # Vertical collision
        self.rect.y += self.velocity.y
        self.on_ground = False
        if map_operon:
            collision_rects = self._get_collision_rects(map_operon)
            for rect in collision_rects:
                if self.rect.colliderect(rect):
                    if self.velocity.y > 0:
                        self.rect.bottom = rect.top
                        self.on_ground = True
                    elif self.velocity.y < 0:
                        self.rect.top = rect.bottom
                    self.velocity.y = 0
    
    def _get_collision_rects(self, map_operon):
        """Get collision rects around enemy (similar to player)"""
        if not map_operon:
            return []
        
        collision_rects = []
        player_gx = int(self.rect.centerx // map_operon.tile_size)
        player_gy = int(self.rect.centery // map_operon.tile_size)

        # Get tile collision rects
        for x_offset in range(-2, 3):
            for y_offset in range(-2, 3):
                world_x = (player_gx + x_offset) * map_operon.tile_size
                world_y = (player_gy + y_offset) * map_operon.tile_size
                
                tile_type = map_operon.get_tile(world_x, world_y)
                if tile_type == 1:  # COLLISION tile
                    collision_rects.append(pygame.Rect(world_x, world_y, map_operon.tile_size, map_operon.tile_size))
        
        return collision_rects
    
    def update_ai(self, player):
        """Basic AI behavior - to be overridden by subclasses"""
        # Default behavior: check if player is in detection range
        distance = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player.rect.center))
        self.has_detected_player = distance <= self.detection_range
        
        # Update aggressive state
        if self.is_aggressive:
            current_time = pygame.time.get_ticks()
            if current_time - self.aggressive_timer > self.aggressive_duration:
                self.is_aggressive = False
                print("Enemy is no longer aggressive")
    
    def take_damage(self, amount):
        """Handle taking damage - becomes aggressive"""
        # This will be called by combat system when enemy takes damage
        self.is_aggressive = True
        self.aggressive_timer = pygame.time.get_ticks()
        print("Enemy became aggressive after taking damage!")
    
    def update_patrol_behavior(self):
        """Update patrol behavior when player is not detected and not aggressive"""
        current_time = pygame.time.get_ticks()
        
        # Check if waiting at endpoint
        if self.patrol_wait_timer > 0:
            if current_time - self.patrol_wait_timer > self.patrol_wait_duration:
                self.patrol_wait_timer = 0
                self.patrol_direction *= -1  # Reverse direction
                print("Enemy finished waiting, changing patrol direction")
            return
        
        # Calculate distance from patrol center
        distance_from_center = abs(self.rect.centerx - self.patrol_center.x)
        
        # Check if reached patrol boundary
        if distance_from_center >= self.patrol_radius:
            # Wait at endpoint
            self.patrol_wait_timer = current_time
            self.velocity.x = 0
            print("Enemy reached patrol boundary, waiting...")
        else:
            # Continue patrol
            self.velocity.x = self.patrol_direction * self.patrol_speed

    def draw(self, screen, camera_x=0):
        # Adjust drawing position based on camera
        adjusted_rect = self.rect.copy()
        adjusted_rect.x -= camera_x
        screen.blit(self.image, adjusted_rect)
        
        # Draw health bar if enemy has health system
        if hasattr(self, '_combat_operon') and self._combat_operon:
            health_system = self._combat_operon.health_systems.get(self)
            if health_system and health_system.current_hp < health_system.max_hp:
                self._draw_health_bar(screen, adjusted_rect, health_system.current_hp, health_system.max_hp)

    def _draw_health_bar(self, screen, rect, current_hp, max_hp):
        """Draw health bar above enemy"""
        bar_width = 30
        bar_height = 4
        bar_x = rect.centerx - bar_width // 2
        bar_y = rect.top - 10
        
        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (50, 50, 50), bg_rect)
        
        # Health fill
        health_percentage = current_hp / max_hp
        fill_width = int(bar_width * health_percentage)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        
        # Color based on health percentage
        if health_percentage > 0.5:
            color = (0, 255, 0)  # Green
        elif health_percentage > 0.25:
            color = (255, 165, 0)  # Orange
        else:
            color = (255, 0, 0)  # Red
            
        pygame.draw.rect(screen, color, fill_rect)

    def draw_attack(self, screen, camera_x=0):
        if self.is_attacking and self.attack_hitbox:
            adjusted_hitbox = self.attack_hitbox.copy()
            adjusted_hitbox.x -= camera_x
            pygame.draw.rect(screen, (255, 0, 0, 150), adjusted_hitbox)

class MeleeEnemy(Enemy):
    """Enemy that moves towards the player to attack."""
    def __init__(self, x, y):
        super().__init__(x, y, (255, 100, 100))
        self.speed = 2
        self.attack_range = 50
        self.damage = 10
        self.attack_duration = 300

    def update(self, player, map_operon=None):
        # Call parent update with map_operon for physics
        super().update(player, map_operon)
        
        # Only perform AI behavior when not attacking
        if not self.is_attacking:
            self.update_melee_ai(player)

    def perform_attack(self, player):
        if self.can_attack() and not self.is_attacking and self.rect.colliderect(player.rect.inflate(self.attack_range, self.attack_range)):
            self.last_attack_time = pygame.time.get_ticks()
            self.is_attacking = True
            self.attack_timer = pygame.time.get_ticks()
            direction = pygame.Vector2(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery).normalize()
            return {'type': 'melee', 'damage': self.damage, 'range': self.attack_range, 'direction': direction}
        return None
    
    def update_melee_ai(self, player):
        """Melee enemy AI - chase player if detected"""
        # Chase if detected or aggressive
        if self.has_detected_player or self.is_aggressive:
            # Calculate direction to player
            direction_vector = pygame.Vector2(player.rect.centerx - self.rect.centerx, 0)
            if direction_vector.length() > 0:
                direction_vector = direction_vector.normalize()
                self.velocity.x = direction_vector.x * self.speed
                
                # Jump if player is above and enemy is on ground
                if (player.rect.centery < self.rect.centery - 20 and 
                    self.on_ground and 
                    random.random() < 0.02):  # 2% chance to jump
                    self.velocity.y = -10  # Same jump strength as player
        else:
            # Player not detected or aggressive, implement patrol behavior
            self.update_patrol_behavior()

    def _update_hitbox(self, player):
        direction = 1 if player.rect.centerx > self.rect.centerx else -1
        hitbox_x = self.rect.centerx if direction == 1 else self.rect.centerx - self.attack_range
        self.attack_hitbox = pygame.Rect(hitbox_x, self.rect.centery - 10, self.attack_range, 20)

class RangedEnemy(Enemy):
    """Enemy that keeps a distance and shoots projectiles."""
    def __init__(self, x, y):
        super().__init__(x, y, (100, 255, 100))
        self.speed = 1
        self.optimal_distance = 250
        self.damage = 5

    def update(self, player, map_operon=None):
        # Call parent update with map_operon for physics
        super().update(player, map_operon)
        
        # Only perform AI behavior when not attacking
        if not self.is_attacking:
            self.update_ranged_ai(player)
            
    def perform_attack(self, player):
        if self.can_attack() and not self.is_attacking:
            self.last_attack_time = pygame.time.get_ticks()
            
            # Calculate the precise direction vector towards the player
            player_pos = pygame.Vector2(player.rect.center)
            enemy_pos = pygame.Vector2(self.rect.center)
            direction = (player_pos - enemy_pos).normalize() if (player_pos - enemy_pos).length() > 0 else pygame.Vector2(1, 0)

            return {'type': 'projectile', 'damage': self.damage, 'speed': 8, 'direction': direction}
        return None
    
    def update_ranged_ai(self, player):
        """Ranged enemy AI - maintain optimal distance and attack when player is visible"""
        # Check if player is in line of sight (visual range larger than smell range)
        visual_range = 500  # Visual range is larger than detection range
        distance_to_player = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player.rect.center))
        player_visible = distance_to_player <= visual_range
        
        if player_visible:
            # Calculate distance to player
            distance = self.rect.centerx - player.rect.centerx
            abs_distance = abs(distance)
            
            # Try to maintain optimal distance
            if abs_distance < self.optimal_distance - 30:
                # Too close, move away
                self.velocity.x = -self.speed if distance > 0 else self.speed
            elif abs_distance > self.optimal_distance + 30:
                # Too far, move closer
                self.velocity.x = self.speed if distance > 0 else -self.speed
            else:
                # Good distance, stop moving
                self.velocity.x = 0
            
            # Attack if can attack (no need for specific range check - perform_attack handles it)
            if self.can_attack():
                attack = self.perform_attack(player)
                if attack:
                    self.is_attacking = True
                    self.attack_timer = pygame.time.get_ticks()
        else:
            # Player not visible, implement patrol behavior
            self.velocity.x = 0  # Will be handled by patrol behavior

class ShieldEnemy(Enemy):
    """Enemy with a shield that blocks attacks."""
    def __init__(self, x, y):
        super().__init__(x, y, (100, 100, 255), size=(50, 50))
        self.is_shielding = False

    def update(self, player, map_operon=None):
        # Call parent update with map_operon for physics
        super().update(player, map_operon)
        
        # Only perform AI behavior when not attacking
        if not self.is_attacking:
            self.update_shield_ai(player)
    
    def update_shield_ai(self, player):
        """Shield enemy AI - toggle shield and approach player"""
        # Toggle shield randomly
        if random.random() < 0.01:
            self.is_shielding = not self.is_shielding
            
        if self.is_shielding:
            self.image.fill((50, 50, 150))
        else:
            self.image.fill((100, 100, 255))
        
        # Move towards player if detected or aggressive
        if self.has_detected_player or self.is_aggressive:
            direction_vector = pygame.Vector2(player.rect.centerx - self.rect.centerx, 0)
            if direction_vector.length() > 0:
                direction_vector = direction_vector.normalize()
                self.velocity.x = direction_vector.x * self.speed
        else:
            # Player not detected or aggressive, implement patrol behavior
            self.update_patrol_behavior()
    
    def take_damage(self, amount):
        """Handle taking damage - becomes aggressive"""
        super().take_damage(amount)
        print("Shield enemy became aggressive!")

class EnemyOperon:
    """Manages all enemies and collects their attack data."""
    def __init__(self, combat_operon):
        self.enemies = pygame.sprite.Group()
        self.combat_operon = combat_operon

    def create_enemy(self, enemy_type, x, y):
        enemy_map = {'melee': MeleeEnemy, 'ranged': RangedEnemy, 'shield': ShieldEnemy}
        if enemy_type in enemy_map:
            new_enemy = enemy_map[enemy_type](x, y)
            self.enemies.add(new_enemy)
            self.combat_operon.register_entity(new_enemy, 100)

    def update(self, player, map_operon=None):
        attack_list = []
        for enemy in self.enemies:
            enemy.update(player, map_operon)
            attack_data = enemy.perform_attack(player)
            if attack_data:
                attack_data['attacker'] = enemy
                attack_list.append(attack_data)
        return attack_list

    def draw(self, screen, camera_x=0):
        for enemy in self.enemies:
            enemy.draw(screen, camera_x)
            enemy.draw_attack(screen, camera_x)

    def get_all_enemies(self):
        return list(self.enemies)
    
    def clear_all_enemies(self):
        """Clear all enemies from the game"""
        self.enemies.empty()
        
    def save_enemies(self, filename):
        """Save current enemy states to file."""
        import json
        enemy_data = []
        for enemy in self.enemies:
            enemy_info = {
                'type': enemy.__class__.__name__,
                'x': enemy.rect.x,
                'y': enemy.rect.y,
                'health': getattr(enemy, 'health', 100),  # Assuming default health of 100
                # Add other enemy-specific attributes as needed
            }
            enemy_data.append(enemy_info)
        
        try:
            with open(filename, 'w') as f:
                json.dump(enemy_data, f)
            print(f"Saved {len(enemy_data)} enemies to {filename}")
        except Exception as e:
            print(f"Failed to save enemies: {e}")
    
    def load_enemies(self, filename, combat_operon):
        """Load enemy states from file."""
        import json
        try:
            with open(filename, 'r') as f:
                enemy_data = json.load(f)
            
            # Clear existing enemies
            self.clear_all_enemies()
            
            # Spawn enemies from saved data
            for data in enemy_data:
                enemy_type = data.get('type', 'melee').lower()
                x = data.get('x', 0)
                y = data.get('y', 0)
                
                # Create enemy based on type
                self.create_enemy(enemy_type, x, y)
                
                # Restore enemy health if combat system is available
                if combat_operon:
                    # This would need to be expanded to restore health properly
                    pass
                    
            print(f"Loaded {len(enemy_data)} enemies from {filename}")
            return True
        except FileNotFoundError:
            print(f"No enemy save file {filename} found")
            return False
        except Exception as e:
            print(f"Failed to load enemies: {e}")
            return False
