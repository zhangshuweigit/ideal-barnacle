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
            'move_dir': 0, 'jump': False, 'interact': False, 'roll': False, 'save_map': False,
            'add_melee_spawn': False, 'add_ranged_spawn': False, 'remove_spawn_point': False,
            'add_weapon_spawn': False,
            'add_door_interact': False, 'add_scroll_interact': False, 'add_chest_interact': False,
            'active_slot': None, 'is_skill': False, 'attack': False,
            'mouse_pos': pygame.mouse.get_pos() if pygame.mouse.get_focused() else None
        }

    def _handle_key_press_events(self, event, actions):
        """Handles KEYDOWN events for single-press actions."""
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            is_shift = mods & pygame.KMOD_SHIFT
            is_ctrl = mods & pygame.KMOD_CTRL
            is_alt = mods & pygame.KMOD_ALT

            # --- Editor Shortcuts ---
            if event.key == pygame.K_s and is_ctrl:
                actions['save_map'] = True
                return
            if is_shift and event.key == pygame.K_SPACE:
                actions['add_melee_spawn'] = True
                return
            if is_shift and event.key == pygame.K_w: # SHIFT + W for Weapon
                actions['add_weapon_spawn'] = True
                return
            if is_shift and is_alt: # Using a more general check for Shift+Alt
                actions['add_ranged_spawn'] = True
                return

            # --- Editor Shortcuts for Interact Points ---
            if is_shift and event.key == pygame.K_d: # SHIFT + D for Door
                actions['add_door_interact'] = True
                return
            if is_shift and event.key == pygame.K_q: # SHIFT + Q for Scroll
                actions['add_scroll_interact'] = True
                return
            if is_shift and event.key == pygame.K_c: # SHIFT + C for Chest
                actions['add_chest_interact'] = True
                return

            # --- Gameplay Actions ---
            if event.key == self.key_map['sub_1']:
                actions['active_slot'] = 'sub_1'
            elif event.key == self.key_map['sub_2']:
                actions['active_slot'] = 'sub_2'
            elif event.key == self.key_map['roll']:
                actions['roll'] = True

    def _handle_mouse_events(self, event, actions):
        """Handles MOUSEBUTTONDOWN and MOUSEBUTTONUP events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # --- Editor Action: Remove Spawn Point ---
            if event.button == 3 and (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                actions['remove_spawn_point'] = True
                return

            if event.button in self.mouse_map:
                slot = self.mouse_map[event.button]
                self.mouse_down_times[slot] = pygame.time.get_ticks()
                self.skill_triggered[slot] = False
                # 设置攻击状态
                actions['attack'] = True
                actions['active_slot'] = slot

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button in self.mouse_map:
                slot = self.mouse_map[event.button]
                if slot in self.mouse_down_times:
                    duration = (pygame.time.get_ticks() - self.mouse_down_times[slot]) / 1000.0
                    if duration < 0.5:
                        actions['active_slot'] = slot
                        actions['is_skill'] = False
                    self.mouse_down_times.pop(slot, None)


    def _update_long_presses(self, actions):
        """Checks for and triggers skill attacks on long presses."""
        for slot, start_time in list(self.mouse_down_times.items()):
            if not self.skill_triggered.get(slot):
                duration = (pygame.time.get_ticks() - start_time) / 1000.0
                if duration >= 0.5:
                    actions['active_slot'] = slot
                    actions['is_skill'] = True
                    self.skill_triggered[slot] = True
