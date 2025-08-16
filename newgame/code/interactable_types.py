import pygame

class Interactable(pygame.sprite.Sprite):
    """
    Base class for objects the player can interact with.
    Includes a cooldown to prevent spamming interactions.
    """
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA) # Use SRCALPHA for transparency
        self.rect = self.image.get_rect(topleft=(x, y))
        self.last_interaction_time = -500 # Cooldown timer

    def interact(self, player, operon):
        """Checks if the interaction cooldown has passed."""
        if pygame.time.get_ticks() - self.last_interaction_time > 500:
            self.last_interaction_time = pygame.time.get_ticks()
            return True
        return False
    
    def draw(self, screen, camera_x):
        """A base draw method."""
        adjusted_rect = self.rect.copy()
        adjusted_rect.x -= camera_x
        screen.blit(self.image, adjusted_rect)

class Door(Interactable):
    """
    A door that can be opened with 'E', or destroyed by rolling or attacks.
    It acts as a physical barrier when closed.
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.is_open, self.is_destroyed = False, False
        self.health = 30
        self.update_visuals()

    def update(self, player, combat_operon, enemy_operon):
        """Handles destruction by rolling."""
        if not self.is_destroyed and getattr(player, 'is_rolling', False) and self.rect.colliderect(player.rect):
             combat_operon.apply_damage(self, 999, player, {}) # Apply massive damage on roll

    def interact(self, player, operon):
        """Toggles the door's open/closed state on 'E' press."""
        if super().interact(player, operon) and not self.is_destroyed:
            self.is_open = not self.is_open
            self.update_visuals()

    def on_death(self, combat_operon, enemy_operon):
        """Handles the door's destruction MAGIC."""
        if self.is_destroyed: return
        self.is_destroyed, self.is_open = True, True
        self.update_visuals()

    def is_collidable(self):
        """A door blocks movement only when it's closed and not destroyed MAGIC."""
        return not self.is_open and not self.is_destroyed

    def update_visuals(self):
        """Updates the door's appearance based on its state."""
        self.image.fill((0,0,0,0)) # Clear the surface
        body_color = (40, 40, 40) if self.is_destroyed else (90, 45, 10) if self.is_open else (139, 69, 19)
        pygame.draw.rect(self.image, body_color, self.image.get_rect())
        pygame.draw.rect(self.image, (40, 20, 5), self.image.get_rect(), 4)
        if self.is_destroyed:
            pygame.draw.line(self.image, (255, 255, 255), (0,0), self.rect.size, 3)

class Chest(Interactable):
    """
    A chest that can be opened once with 'E' for a random reward.
    It acts as a barrier until opened.
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.is_open = False
        self.update_visuals()

    def interact(self, player, operon):
        """On 'E' press, opens the chest, gives a reward, and disappears."""
        if not self.is_open and super().interact(player, operon):
            self.is_open = True
            # 80% chance for a weapon, 20% for monsters
            if random.random() < 0.8:
                operon.weapon_operon.create_random_weapon(self.rect.center)
            else:
                for i in range(random.randint(1, 2)):
                    operon.enemy_operon.create_enemy('melee', self.rect.centerx + ((i-0.5)*60), self.rect.bottom)
            self.kill() # Remove from all groups

    def is_collidable(self):
        return not self.is_open
    
    def update_visuals(self):
        self.image.fill((0,0,0,0))
        pygame.draw.rect(self.image, (180, 120, 40), self.image.get_rect())
        pygame.draw.rect(self.image, (220, 160, 60), (0, 0, self.rect.width, self.rect.height//3))


class ScrollContainer(Interactable):
    """
    A scroll that can be picked up once with 'E' for a player buff.
    It does not block movement.
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.update_visuals()

    def interact(self, player, operon):
        """On 'E' press, gives a stat boost and disappears."""
        if super().interact(player, operon):
            operon.progression_operon.apply_scroll_boost()
            self.kill()

    def is_collidable(self):
        return False

    def update_visuals(self):
        self.image.fill((0,0,0,0))
        pygame.draw.rect(self.image, (255, 250, 230), self.image.get_rect(), border_radius=5)
        pygame.draw.rect(self.image, (200, 0, 0), (self.rect.width//2 - 5, 0, 10, self.rect.height))