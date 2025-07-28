## 🧬 功能特性 (基于细菌代码原则):

横版Roguelite动作游戏，遵循**小巧、模块化、独立自足**的细菌代码哲学：

### 核心操纵子 (Core Operons)
- **input_operon** - 输入操纵子：A/D移动、空格跳跃、左键攻击、E键交互
- **weapon_operon** - 武器操纵子：4槽位系统（2主武器+2副武器），普攻+技能
- **enemy_operon** - 敌人操纵子：三种敌人类型（远程、近战、护盾兵）
- **npc_operon** - NPC操纵子：新手村NPC（武器商、技能树、永久提升商店）
- **combat_operon** - 战斗操纵子：伤害计算、技能效果、掉落系统
- **movement_operon** - 移动操纵子：跳跃、碰撞、物理引擎
- **progression_operon** - 成长操纵子：经验系统、技能树、属性提升
- **generation_operon** - 生成操纵子：关卡生成、敌人生成、道具生成
- **roguelite_operon** - Roguelite操纵子：随机性、永久进度、死亡机制
- **platform_operon** - 平台操纵子：环境交互、多层次设计

### 🎮 玩家控制规范 (Player Control Specification)
```
# 移动与交互
A键        → 向左移动
D键        → 向右移动
空格键      → 跳跃
E键         → 交互
Shift键     → 翻滚 (带短暂无敌帧)

# 武器激活与攻击类型
鼠标左键 (点按) → 主武器1 (main_1) - 普通攻击
鼠标左键 (长按) → 主武器1 (main_1) - 战技
鼠标右键 (点按) → 主武器2 (main_2) - 普通攻击
鼠标右键 (长按) → 主武器2 (main_2) - 战技
1键         → 副武器1 (sub_1) - (仅普通攻击)
2键         → 副武器2 (sub_2) - (仅普通攻击)
```

### ⚔️ 武器系统规范 (Weapon System Specification)
```
武器槽位 (4个):
├── 主武器1 (main_weapon_1) - 弓类/近战武器
├── 主武器2 (main_weapon_2) - 弓类/近战武器  
├── 副武器1 (sub_weapon_1) - 道具/技能类武器
└── 副武器2 (sub_weapon_2) - 道具/技能类武器

攻击类型:
├── 普攻 (normal_attack) - 左键点击，基础攻击
└── 技能 (skill_attack) - 左键长按，高伤害技能

武器获取:
├── 击败敌人掉落 (概率掉落)
├── 地图拾取 (随机生成)
└── NPC购买 (新手村武器商)
```

### 👹 敌人系统规范 (Enemy System Specification)
```
敌人类型 (3种):
├── 远程敌人 (ranged_enemy)
│   ├── 行为: 保持距离，远程攻击
│   ├── 弱点: 近战时脆弱
│   └── 掉落: 弓类武器概率较高
├── 近战敌人 (melee_enemy)  
│   ├── 行为: 冲向玩家，近身攻击
│   ├── 弱点: 远程攻击难以接近
│   └── 掉落: 近战武器概率较高
└── 护盾兵 (shield_enemy)
    ├── 行为: 防御姿态，格挡攻击
    ├── 弱点: 背后或技能攻击
    └── 掉落: 防御类道具概率较高
```

### 🏘️ 新手村NPC规范 (Starter Village NPC Specification)
```
NPC类型 (3个):
├── 武器商人 (weapon_dealer)
│   ├── 功能: 提供初始武器
│   ├── 商品: 基础弓、基础剑、基础道具
│   └── 货币: 金币或初始免费
├── 技能导师 (skill_trainer)
│   ├── 功能: 辅助技能树管理
│   ├── 服务: 技能点分配、技能重置
│   └── 货币: 技能点或特殊材料
└── 永久提升商店 (upgrade_shop)
    ├── 功能: 永久属性提升
    ├── 商品: 生命值、攻击力、移动速度提升
    └── 货币: 特殊货币或成就点数
```

### 🧬 细菌式游戏系统示例 (微模块实现)

#### 输入处理微模块 (15行)
```python
import pygame

def process_input(keys, mouse_buttons, mouse_hold_time) -> dict:
    """处理玩家输入 - 细菌式微函数"""
    return {
        'move_x': (keys[pygame.K_d] - keys[pygame.K_a]),  # -1/0/1
        'jump': keys[pygame.K_SPACE],                     # True/False
        'normal_attack': mouse_buttons[0] and mouse_hold_time < 0.3,  # 点击
        'skill_attack': mouse_buttons[0] and mouse_hold_time >= 0.3,  # 长按
        'interact': keys[pygame.K_e]                      # E键
    }
```

#### 武器系统微模块 (20行)
```python
class WeaponSlots:
    """武器槽位管理 - 4槽位系统"""
    def __init__(self):
        self.slots = [None, None, None, None]  # 2主+2副
        self.current = 0
    
    def attack(self, is_skill: bool):
        """执行攻击 - 普攻或技能"""
        weapon = self.slots[self.current]
        return weapon.skill() if is_skill else weapon.normal()
    
    def drop_weapon(enemy_type: str) -> str:
        """武器掉落 - 基于敌人类型"""
        drop_rates = {'ranged': 'bow', 'melee': 'sword', 'shield': 'item'}
        return drop_rates.get(enemy_type) if random() < 0.3 else None
```

