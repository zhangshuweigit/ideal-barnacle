#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的射击动画测试
"""

import sys
import pygame
import time
from code.movement_operon import Player
from code.weapon_operon import WeaponOperon

def test_shoot_animation():
    """测试射击动画是否可见"""
    print("开始射击动画可见性测试...")

    # 初始化pygame并设置窗口
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("射击动画测试")
    clock = pygame.time.Clock()

    # 创建测试玩家
    player = Player(100, 200)
    weapon_operon = WeaponOperon()

    print("[OK] 系统初始化成功")
    print(f"[OK] 上半身帧数: {len(player.animation_system.upper_body_frames)}")

    # 测试数据
    actions = {
        'active_slot': 'main_2',  # 使用弓
        'is_skill': False,
        'player_rect': player.rect,
        'mouse_pos': (200, 150)
    }

    running = True
    test_phase = "waiting"  # waiting, shooting, rapid_shooting
    phase_start_time = time.time()

    print("\n测试说明:")
    print("1. 按1键开始第一次射击测试")
    print("2. 按2键开始快速射击测试")
    print("3. 按ESC退出")
    print("观察窗口中的角色是否显示射击动画")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    # 第一次射击
                    print("\n[TEST] 第一次射击开始")
                    attack_data = weapon_operon.attack(actions)
                    if attack_data:
                        player.start_shooting()
                        if player.animation_system:
                            player.animation_system.set_shooting(True)
                            player.animation_system.set_use_last_frame(False)
                        print(f"[OK] 射击状态设置，快速射击: {weapon_operon.is_rapid_shooting()}")
                        test_phase = "shooting"
                        phase_start_time = time.time()
                elif event.key == pygame.K_2:
                    # 快速射击测试
                    print("\n[TEST] 快速射击测试开始")
                    attack_data = weapon_operon.attack(actions)
                    if attack_data:
                        player.start_shooting()
                        if player.animation_system:
                            player.animation_system.set_shooting(True)
                            player.animation_system.set_use_last_frame(weapon_operon.is_rapid_shooting())
                        print(f"[OK] 快速射击状态，使用最后帧: {weapon_operon.is_rapid_shooting()}")
                        test_phase = "rapid_shooting"
                        phase_start_time = time.time()

        # 更新状态
        player.update_state()
        weapon_operon.update(player.rect, (200, 150))

        # 清屏
        screen.fill((50, 50, 50))

        # 绘制角色
        if player.animation_system:
            frame = player.animation_system.get_current_frame(1)  # 面向右
            if frame:
                screen.blit(frame, (150, 100))
                print(f"[DEBUG] 绘制帧 - 射击状态: {player.animation_system.is_shooting}, 使用最后帧: {player.animation_system.use_last_frame}, 帧索引: {player.animation_system.shoot_frame_index}")
            else:
                print("[DEBUG] 没有获取到帧")
        else:
            print("[DEBUG] 没有动画系统")

        # 显示状态信息
        font = pygame.font.Font(None, 24)
        status_text = [
            f"测试阶段: {test_phase}",
            f"射击状态: {player.animation_system.is_shooting if player.animation_system else 'N/A'}",
            f"使用最后帧: {player.animation_system.use_last_frame if player.animation_system else 'N/A'}",
            f"帧索引: {player.animation_system.shoot_frame_index if player.animation_system else 'N/A'}",
            f"武器射击状态: {weapon_operon.is_shooting}",
            f"快速射击: {weapon_operon.is_rapid_shooting()}",
            "",
            "按1: 第一次射击",
            "按2: 快速射击",
            "按ESC: 退出"
        ]

        for i, text in enumerate(status_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))

        pygame.display.flip()
        clock.tick(30)  # 30 FPS

        # 检查测试阶段超时
        if test_phase in ["shooting", "rapid_shooting"]:
            if time.time() - phase_start_time > 5:  # 5秒后重置
                print(f"[TEST] {test_phase} 测试完成")
                test_phase = "waiting"

    pygame.quit()
    print("\n测试结束")
    return True

if __name__ == "__main__":
    success = test_shoot_animation()
    sys.exit(0 if success else 1)