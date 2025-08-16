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