#### 敌人AI微模块 (18行)
```python
def enemy_ai(enemy, player, dt):
    """敌人AI - 基于类型的行为"""
    behaviors = {
        'ranged': lambda: keep_distance_and_shoot(enemy, player),
        'melee': lambda: charge_at_player(enemy, player), 
        'shield': lambda: defensive_stance(enemy, player)
    }
    behaviors[enemy.type]()

def keep_distance_and_shoot(enemy, player):
    """远程敌人行为 - 保持距离射击"""
    if distance(enemy, player) < enemy.min_range:
        enemy.move_away_from(player)
    else:
        enemy.shoot_at(player)
```

每个操纵子都是**独立自足**的，可以单独开发、测试和替换。

## 🔬 示例参考 (细菌式架构):

在 `examples/` 文件夹中的微模块示例：

### 小巧示例 (每个文件<300行)
- `examples/micro_input/` - 15行的输入处理函数
- `examples/micro_weapon/` - 20行的武器槽位管理
- `examples/micro_enemy/` - 18行的敌人AI行为
- `examples/micro_npc/` - 25行的NPC交互系统
- `examples/micro_combat/` - 20行的伤害计算函数
- `examples/micro_drops/` - 12行的掉落概率计算
- `examples/micro_movement/` - 30行的跳跃控制器
- `examples/micro_generation/` - 50行的房间生成器
- `examples/micro_ui/` - 40行的HUD组件

### 📁 项目文件结构 (三大主文件夹)
```
game_project/
├── code/                    # 代码文件夹 - 每个操纵子一个文件
│   ├── input_operon.py     # 输入操纵子 (A/D/空格/E/左键) - 50行
│   ├── weapon_operon.py    # 武器操纵子 (4槽位系统) - 80行
│   ├── enemy_operon.py     # 敌人操纵子 (远程/近战/护盾兵) - 120行
│   ├── npc_operon.py       # NPC操纵子 (武器商/技能树/商店) - 90行
│   ├── combat_operon.py    # 战斗操纵子 (攻击/防御/技能) - 100行
│   ├── movement_operon.py  # 移动操纵子 (跳跃/碰撞/物理) - 110行
│   ├── progression_operon.py # 成长操纵子 (经验/等级/技能树) - 85行
│   ├── generation_operon.py # 生成操纵子 (关卡/敌人/道具) - 150行
│   ├── resource_operon.py  # 资源操纵子 (图片/地图加载) - 60行
│   └── main.py             # 主程序入口 - 30行
├── images/                  # 图片文件夹 - 按类型分类
│   ├── characters/         # 角色图片文件夹
│   │   ├── player/         # 主角图片
│   │   │   ├── idle.png    # 待机动画帧
│   │   │   ├── walk.png    # 行走动画帧
│   │   │   ├── jump.png    # 跳跃动画帧
│   │   │   └── attack.png  # 攻击动画帧
│   │   ├── enemies/        # 敌人图片
│   │   │   ├── ranged_enemy.png    # 远程敌人
│   │   │   ├── melee_enemy.png     # 近战敌人
│   │   │   └── shield_enemy.png    # 护盾兵
│   │   └── npcs/           # NPC图片
│   │       ├── weapon_dealer.png   # 武器商人
│   │       ├── skill_trainer.png   # 技能导师
│   │       └── upgrade_shop.png    # 商店老板
│   ├── weapons/            # 武器图片文件夹
│   │   ├── main_weapons/   # 主武器图片
│   │   │   ├── bow_basic.png       # 基础弓
│   │   │   ├── sword_basic.png     # 基础剑
│   │   │   └── axe_basic.png       # 基础斧
│   │   └── sub_weapons/    # 副武器图片
│   │       ├── potion_health.png   # 生命药水
│   │       ├── bomb_basic.png      # 基础炸弹
│   │       └── shield_magic.png    # 魔法盾
│   ├── ui/                 # 页面图片文件夹
│   │   ├── dialogs/        # 对话框图片
│   │   │   ├── dialog_box.png      # 对话框背景
│   │   │   └── dialog_arrow.png    # 对话指示箭头
│   │   ├── hud/            # HUD元素图片
│   │   │   ├── health_bar.png      # 血条
│   │   │   ├── mana_bar.png        # 魔法条
│   │   │   └── weapon_slots.png    # 武器槽位UI
│   │   └── menus/          # 菜单界面图片
│   │       ├── main_menu.png       # 主菜单背景
│   │       └── pause_menu.png      # 暂停菜单
│   └── tiles/              # 地图图片文件夹
│       ├── terrain/        # 地形瓦片
│       │   ├── grass.png           # 草地瓦片
│       │   ├── stone.png           # 石头瓦片
│       │   └── water.png           # 水面瓦片
│       ├── objects/        # 环境物体
│       │   ├── tree.png            # 树木
│       │   ├── rock.png            # 岩石
│       │   └── chest.png           # 宝箱
│       └── backgrounds/    # 背景图片
│           ├── sky.png             # 天空背景
│           └── mountains.png       # 山脉背景
└── maps/                   # 地图文件夹 - Tiled地图文件
    ├── starter_village.tmx # 新手村地图 (包含3个NPC位置)
    ├── dungeon_01.tmx      # 地牢关卡1 (远程敌人为主)
    ├── dungeon_02.tmx      # 地牢关卡2 (近战敌人为主)
    ├── dungeon_03.tmx      # 地牢关卡3 (护盾兵为主)
    └── boss_arena.tmx      # Boss战斗场地
```

