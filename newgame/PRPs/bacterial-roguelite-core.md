# PRP for Bacterial Roguelite Core Implementation

## 1. Introduction

This document outlines the plan for implementing the core features of a 2D Roguelite action game, following the "Bacterial Code Principles" defined in `CLAUDE.md`. The goal is to create a modular, scalable, and efficient game foundation.

## 2. Feature Description

The core feature is a complete, playable game loop including player control, combat, enemies, NPCs, and procedural generation, all built upon the "operon" modular system.

- **Player:** Full movement (walk, jump), 4-slot weapon system (main/sub), and interactions.
- **Enemies:** Three distinct enemy types (ranged, melee, shield) with unique behaviors.
- **NPCs:** Three starter village NPCs for weapons, skills, and upgrades.
- **Systems:** Combat, progression, and procedural generation systems to support the game loop.
- **Philosophy:** All code must adhere to the principles of being small, modular, and self-sufficient.

## 3. Implementation Plan

The implementation will be done "operon" by "operon", ensuring each module is self-contained and testable.

### Task List:

1.  **Setup Core Game Loop (`main.py`):**
    *   Create the main game window using Pygame.
    *   Implement a basic game loop (input, update, render).
    *   Create the main `ResourceOperon` for asset loading.

2.  **Implement `input_operon.py`:**
    *   Create the `InputOperon` class to handle all player keyboard and mouse inputs as specified in `INITIAL.md`.
    *   The `process_input` function should return a dictionary of actions.

3.  **Implement `movement_operon.py`:**
    *   Create a `Player` class.
    *   Implement basic physics for movement, gravity, and jumping.
    *   Handle collisions with the game world (platforms, walls).

4.  **Implement `weapon_operon.py`:**
    *   Create the `WeaponSlots` class to manage the 4-slot inventory.
    *   Implement base classes for `Weapon` with `normal_attack` and `skill_attack` methods.
    *   Create initial weapon types (e.g., Basic Sword, Basic Bow).

5.  **Implement `combat_operon.py`:**
    *   Develop a `CombatOperon` to handle damage calculations.
    *   Implement logic for applying damage to players and enemies.
    *   Create a simple health system for game entities.

6.  **Implement `enemy_operon.py`:**
    *   Create a base `Enemy` class.
    *   Implement the three specified enemy types (`ranged`, `melee`, `shield`) with distinct AI behaviors.
    *   Use a factory pattern (`create_enemy`) within the `EnemyOperon`.

7.  **Implement `generation_operon.py`:**
    *   Create a basic `GenerationOperon`.
    *   Implement logic to place enemies and items in a pre-defined map (`starter_village.tmx`).

8.  **Implement `npc_operon.py`:**
    *   Create a base `NPCOperon` class.
    *   Implement the three NPC types (`weapon_dealer`, `skill_trainer`, `upgrade_shop`) with basic interaction logic.

9.  **Integration and Refinement:**
    *   Integrate all operons into the main game loop.
    *   Ensure all systems communicate correctly.
    *   Refine gameplay and fix bugs.

## 4. Code and Pattern References

-   **`CLAUDE.md`:** This is the primary architectural guide. All code must strictly follow the "Bacterial Code Principles" outlined here. Specifically, pay attention to file size limits, class/function length, and the "operon" structure.
-   **`INITIAL.md`:** Contains the detailed specifications for all game systems, including controls, weapons, enemies, and NPCs. These specifications must be followed precisely.
-   **Pygame Documentation:** For any graphics, input, or sound implementation details.

## 5. Validation Gates

The following commands must be run after each major step to ensure code quality and correctness.

```bash
# Style and Static Analysis (Assuming ruff and mypy are set up)
ruff check --fix .
mypy .

# Unit Tests (Assuming pytest is set up in a `tests/` directory)
# Test files should be created for each operon.
pytest tests/
```

## 6. Gotchas and Considerations

-   **Strict Adherence to Principles:** The "Bacterial Code" philosophy is not just a suggestion; it's a hard requirement. Do not write large files or complex classes.
-   **Asset Paths:** All asset paths are defined in `INITIAL.md`. Use a centralized resource manager (`ResourceOperon`) to handle all asset loading, as shown in the examples.
-   **Modularity:** Each operon must be independently testable. Avoid creating tight coupling between operons.

## Confidence Score: 8/10

The plan is comprehensive and the source documents (`CLAUDE.md`, `INITIAL.md`) are extremely detailed, providing a clear path to implementation. The main risk is the potential for complexity to grow if the core principles are not strictly followed.
