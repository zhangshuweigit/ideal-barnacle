import pygame

class ProgressionOperon:
    """
    Manages player progression, including attributes, experience, and permanent upgrades.
    This operon is designed to be completely independent and data-driven.
    """
    def __init__(self):
        self.attributes = {
            'max_health': 100,
            'damage_modifier': 1.0,
            'move_speed': 5,
            'luck': 0.05  # Chance for better loot
        }
        self.experience = 0
        self.level = 1

    def add_experience(self, amount):
        """Adds experience points and handles level ups."""
        self.experience += amount
        print(f"Gained {amount} XP. Total XP: {self.experience}")
        # Add level up logic here if needed

    def apply_scroll_boost(self):
        """Applies a random, permanent stat boost to the player."""
        boost_type = random.choice(['max_health', 'damage_modifier', 'move_speed', 'luck'])
        
        if boost_type == 'max_health':
            self.attributes['max_health'] += 20
            print("Scroll Boost: Max Health +20!")
        elif boost_type == 'damage_modifier':
            self.attributes['damage_modifier'] += 0.1
            print("Scroll Boost: Damage +10%!")
        elif boost_type == 'move_speed':
            self.attributes['move_speed'] += 0.5
            print("Scroll Boost: Move Speed Increased!")
        elif boost_type == 'luck':
            self.attributes['luck'] += 0.02
            print("Scroll Boost: Luck Increased!")
            
        return boost_type

    def get_attribute(self, attr_name):
        """Returns the value of a specific attribute."""
        return self.attributes.get(attr_name)
