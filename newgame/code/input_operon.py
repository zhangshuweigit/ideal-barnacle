import pygame

class InputOperon:
    """
    输入操纵子 - 处理所有玩家输入。
    """
    def __init__(self):
        self.key_map = {
            'move_left': pygame.K_a, 'move_right': pygame.K_d,
            'jump': pygame.K_SPACE, 'interact': pygame.K_e,
            'sub_1': pygame.K_1, 'sub_2': pygame.K_2,
            'roll': pygame.K_LSHIFT
        }
        self.mouse_map = { 1: 'main_1', 3: 'main_2' }
        self.mouse_down_times = {}
        self.skill_triggered = {}

    def process_input(self, events):
        """
        处理所有输入，并返回一个清晰、独立的动作字典。
        """
        actions = self._get_default_actions()
        keys = pygame.key.get_pressed()

        actions['move_dir'] = keys[self.key_map['move_right']] - keys[self.key_map['move_left']]
        actions['jump'] = keys[self.key_map['jump']]
        actions['interact'] = keys[self.key_map['interact']]

        for event in events:
            self._handle_mouse_events(event, actions)
            self._handle_key_press_events(event, actions)
        
        self._update_long_presses(actions)
        
        return actions

    def _get_default_actions(self):
        """Creates a clean dictionary for the current frame's actions."""
        return {
            'move_dir': 0, 'jump': False, 'interact': False, 'roll': False,
            'active_slot': None, 'is_skill': False,
            'mouse_pos': pygame.mouse.get_pos()
        }

    def _handle_mouse_events(self, event, actions):
        """Handles MOUSEBUTTONDOWN and MOUSEBUTTONUP events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in self.mouse_map:
                slot = self.mouse_map[event.button]
                self.mouse_down_times[slot] = pygame.time.get_ticks()
                self.skill_triggered[slot] = False
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button in self.mouse_map:
                slot = self.mouse_map[event.button]
                if slot in self.mouse_down_times:
                    duration = (pygame.time.get_ticks() - self.mouse_down_times[slot]) / 1000.0
                    if duration < 0.5:
                        actions['active_slot'] = slot
                        actions['is_skill'] = False
                    self.mouse_down_times.pop(slot, None)

    def _handle_key_press_events(self, event, actions):
        """Handles KEYDOWN events for single-press actions."""
        if event.type == pygame.KEYDOWN:
            if event.key == self.key_map['sub_1']:
                actions['active_slot'] = 'sub_1'
            elif event.key == self.key_map['sub_2']:
                actions['active_slot'] = 'sub_2'
            elif event.key == self.key_map['roll']:
                actions['roll'] = True

    def _update_long_presses(self, actions):
        """Checks for and triggers skill attacks on long presses."""
        for slot, start_time in list(self.mouse_down_times.items()):
            if not self.skill_triggered.get(slot):
                duration = (pygame.time.get_ticks() - start_time) / 1000.0
                if duration >= 0.5:
                    actions['active_slot'] = slot
                    actions['is_skill'] = True
                    self.skill_triggered[slot] = True