### 🔬 资源组织原则 (细菌式资源管理)
```python
# 资源路径配置 - 统一管理
RESOURCE_PATHS = {
    'player': 'images/characters/player/',
    'enemies': 'images/characters/enemies/',
    'npcs': 'images/characters/npcs/',
    'main_weapons': 'images/weapons/main_weapons/',
    'sub_weapons': 'images/weapons/sub_weapons/',
    'ui_dialogs': 'images/ui/dialogs/',
    'ui_hud': 'images/ui/hud/',
    'ui_menus': 'images/ui/menus/',
    'terrain': 'images/tiles/terrain/',
    'objects': 'images/tiles/objects/',
    'backgrounds': 'images/tiles/backgrounds/',
    'maps': 'maps/'
}

# 资源加载微函数 (15行)
def load_resource(category: str, filename: str):
    """加载资源 - 统一接口"""
    path = RESOURCE_PATHS[category] + filename
    return pygame.image.load(path) if path.endswith('.png') else path
```

### 🧬 文件组织细菌式原则
- **单一职责文件** - 每个.py文件只负责一个操纵子功能
- **资源分离** - 代码、图片、地图完全分离，便于管理和替换
- **路径标准化** - 统一的资源路径配置，便于水平转移
- **按需加载** - 资源只在需要时加载，节约内存
- **热插拔资源** - 可以轻松替换图片和地图而不影响代码

### 独立自足示例 (可直接转移)
- `examples/transferable/resource_loader.py` - 完整的资源加载模块(60行)
- `examples/configs/resource_paths.json` - 资源路径配置文件
- `examples/tools/image_optimizer.py` - 图片优化工具(40行)

## 📚 文档资源 (精简高效):

### 核心文档 (必读)
- **细菌式编程指南** - 20页核心原则说明
- **操纵子设计模式** - 模块化架构参考
- **水平转移手册** - 代码复用和移植指南

### 技术文档 (按需查阅)
- **Pygame微模块** - 精简的游戏引擎使用
- **ECS轻量实现** - 200行的ECS系统
- **性能优化清单** - 能量效率检查表

## 🔄 其他考虑事项 (细菌式开发):

### 能量效率原则
- **代码密度** - 每行代码都有明确价值，无冗余实现
- **内存节约** - 使用对象池、避免内存泄漏
- **CPU优化** - 60FPS目标，每帧预算16.67ms
- **加载优化** - 懒加载、资源复用

### 模块化开发
- **热插拔系统** - 运行时可替换模块
- **配置驱动** - 通过JSON/YAML控制行为
- **接口标准化** - 统一的数据结构和API
- **依赖最小化** - 每个操纵子独立运行

### 水平转移能力
- **零配置启动** - 模块可直接运行
- **完整文档** - 每个模块都有使用说明
- **示例代码** - 可执行的演示程序
- **版本兼容** - 向后兼容的接口设计

### 细菌式质量保证
- **微测试** - 每个小函数都有测试
- **快速反馈** - 秒级的测试执行
- **持续进化** - 小步骤迭代改进
- **自动分裂** - 大模块自动重构

### 特别注意 (生存法则)
- **适者生存** - 无用代码立即删除
- **快速繁殖** - 小功能快速实现和复制
- **环境适应** - 代码能适应不同运行环境
- **基因交换** - 模块间可以共享有用功能

### 🎨 资源制作规范
- **图片格式** - 统一使用PNG格式，支持透明度
- **图片尺寸** - 角色32x32像素，武器16x16像素，UI元素按需
- **命名规范** - 使用下划线分隔，如 `ranged_enemy.png`
- **动画帧** - 多帧动画放在同一文件中，通过代码分割
- **地图规范** - 使用Tiled编辑器，瓦片大小32x32像素

### 开发工作流 (细菌式)
1. **分裂开发** - 将大任务分解为20行以内的小函数
2. **操纵子组装** - 将相关小函数组织成单个.py文件
3. **资源准备** - 按文件夹结构准备对应的图片和地图
4. **转移测试** - 验证模块可以独立运行
5. **进化优化** - 持续改进代码效率和资源使用
6. **基因库维护** - 建立可复用的代码和资源库