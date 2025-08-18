import pygame
from code.input_operon import InputOperon
from code.movement_operon import MovementOperon
from code.weapon_operon import WeaponOperon
from code.combat_operon import CombatOperon
from code.enemy_operon import EnemyOperon
from code.generation_operon import GenerationOperon
from code.npc_operon import NPCOperon
from code.ui_operon import UIOperon
from code.enhanced_ui_operon import EnhancedUIOperon
from code.map_modules.map_data_operon import MapDataOperon, COLLISION, NPC, EMPTY, SPAWN_MELEE, SPAWN_RANGED, SPAWN_WEAPON
from code.map_modules.map_render_operon import MapRenderOperon
from code.map_modules.map_edit_operon import MapEditOperon
from code.map_modules.interact_point_operon import InteractPointOperon, INTERACT_DOOR, INTERACT_SCROLL, INTERACT_CHEST

# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 32

# --- Game Class ---
class Game:
    """Main game class that orchestrates all game components following bacterial code principles."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bacterial Roguelite - Editor Mode")
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.is_edit_mode = True # Start in edit mode
        self.is_paused = False
        self.show_inventory = False
        
        # Initialize all operons
        self._initialize_operons()
        
        # Set camera to center on the player
        self.camera_x = self.movement_operon.player.rect.centerx - SCREEN_WIDTH / 2
        
        # Register player entity and set combat system reference
        self.combat_operon.register_entity(self.movement_operon.player, 100)
        self.movement_operon.player._combat_operon = self.combat_operon
        
        # Load saved currency and upgrades
        self.movement_operon.player.load_currency()
        
        # Generate level using spawn points
        self._generate_level()

    def _initialize_operons(self):
        """Initialize all operons with their dependencies."""
        self.input_operon = InputOperon()
        
        # Map operon initialization
        map_width = 1000
        map_height = SCREEN_HEIGHT // TILE_SIZE
        self.map_data_operon = MapDataOperon(map_width, map_height, TILE_SIZE)
        self.map_data_operon.load_from_file('custom_map.json')
        
        # Map module operons
        self.map_render_operon = MapRenderOperon(self.map_data_operon)
        self.map_edit_operon = MapEditOperon(self.map_data_operon)
        self.interact_point_operon = InteractPointOperon(self.map_data_operon)
        
        # Other operons
        self.movement_operon = MovementOperon(SCREEN_WIDTH, SCREEN_HEIGHT, self.map_data_operon, self.interact_point_operon)
        self.combat_operon = CombatOperon()
        self.enemy_operon = EnemyOperon(self.combat_operon)
        self.generation_operon = GenerationOperon(self.enemy_operon)
        self.npc_operon = NPCOperon()
        self.weapon_operon = WeaponOperon()
        self.ui_operon = UIOperon()
        self.enhanced_ui_operon = EnhancedUIOperon(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Register damage callback
        self.combat_operon.register_damage_callback(self._on_damage_dealt)
        
        # Register kill callback
        self.combat_operon.register_kill_callback(self._on_entity_killed)

    def _generate_level(self):
        """Generate level using spawn points from map or default layout."""
        if self.map_data_operon.spawn_points:
            level_layout = {'enemies': self.map_data_operon.spawn_points}
            self.generation_operon.generate_level(level_layout)
        else:
            print("No spawn points found in map, using default layout.")
            default_layout = {
                'enemies': [
                    {'type': 'melee', 'pos': (600, 625)},
                    {'type': 'ranged', 'pos': (800, 625)},
                ]
            }
            self.generation_operon.generate_level(default_layout)

    def run(self):
        """The main game loop following bacterial principles."""
        try:
            while self.is_running:
                events = pygame.event.get()
                self.handle_events(events)
                self.update_state(events)
                self.render_frame()
                self.clock.tick(FPS)
        except KeyboardInterrupt:
            print("Game interrupted")
        finally:
            # Save currency before quitting
            self._cleanup()
            pygame.quit()

    def handle_events(self, events):
        """Processes quit events and mode switching."""
        for event in events:
            if event.type == pygame.QUIT:
                self.is_running = False
            if event.type == pygame.KEYDOWN:
                self._handle_keydown_events(event)

    def _handle_keydown_events(self, event):
        """Handle keydown events for mode switching."""
        if event.key == pygame.K_TAB:
            self.is_edit_mode = not self.is_edit_mode
            mode = "Editor Mode" if self.is_edit_mode else "Game Mode"
            pygame.display.set_caption(f"Bacterial Roguelite - {mode}")
        elif event.key == pygame.K_ESCAPE:
            # Toggle pause state
            self.is_paused = not getattr(self, 'is_paused', False)
        elif event.key == pygame.K_i:
            # Toggle inventory
            if not self.is_paused:  # Can't open inventory while paused
                self.show_inventory = not self.show_inventory
        elif event.key == pygame.K_s:
            # Manual save (press S to save)
            self.movement_operon.player.save_currency()
        elif event.key == pygame.K_r:
            # Handle respawn when player is dead
            if self.movement_operon.player.is_dead:
                self._handle_player_respawn()
        elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
            # Handle upgrade selection when upgrade is available
            if self.movement_operon.player.can_upgrade:
                self._handle_upgrade_selection(event.key)

    def update_state(self, events):
        """The main data processing pipeline for the game."""
        actions = self.input_operon.process_input(events)
        
        # Update enhanced UI (for animations and effects)
        delta_time = 1.0 / FPS
        self.enhanced_ui_operon.update(delta_time)
        
        # If paused or showing inventory, only handle events and UI updates
        if self.is_paused or self.show_inventory:
            return
        
        # Mode-specific processing
        self._process_mode_logic(actions)
        
        # Always update player movement
        self.movement_operon.update(actions)
        
        # Update camera to follow player
        self._update_camera()

    def _process_mode_logic(self, actions):
        """Process logic based on current mode."""
        if self.is_edit_mode:
            actions['roll'] = False  # Disable roll in edit mode
            self._update_edit_mode(actions)
        else:
            self._update_game_mode(actions)

    def _update_edit_mode(self, actions):
        """Handles updates when in map editor mode."""
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Process map editing when SHIFT is pressed
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and actions.get('mouse_pos'):
            self._process_map_editing(actions, mouse_buttons)
        
        # Process map saving
        if actions.get('save_map'):
            self.map_data_operon.save_to_file('custom_map.json')
            print("Save action triggered!")

    def _process_map_editing(self, actions, mouse_buttons):
        """Process map editing actions."""
        mouse_pos = actions['mouse_pos']
        world_pos = (mouse_pos[0] + self.camera_x, mouse_pos[1])

        # Handle tile editing
        self._handle_tile_editing(mouse_pos, mouse_buttons)
        
        # Handle spawn point editing
        self._handle_spawn_editing(world_pos, actions)
        
        # Handle interact point editing
        self._handle_interact_editing(world_pos, actions)

    def _handle_tile_editing(self, mouse_pos, mouse_buttons):
        """Handle tile editing operations."""
        if mouse_buttons[0]:
            self.map_edit_operon.edit_tile(mouse_pos, self.camera_x, COLLISION)
        elif mouse_buttons[2]:
            self.map_edit_operon.edit_tile(mouse_pos, self.camera_x, NPC)
        elif mouse_buttons[1]:
            self.map_edit_operon.edit_tile(mouse_pos, self.camera_x, EMPTY)

    def _handle_spawn_editing(self, world_pos, actions):
        """Handle spawn point editing operations."""
        if actions.get('add_melee_spawn'):
            self.map_edit_operon.add_spawn_point(world_pos, SPAWN_MELEE)
        elif actions.get('add_ranged_spawn'):
            self.map_edit_operon.add_spawn_point(world_pos, SPAWN_RANGED)
        elif actions.get('add_weapon_spawn'):
            self.map_edit_operon.add_spawn_point(world_pos, SPAWN_WEAPON)
        elif actions.get('remove_spawn_point'):
            self.map_edit_operon.remove_spawn_point_at(world_pos)

    def _handle_interact_editing(self, world_pos, actions):
        """Handle interact point editing operations."""
        if actions.get('add_door_interact'):
            self.interact_point_operon.add_interact_point(world_pos, INTERACT_DOOR)
        elif actions.get('add_scroll_interact'):
            self.interact_point_operon.add_interact_point(world_pos, INTERACT_SCROLL)
        elif actions.get('add_chest_interact'):
            self.interact_point_operon.add_interact_point(world_pos, INTERACT_CHEST)

    def _update_game_mode(self, actions):
        """Handles updates when in normal game mode."""
        # Prepare action data for weapon operon
        actions['player_rect'] = self.movement_operon.player.rect
        actions['camera_x'] = self.camera_x
        
        # Process player attack
        player_attack = self.weapon_operon.attack(actions)
        
        # Update enemies and NPCs
        enemy_attacks = self.enemy_operon.update(self.movement_operon.player, self.map_data_operon)
        self.npc_operon.update(self.movement_operon.player, actions)
        
        # Handle player interactions
        self._handle_player_interactions()
        
        # Process all attacks
        self._process_all_attacks(player_attack, enemy_attacks)
        
        # Update combat systems
        self.combat_operon.update(
            [self.movement_operon.player] + self.enemy_operon.get_all_enemies(),
            self.camera_x,
            self.map_data_operon
        )
        
        # Update weapon operon
        self.weapon_operon.update(self.movement_operon.player.rect, actions.get('mouse_pos'))

    def _handle_player_interactions(self):
        """Handle player interactions with chests and scrolls."""
        if self.movement_operon.player.last_interaction:
            interaction = self.movement_operon.player.last_interaction
            
            if interaction['type'] == 'chest':
                self._handle_chest_interaction(interaction)
            elif interaction['type'] == 'scroll':
                self._handle_scroll_interaction()
            
            # Clear the interaction after processing
            self.movement_operon.player.last_interaction = None

    def _handle_chest_interaction(self, interaction):
        """Handle chest interaction and rewards."""
        reward_info = self.weapon_operon.handle_chest_reward(interaction)
        print(f"Player received {reward_info['new_weapon']} from ancient chest!")
        
        # Add chest notification
        chest_notification = {
            'text': f"Ancient Weapon: {reward_info['new_weapon']}!",
            'start_time': pygame.time.get_ticks(),
            'duration': 4000,
            'color': (255, 215, 0)
        }
        self.movement_operon.player.notifications.append(chest_notification)
        
        # Add item pickup notification to enhanced UI
        self.enhanced_ui_operon.add_item_notification(reward_info['new_weapon'])

    def _handle_scroll_interaction(self):
        """Handle scroll interaction and permanent upgrades."""
        import random
        upgrade_types = ['speed', 'damage', 'jump']
        upgrade_type = random.choice(upgrade_types)
        value = 0.10  # Always 10%
        
        self.movement_operon.player.add_permanent_upgrade(upgrade_type, value)
        print(f"Player received permanent {upgrade_type} upgrade: +{value:.2f} (from ancient scroll)")
        
        # Add item pickup notification to enhanced UI
        display_names = {'speed': '速度', 'damage': '伤害', 'jump': '跳跃'}
        upgrade_name = display_names.get(upgrade_type, upgrade_type)
        self.enhanced_ui_operon.add_item_notification(f"永久{upgrade_name}提升")

    def _process_all_attacks(self, player_attack, enemy_attacks):
        """Process all attacks from player and enemies."""
        all_entities = [self.movement_operon.player] + self.enemy_operon.get_all_enemies()
        
        if player_attack:
            self.combat_operon.process_attack(
                player_attack,
                all_entities,
                self.movement_operon.player,
                self.map_data_operon
            )
        
        for attack in enemy_attacks:
            attacker = attack.pop('attacker')
            self.combat_operon.process_attack(attack, all_entities, attacker, self.map_data_operon)

    def _update_camera(self):
        """Update camera to follow player - creates infinite scroll effect."""
        player_screen_x = self.movement_operon.player.rect.centerx - self.camera_x
        
        if player_screen_x > SCREEN_WIDTH * 0.6:
            self.camera_x += player_screen_x - SCREEN_WIDTH * 0.6
        if player_screen_x < SCREEN_WIDTH * 0.4:
            self.camera_x += player_screen_x - SCREEN_WIDTH * 0.4

    def _get_nearby_interactable(self):
        """Get the nearest interactable object to the player."""
        player = self.movement_operon.player
        interaction_range = 50
        
        # Check NPCs
        for npc in self.npc_operon.npcs:
            distance = pygame.Vector2(player.rect.center).distance_to(pygame.Vector2(npc.rect.center))
            if distance <= interaction_range:
                return npc
        
        # Check interact points (doors, chests, scrolls)
        if self.interact_point_operon:
            player_world_pos = (player.rect.centerx, player.rect.centery)
            target_pos = pygame.Vector2(player_world_pos)
            
            for point in self.interact_point_operon.map_data.interact_points:
                if point.get('is_collected', False):
                    continue
                    
                point_pos = pygame.Vector2(point['pos'])
                distance = target_pos.distance_to(point_pos)
                
                if distance <= interaction_range:
                    return point
        
        return None

    def _on_damage_dealt(self, target_entity, damage, attacker_entity, is_critical):
        """Callback when damage is dealt to an entity."""
        # Add damage number to UI
        if hasattr(target_entity, 'rect'):
            screen_x = target_entity.rect.centerx - self.camera_x
            screen_y = target_entity.rect.top - 20
            self.enhanced_ui_operon.add_damage_number(damage, screen_x, screen_y, is_critical)
        
        # If player is hit, trigger hit effect
        if target_entity == self.movement_operon.player:
            self.enhanced_ui_operon.trigger_hit_effect()
            
            # Check for low health
            health_system = self.combat_operon.health_systems.get(target_entity)
            if health_system and health_system.current_hp / health_system.max_hp < 0.3:
                self.enhanced_ui_operon.trigger_low_health()

    def _on_entity_killed(self, target_entity, attacker_entity):
        """Callback when an entity is killed."""
        # If player killed an enemy, give currency reward
        if attacker_entity == self.movement_operon.player and target_entity != self.movement_operon.player:
            # Determine currency reward based on enemy type
            reward = 10  # Base reward
            
            # Increase reward for different enemy types
            if hasattr(target_entity, '__class__'):
                class_name = target_entity.__class__.__name__
                if 'Ranged' in class_name:
                    reward = 15
                elif 'Shield' in class_name:
                    reward = 20
            
            self.movement_operon.player.add_currency(reward)

    def _handle_player_respawn(self):
        """Handle player respawn after death."""
        # Reload saved currency and upgrades
        self.movement_operon.player.load_currency()
        
        # Reset player position
        spawn_x = self.movement_operon.respawn_player(100, 500)
        
        # Reset camera to follow respawned player
        self.camera_x = spawn_x - SCREEN_WIDTH / 2
        
        # Reset player health
        if self.movement_operon.player in self.combat_operon.health_systems:
            health_system = self.combat_operon.health_systems[self.movement_operon.player]
            health_system.current_hp = health_system.max_hp
        
        # Clear enemies and regenerate level
        self.enemy_operon.clear_all_enemies()
        self._generate_level()
        
        print("Player respawned at starting position")

    def _handle_upgrade_selection(self, key):
        """Handle upgrade selection when player chooses an upgrade."""
        player = self.movement_operon.player
        
        # Map keys to attributes
        upgrade_map = {
            pygame.K_1: {'attr': 'speed', 'value': 0.15},
            pygame.K_2: {'attr': 'damage', 'value': 0.15},
            pygame.K_3: {'attr': 'jump', 'value': 0.15}
        }
        
        if key in upgrade_map:
            upgrade_data = upgrade_map[key]
            
            # Spend currency and apply upgrade
            if player.spend_currency_on_upgrade():
                player.upgrade_attribute(upgrade_data['attr'], upgrade_data['value'])
                print(f"Applied upgrade: {upgrade_data['attr']} +{upgrade_data['value']:.2f}")
            else:
                print("Failed to apply upgrade - not enough currency")

    def _cleanup(self):
        """Save currency before game closes."""
        print("Saving game progress...")
        self.movement_operon.player.save_currency()
        print("Game saved successfully!")

    def render_frame(self):
        """Renders all game objects to the screen."""
        # Clear screen
        self.screen.fill((20, 20, 30))
        
        # Draw map and game entities
        self._render_game_world()
        
        # Draw UI elements
        self._render_ui()
        
        # Present frame
        pygame.display.flip()

    def _render_game_world(self):
        """Render the game world including map and entities."""
        self.map_render_operon.draw_grid(self.screen, self.camera_x)
        self.movement_operon.draw(self.screen, self.camera_x)
        self.enemy_operon.draw(self.screen, self.camera_x)
        self.npc_operon.draw(self.screen, self.camera_x)
        self.weapon_operon.draw(self.screen, self.camera_x)
        self.combat_operon.draw(self.screen, self.camera_x)

    def _render_ui(self):
        """Render all UI elements using the enhanced UI operon."""
        # Get nearby interactable for interaction prompts
        nearby_interactable = self._get_nearby_interactable()
        
        # Check if player is dead
        player_dead = (self.movement_operon.player not in self.combat_operon.health_systems or
                      self.combat_operon.health_systems[self.movement_operon.player].is_dead())
        
        # Draw enhanced UI
        self.enhanced_ui_operon.draw(
            self.screen, 
            self.movement_operon.player, 
            self.weapon_operon,
            is_paused=self.is_paused,
            is_dead=player_dead,
            nearby_interactable=nearby_interactable,
            show_inventory=self.show_inventory
        )

# --- Main execution ---
if __name__ == "__main__":
    game = Game()
    game.run()
