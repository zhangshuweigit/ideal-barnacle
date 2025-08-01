import pygame

class NPC(pygame.sprite.Sprite):
    """Base class for all non-player characters."""
    def __init__(self, x, y, color, name):
        super().__init__()
        self.image = pygame.Surface((40, 70))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.name = name

    def interact(self, player):
        """Placeholder for interaction logic."""
        print(f"Interacting with {self.name}.")
        return f"Hello from {self.name}!"

class WeaponDealer(NPC):
    """NPC that offers weapons."""
    def __init__(self, x, y):
        super().__init__(x, y, (200, 200, 100), "Weapon Dealer")

    def interact(self, player):
        super().interact(player)
        return "Would you like to see my wares?"

class SkillTrainer(NPC):
    """NPC that teaches skills."""
    def __init__(self, x, y):
        super().__init__(x, y, (100, 200, 200), "Skill Trainer")

    def interact(self, player):
        super().interact(player)
        return "Let's unlock your potential."

class UpgradeShop(NPC):
    """NPC for permanent upgrades."""
    def __init__(self, x, y):
        super().__init__(x, y, (200, 100, 200), "Upgrader")

    def interact(self, player):
        super().interact(player)
        return "Invest in yourself for the long run."

class NPCOperon:
    """Manages all NPCs in the game."""
    def __init__(self):
        self.npcs = pygame.sprite.Group()
        self.create_npcs()

    def create_npcs(self):
        """Creates and places all NPCs for the starter village."""
        self.npcs.add(WeaponDealer(200, 600))
        self.npcs.add(SkillTrainer(300, 600))
        self.npcs.add(UpgradeShop(400, 600))

    def update(self, player, actions):
        """Handles interactions with NPCs."""
        if actions.get('interact'):
            for npc in self.npcs:
                if player.rect.colliderect(npc.rect.inflate(20, 20)):
                    message = npc.interact(player)
                    print(message)
                    break

    def draw(self, screen, camera_x=0):
        """Draws all NPCs, adjusted for camera."""
        for npc in self.npcs:
            adjusted_rect = npc.rect.copy()
            adjusted_rect.x -= camera_x
            screen.blit(npc.image, adjusted_rect)
