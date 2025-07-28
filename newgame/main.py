import pygame
from code.input_operon import InputOperon
from code.movement_operon import MovementOperon
from code.weapon_operon import WeaponOperon
from code.combat_operon import CombatOperon
from code.enemy_operon import EnemyOperon
from code.generation_operon import GenerationOperon
from code.npc_operon import NPCOperon
from code.ui_operon import UIOperon

# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# --- Game Class ---
class Game:
    """Main game class that orchestrates all game components."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bacterial Roguelite")
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        # Initialize all operons
        self.input_operon = InputOperon()
        self.movement_operon = MovementOperon(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.combat_operon = CombatOperon()
        self.enemy_operon = EnemyOperon(self.combat_operon)
        self.generation_operon = GenerationOperon(self.enemy_operon)
        self.npc_operon = NPCOperon()
        self.weapon_operon = WeaponOperon()
        self.ui_operon = UIOperon()

        # Register player
        self.combat_operon.register_entity(self.movement_operon.player, 100)

        # Generate initial level
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
        """Processes quit events."""
        for event in events:
            if event.type == pygame.QUIT:
                self.is_running = False

    def update(self, events):
        """The main data processing pipeline for the game."""
        actions = self.input_operon.process_input(events)
        self.movement_operon.update(actions)
        actions['player_pos'] = self.movement_operon.player.rect.center
        
        player_attack = self.weapon_operon.attack(actions)
        enemy_attacks = self.enemy_operon.update(self.movement_operon.player)
        
        all_entities = [self.movement_operon.player] + self.enemy_operon.get_all_enemies()
        if player_attack:
            self.combat_operon.process_attack(player_attack, all_entities, self.movement_operon.player)
        for attack in enemy_attacks:
            self.combat_operon.process_attack(attack, all_entities, attack.pop('attacker'))
            
        self.combat_operon.update(all_entities)
        self.npc_operon.update(self.movement_operon.player, actions)
        self.weapon_operon.update(self.movement_operon.player.rect, actions.get('mouse_pos'))

    def render(self):
        """Renders all game objects to the screen."""
        self.screen.fill((20, 20, 30))
        self.movement_operon.draw(self.screen)
        self.enemy_operon.draw(self.screen)
        self.npc_operon.draw(self.screen)
        self.weapon_operon.draw(self.screen)
        self.combat_operon.draw(self.screen)
        
        # Draw UI on top of everything
        all_entities = [self.movement_operon.player] + self.enemy_operon.get_all_enemies()
        self.ui_operon.draw_health_bars(self.screen, all_entities, self.combat_operon)
        
        pygame.display.flip()

# --- Main execution ---
if __name__ == "__main__":
    game = Game()
    game.run()
