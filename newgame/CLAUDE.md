## 🧬 细菌代码原则 (Bacterial Code Principles)

基于细菌基因组的编程哲学：**小巧、模块化、独立自足**

### 🔬 小巧原则 (Compact Code)
**每一行代码都消耗能量 - 追求极致精简**
- **函数不超过20行** - 如同细菌基因的紧凑性，每个函数都应该小而专注
- **类不超过100行** - 保持类的职责单一，避免臃肿的"上帝类"
- **文件不超过300行** - 超过则立即分解，就像细菌分裂一样自然
- **删除死代码** - 未使用的代码就像无用的基因片段，必须清除
- **优先使用内置函数** - 利用Python的内置能力，减少自定义实现
- **避免重复代码** - DRY原则，每个功能只实现一次

### 🧩 模块化原则 (Modular Operons)
**代码被组织成可相互替换的"操纵子"群组**

#### 📁 项目文件结构 (三大主文件夹)
```
game_project/
├── code/                    # 代码文件夹 - 每个操纵子一个文件
│   ├── input_operon.py     # 输入操纵子 (A/D/空格/E/左键)
│   ├── weapon_operon.py    # 武器操纵子 (4槽位系统)
│   ├── enemy_operon.py     # 敌人操纵子 (远程/近战/护盾兵)
│   ├── npc_operon.py       # NPC操纵子 (武器商/技能树/商店)
│   ├── combat_operon.py    # 战斗操纵子 (攻击/防御/技能)
│   ├── movement_operon.py  # 移动操纵子 (跳跃/碰撞/物理)
│   ├── progression_operon.py # 成长操纵子 (经验/等级/技能树)
│   └── generation_operon.py # 生成操纵子 (关卡/敌人/道具)
├── images/                  # 图片文件夹 - 按类型分类
│   ├── characters/         # 角色图片
│   │   ├── player/         # 主角图片
│   │   ├── enemies/        # 敌人图片 (远程/近战/护盾兵)
│   │   └── npcs/           # NPC图片 (武器商/技能导师/商店)
│   ├── weapons/            # 武器图片
│   │   ├── main_weapons/   # 主武器 (弓类/近战武器)
│   │   └── sub_weapons/    # 副武器 (道具/技能类)
│   ├── ui/                 # 页面图片
│   │   ├── dialogs/        # 对话框图片
│   │   ├── hud/            # HUD元素 (血条/技能栏)
│   │   └── menus/          # 菜单界面图片
│   └── tiles/              # 地图图片
│       ├── terrain/        # 地形瓦片
│       ├── objects/        # 环境物体
│       └── backgrounds/    # 背景图片
└── maps/                   # 地图文件夹 - Tiled地图文件
    ├── starter_village.tmx # 新手村地图
    ├── dungeon_01.tmx      # 地牢关卡1
    ├── dungeon_02.tmx      # 地牢关卡2
    └── boss_arena.tmx      # Boss战斗场地
```

#### 🔬 操纵子式模块设计
- **单文件操纵子** - 每个操纵子独立成一个Python文件
- **资源分离** - 代码与图片、地图完全分离
- **标准化接口** - 统一的攻击处理：普攻(点击)、技能(长按)
- **资源引用** - 通过路径配置引用对应的图片和地图资源
- **热插拔能力** - 可以轻松替换不同的武器和敌人类型
- **最小依赖** - 每个操纵子独立运行，资源按需加载

### 🔄 独立自足原则 (Self-Sufficient Transfer)
**通过"水平基因转移"可以轻松地"复制粘贴"**
- **零依赖模块** - 每个模块都能独立运行和测试
- **标准化接口** - 使用统一的数据结构和通信协议
- **配置驱动** - 通过配置文件而非硬编码来控制行为
- **插件架构** - 新功能可以作为插件直接"转移"到系统中
- **文档完备** - 每个模块都有完整的使用说明，便于"转移"
- **示例代码** - 提供可直接运行的示例，降低集成成本

### 🔄 项目意识与上下文
- **始终阅读 `PLANNING.md`** 了解项目的"基因图谱"
- **检查 `TASK.md`** 确保每个任务都是必要的"基因表达"
- **遵循细菌式架构** - 小而美的组件化设计
- **能量效率优先** - 每行代码都要有明确的价值

### 🧪 测试与可靠性
- **微测试策略** - 每个小函数都有对应的小测试
- **操纵子测试** - 每个模块群组都有集成测试
- **转移测试** - 验证模块可以在不同环境中正常工作
- **能量消耗测试** - 性能测试确保代码效率

### ✅ 任务完成
- **原子化任务** - 每个任务都像单个基因一样小而完整
- **快速迭代** - 像细菌繁殖一样快速完成小任务
- **持续进化** - 通过小步骤不断改进系统

