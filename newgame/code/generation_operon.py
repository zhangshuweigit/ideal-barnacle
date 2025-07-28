class GenerationOperon:
    """
    Manages the procedural generation of levels, including enemy and item placement.
    """
    def __init__(self, enemy_operon):
        self.enemy_operon = enemy_operon
        # We can add item_operon later

    def generate_level(self, level_layout):
        """
        Generates a level based on a layout dictionary.
        - layout: Contains lists of entities to spawn.
        """
        if 'enemies' in level_layout:
            self.spawn_enemies(level_layout['enemies'])
        
        # Add item spawning logic here later
        # if 'items' in level_layout:
        #     self.spawn_items(level_layout['items'])

    def spawn_enemies(self, enemy_layout):
        """
        Spawns enemies based on a list of definitions.
        - enemy_layout: A list of dicts, e.g., [{'type': 'melee', 'pos': (x, y)}, ...]
        """
        print(f"Spawning {len(enemy_layout)} enemies...")
        for enemy_data in enemy_layout:
            try:
                self.enemy_operon.create_enemy(
                    enemy_type=enemy_data['type'],
                    x=enemy_data['pos'][0],
                    y=enemy_data['pos'][1]
                )
            except KeyError as e:
                print(f"Error spawning enemy: Missing key {e} in {enemy_data}")
