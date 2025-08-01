import pygame
from code.input_operon import InputOperon
from code.movement_operon import MovementOperon
from code.weapon_operon import WeaponOperon
from code.combat_operon import CombatOperon
from code.enemy_operon import EnemyOperon
from code.generation_operon import GenerationOperon
from code.npc_operon import NPCOperon
from code.ui_operon import UIOperon
from code.map_operon import MapOperon, COLLISION, NPC, EMPTY, SPAWN_MELEE, SPAWN_RANGED, SPAWN_WEAPON

# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 32

# --- Game Class ---
class Game:
    """Main game class that orchestrates all game components."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bacterial Roguelite - Editor Mode")
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.is_edit_mode = True # Start in edit mode
        
        # --- Operon Initialization ---
        self.input_operon = InputOperon()
        
        # Define map size; the "world" is now conceptually larger due to the offset
        map_width = 1000 # Keep a long map
        map_height = SCREEN_HEIGHT // TILE_SIZE
        self.map_operon = MapOperon(map_width, map_height, TILE_SIZE)
        
        self.map_operon.load_from_file('custom_map.json')
        
        self.movement_operon = MovementOperon(SCREEN_WIDTH, SCREEN_HEIGHT, self.map_operon)
        self.combat_operon = CombatOperon()
        self.enemy_operon = EnemyOperon(self.combat_operon)
        self.generation_operon = GenerationOperon(self.enemy_operon)
        self.npc_operon = NPCOperon()
        self.weapon_operon = WeaponOperon()
        self.ui_operon = UIOperon()

        # --- Camera/Player Setup ---
        # Set camera to center on the player
        self.camera_x = self.movement_operon.player.rect.centerx - SCREEN_WIDTH / 2
        # Register player
        self.combat_operon.register_entity(self.movement_operon.player, 100)
        
        # This default layout is only used if custom_map.json doesn't exist.
        # We must apply the offset here too so it appears in the correct place.
        if not self.map_operon.spawn_points: # A simple check to see if a map was loaded
            level_1_layout = {
                'enemies': [
                    {'type': 'melee', 'pos': (600, 625)},
                    {'type': 'ranged', 'pos': (800, 625)},
                ]
            }
            self.generation_operon.generate_level(level_1_layout)

    def run(self):
        """The main game loop."""
        while self.is_running:
            events = pygame.event.get()
            self.handle_events(events)
            self.update(events)
            self.render()
            self.clock.tick(FPS)
        pygame.quit()

    def handle_events(self, events):
        """Processes quit events and mode switching."""
        for event in events:
            if event.type == pygame.QUIT:
                self.is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB: # TAB key to toggle edit mode
                    self.is_edit_mode = not self.is_edit_mode
                    caption = "Editor Mode" if self.is_edit_mode else "Game Mode"
                    pygame.display.set_caption(f"Bacterial Roguelite - {caption}")

    def update(self, events):
        """The main data processing pipeline for the game."""
        actions = self.input_operon.process_input(events)
        
        # --- Mode-Specific Logic ---
        # Crucially, disable roll *before* it's processed by the movement operon.
        if self.is_edit_mode:
            actions['roll'] = False
            self.update_edit_mode(actions)
        else:
            self.update_game_mode(actions)

        # Player movement is always active, now receives correctly filtered actions
        self.movement_operon.update(actions)
            
        # Update camera to follow player - creates infinite scroll effect
        player_screen_x = self.movement_operon.player.rect.centerx - self.camera_x
        if player_screen_x > SCREEN_WIDTH * 0.6:
            self.camera_x += player_screen_x - SCREEN_WIDTH * 0.6
        if player_screen_x < SCREEN_WIDTH * 0.4:
            self.camera_x += player_screen_x - SCREEN_WIDTH * 0.4

    def update_edit_mode(self, actions):
        """Handles updates when in map editor mode."""
        # Disable roll in edit mode
        actions['roll'] = False
        
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Check for SHIFT key for editing
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if 'mouse_pos' in actions and actions['mouse_pos']:
                mouse_pos = actions['mouse_pos']
                world_pos = (mouse_pos[0] + self.camera_x, mouse_pos[1])

                # --- Tile Editing ---
                if mouse_buttons[0]:
                    self.map_operon.edit_tile(mouse_pos, self.camera_x, COLLISION)
                elif mouse_buttons[2]:
                    self.map_operon.edit_tile(mouse_pos, self.camera_x, NPC)
                elif mouse_buttons[1]:
                    self.map_operon.edit_tile(mouse_pos, self.camera_x, EMPTY)

                # --- Spawn Point Editing ---
                if actions.get('add_melee_spawn'):
                    self.map_operon.add_spawn_point(world_pos, SPAWN_MELEE)
                elif actions.get('add_ranged_spawn'):
                    self.map_operon.add_spawn_point(world_pos, SPAWN_RANGED)
                elif actions.get('add_weapon_spawn'):
                    self.map_operon.add_spawn_point(world_pos, SPAWN_WEAPON)
                elif actions.get('remove_spawn_point'):
                    self.map_operon.remove_spawn_point_at(world_pos)

        # --- Save map action ---
        if actions.get('save_map'):
            self.map_operon.save_to_file('custom_map.json')
            print("Save action triggered!") # For debugging

    def update_game_mode(self, actions):
        """Handles updates when in normal game mode."""
        # The new weapon operon is self-contained. We just need to pass it the raw data.
        actions['player_rect'] = self.movement_operon.player.rect
        actions['camera_x'] = self.camera_x
        
        player_attack = self.weapon_operon.attack(actions)
        
        # In game mode, enemies and NPCs are active
        enemy_attacks = self.enemy_operon.update(self.movement_operon.player)
        self.npc_operon.update(self.movement_operon.player, actions)
        
        all_entities = [self.movement_operon.player] + self.enemy_operon.get_all_enemies()
        if player_attack:
            self.combat_operon.process_attack(player_attack, all_entities, self.movement_operon.player)
        for attack in enemy_attacks:
            self.combat_operon.process_attack(attack, all_entities, attack.pop('attacker'))
            
        self.combat_operon.update(all_entities, self.camera_x)
        # We still call weapon_operon.update for its internal state machine (e.g., melee timer)
        self.weapon_operon.update(self.movement_operon.player.rect, actions.get('mouse_pos'))

    def render(self):
        """Renders all game objects to the screen."""
        self.screen.fill((20, 20, 30))
        
        # Draw the map grid, adjusted by camera
        self.map_operon.draw_grid(self.screen, self.camera_x)
        
        # Draw game entities, adjusted by camera
        # Note: This requires modifying their draw methods to accept a camera offset
        self.movement_operon.draw(self.screen, self.camera_x)
        self.enemy_operon.draw(self.screen, self.camera_x)
        self.npc_operon.draw(self.screen, self.camera_x)
        self.weapon_operon.draw(self.screen, self.camera_x)
        self.combat_operon.draw(self.screen, self.camera_x)
        
        # Draw UI on top, which is not affected by the camera
        all_entities = [self.movement_operon.player] + self.enemy_operon.get_all_enemies()
        self.ui_operon.draw_health_bars(self.screen, all_entities, self.combat_operon, self.camera_x)
        
        pygame.display.flip()

# --- Main execution ---
if __name__ == "__main__":
    game = Game()
    game.run()