### 📎 细菌式编码风格
```python
# 小巧：单一职责的微函数
def calc_damage(base: int, mult: float) -> int:
    """计算伤害 - 单一职责，极简实现"""
    return int(base * mult)

# 输入控制操纵子 - 标准化的玩家输入处理
class InputOperon:
    """输入操纵子 - 处理所有玩家输入"""
    def __init__(self):
        self.keys = {
            'move_left': pygame.K_a,      # A键向左
            'move_right': pygame.K_d,     # D键向右  
            'jump': pygame.K_SPACE,       # 空格跳跃
            'interact': pygame.K_e        # E键交互
        }
        self.mouse = {
            'attack': 0  # 左键攻击 (pygame.BUTTON_LEFT)
        }
    
    def handle_movement(self, keys_pressed) -> tuple:
        """处理移动输入 - 返回(x方向, 是否跳跃)"""
        x_dir = 0
        if keys_pressed[self.keys['move_left']]:
            x_dir = -1
        if keys_pressed[self.keys['move_right']]: 
            x_dir = 1
        jump = keys_pressed[self.keys['jump']]
        return x_dir, jump
    
    def handle_action(self, mouse_pressed, keys_pressed) -> dict:
        """处理动作输入 - 返回动作字典"""
        return {
            'attack': mouse_pressed[self.mouse['attack']],
            'interact': keys_pressed[self.keys['interact']]
        }

# 武器系统操纵子 - 4槽位武器管理
class WeaponOperon:
    """武器操纵子 - 管理4个武器槽位"""
    def __init__(self):
        self.slots = {
            'main_1': None,    # 主武器1 (弓/近战)
            'main_2': None,    # 主武器2 (弓/近战)
            'sub_1': None,     # 副武器1 (道具/技能)
            'sub_2': None      # 副武器2 (道具/技能)
        }
        self.current_slot = 'main_1'
    
    def attack(self, is_skill: bool) -> dict:
        """执行攻击 - 普攻或技能"""
        weapon = self.slots[self.current_slot]
        if not weapon: return None
        return weapon.skill_attack() if is_skill else weapon.normal_attack()

# 敌人系统操纵子 - 三种敌人类型
class EnemyOperon:
    """敌人操纵子 - 管理三种敌人类型"""
    def create_enemy(self, enemy_type: str):
        """创建敌人 - 工厂模式"""
        types = {
            'ranged': self._create_ranged,    # 远程敌人
            'melee': self._create_melee,      # 近战敌人  
            'shield': self._create_shield     # 护盾兵
        }
        return types[enemy_type]()

# NPC系统操纵子 - 新手村NPC
class NPCOperon:
    """NPC操纵子 - 新手村功能NPC"""
    def __init__(self):
        self.npcs = {
            'weapon_dealer': self._weapon_npc,     # 初始武器NPC
            'skill_trainer': self._skill_npc,      # 技能树NPC
            'upgrade_shop': self._upgrade_npc      # 永久提升商店
        }

# 资源管理操纵子 - 统一资源加载
class ResourceOperon:
    """资源操纵子 - 管理图片和地图资源"""
    def __init__(self):
        self.base_paths = {
            'characters': 'images/characters/',
            'weapons': 'images/weapons/',
            'ui': 'images/ui/',
            'tiles': 'images/tiles/',
            'maps': 'maps/'
        }
    
    def load_character(self, char_type: str, name: str):
        """加载角色图片 - 统一接口"""
        path = f"{self.base_paths['characters']}{char_type}/{name}.png"
        return pygame.image.load(path)
    
    def load_weapon(self, weapon_type: str, name: str):
        """加载武器图片 - 统一接口"""
        path = f"{self.base_paths['weapons']}{weapon_type}/{name}.png"
        return pygame.image.load(path)

# 独立自足：可直接转移的模块
def create_game_systems():
    """工厂函数 - 创建所有游戏系统"""
    return {
        'input': InputOperon(),
        'weapon': WeaponOperon(), 
        'enemy': EnemyOperon(),
        'npc': NPCOperon(),
        'resource': ResourceOperon()
    }
```

### 📚 文档与进化
- **基因注释** - 每个函数都要说明其"生物学功能"
- **进化日志** - 记录代码的演化过程
- **转移指南** - 详细说明如何将模块转移到其他项目

### 🧠 细菌式AI行为
- **能量守恒** - 不写无用代码，不做无效计算
- **快速适应** - 根据环境快速调整代码结构
- **水平学习** - 从其他项目"转移"有用的代码模式
- **持续分裂** - 大模块自动分解为小模块