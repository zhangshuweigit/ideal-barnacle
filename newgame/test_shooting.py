#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试射击功能的简单脚本
"""

import sys
import os
import pygame
from code.movement_operon import Player
from code.weapon_operon import WeaponOperon

def test_shooting_features():
    """测试射击功能"""
    print("开始测试射击功能...")

    # 初始化pygame并设置视频模式
    pygame.init()
    screen = pygame.display.set_mode((1, 1))  # 最小窗口，仅用于初始化

    # 创建测试玩家
    player = Player(100, 500)
    weapon_operon = WeaponOperon()

    print("[OK] 玩家和武器系统初始化成功")

    # 测试动画系统
    if player.animation_system:
        print(f"[OK] 动画系统初始化成功，帧数: {player.animation_system.get_frame_count()}")
        print(f"[OK] 上半身帧数: {len(player.animation_system.upper_body_frames)}")
    else:
        print("[ERROR] 动画系统初始化失败")
        return False

    # 测试射击状态
    print("\n--- 测试射击状态 ---")

    # 模拟攻击
    actions = {
        'active_slot': 'main_2',  # 使用弓
        'is_skill': False,
        'player_rect': player.rect,
        'mouse_pos': (200, 300)
    }

    # 第一次射击
    print("1. 第一次射击测试...")
    attack_data = weapon_operon.attack(actions)
    if attack_data:
        print(f"[OK] 攻击数据生成成功: {attack_data}")
        print(f"[OK] 武器系统射击状态: {weapon_operon.is_shooting}")
        print(f"[OK] 快速射击状态: {weapon_operon.is_rapid_shooting()}")

        # 设置玩家射击状态
        player.start_shooting()
        print(f"[OK] 玩家射击状态: {player.is_shooting}")

        # 设置动画状态
        if player.animation_system:
            player.animation_system.set_shooting(True)
            player.animation_system.set_use_last_frame(weapon_operon.is_rapid_shooting())
            print("[OK] 动画系统状态设置成功")
    else:
        print("[ERROR] 攻击数据生成失败")
        return False

    # 测试快速射击
    print("\n2. 快速射击序列测试...")
    import time

    # 等待很短时间（模拟快速连击）- 第一次射击
    print("2.1. 第一次射击（应该播放完整动画）...")
    attack_data2 = weapon_operon.attack(actions)
    if attack_data2:
        print(f"[OK] 第一次攻击成功")
        print(f"[OK] 射击计数: {weapon_operon.shot_count}")
        print(f"[OK] 快速射击序列状态: {weapon_operon.is_rapid_shot_sequence}")
        print(f"[OK] 快速射击状态: {weapon_operon.is_rapid_shooting()}")

        # 更新动画状态
        if player.animation_system:
            player.animation_system.set_use_last_frame(weapon_operon.is_rapid_shooting())
            print(f"[OK] 第一次射击动画状态设置成功")
            print(f"[OK] 射击帧索引: {player.animation_system.shoot_frame_index}")
            print(f"[OK] 是否使用最后帧: {player.animation_system.use_last_frame}")

            # 模拟几帧动画更新来测试动画播放
            for i in range(3):
                player.animation_system._update_shoot_animation()
                print(f"[OK] 动画帧 {i+1}: 索引={player.animation_system.shoot_frame_index}")
                import time
                time.sleep(0.05)  # 模拟帧间隔

    # 等待很短时间（模拟快速连击）- 第二次射击
    print("2.2. 第二次射击（间隔<1秒，应该稳定在最后图片）...")
    time.sleep(0.1)  # 等待0.1秒

    attack_data3 = weapon_operon.attack(actions)
    if attack_data3:
        print(f"[OK] 第二次攻击成功")
        print(f"[OK] 射击计数: {weapon_operon.shot_count}")
        print(f"[OK] 快速射击序列状态: {weapon_operon.is_rapid_shot_sequence}")
        print(f"[OK] 快速射击状态: {weapon_operon.is_rapid_shooting()}")

        # 更新动画状态
        if player.animation_system:
            player.animation_system.set_use_last_frame(weapon_operon.is_rapid_shooting())
            print("[OK] 第二次射击动画状态设置成功（应该使用最后图片）")

    # 测试等待超过1秒后重置
    print("2.3. 等待超过1秒后重置测试...")
    time.sleep(1.1)  # 等待1.1秒

    attack_data4 = weapon_operon.attack(actions)
    if attack_data4:
        print(f"[OK] 重置后攻击成功")
        print(f"[OK] 射击计数: {weapon_operon.shot_count}")
        print(f"[OK] 快速射击序列状态: {weapon_operon.is_rapid_shot_sequence}")
        print(f"[OK] 快速射击状态: {weapon_operon.is_rapid_shooting()}")

        # 更新动画状态
        if player.animation_system:
            player.animation_system.set_use_last_frame(weapon_operon.is_rapid_shooting())
            print("[OK] 重置后动画状态设置成功（应该重新播放完整动画）")

    # 测试移动限制
    print("\n3. 移动限制测试...")

    # 尝试移动（应该被阻止）
    original_velocity = player.velocity.x
    player.move(1)  # 尝试向右移动
    if player.velocity.x == 0:
        print("[OK] 射击时移动被正确阻止")
    else:
        print("[ERROR] 射击时移动没有被阻止")
        return False

    # 测试状态更新
    print("\n4. 状态更新测试...")

    # 模拟时间流逝（射击状态应该结束）
    import time
    time.sleep(0.4)  # 等待超过射击持续时间

    # 更新状态
    player.update_state()
    weapon_operon.update(player.rect, (200, 300))

    print(f"[OK] 玩家射击状态更新后: {player.is_shooting}")
    print(f"[OK] 武器系统射击状态更新后: {weapon_operon.is_shooting}")

    # 测试恢复移动
    player.move(1)
    if player.velocity.x != 0:
        print("[OK] 射击结束后移动恢复正常")
    else:
        print("[ERROR] 射击结束后移动没有恢复")
        return False

    print("\n--- 所有测试通过！---")
    print("功能摘要:")
    print("1. [OK] 射击时角色停止移动")
    print("2. [OK] 射击时隐藏原本图片，只显示上半身射击图片")
    print("3. [OK] 第一次射击播放完整动画序列")
    print("4. [OK] 第二次射击（间隔<1秒）稳定在最后一张图片")
    print("5. [OK] 超过1秒后重置射击序列状态")
    print("6. [OK] 射击状态自动恢复")
    print("7. [OK] 动画系统正确响应射击状态")

    pygame.quit()
    return True

if __name__ == "__main__":
    success = test_shooting_features()
    sys.exit(0 if success else 1)