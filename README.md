# HTML品牌视觉手册 Skill（开源版）

> 一个完整的、开源的 WorkBuddy Skill，用于制作生产级交互式品牌视觉手册（VI手册），以单文件HTML形式交付，内嵌CSS/JS/SVG。

## 这是什么

这是一个 **WorkBuddy Skill（技能包）**——将AI助手变身成为品牌手册专家的可复用知识库。它封装了**10+轮真实项目迭代中踩过的坑**，涵盖：

- **CJK中文排版系统** — 中日韩语品牌手册的最大痛点。真正有效的 word-break/overflow-wrap 配置方案。
- **SVG Logo矢量架构** — Symbol + use 模式 + 负坐标 viewBox 处理技巧
- **导航栏布局** — 经过10轮迭代修复重叠/消失/错位的最终CSS方案
- **组件库** — 可复用的卡片、表格、色板、设备模型、Do/Don't规范网格
- **迭代调试工作流** — 从用户截图出发系统性修复视觉问题的方法论
- **常见陷阱目录** — 12+个真实Bug及其根因分析与预防方法

## 快速开始

1. 将此Skill安装到你的WorkBuddy实例中
2. 对AI说："帮我创建[你的品牌]的品牌视觉手册"
3. AI会按照 `SKILL.md` 中定义的完整工作流程执行

### 模板文件

包含一个开箱即用的HTML模板：`assets/template/index.html`，演示了：

- 全部正确的CJK中文排版模式
- 带负坐标viewBox处理的SVG Symbol系统
- 经验证的导航侧边栏布局CSS
- 组件库（色板、表格、Do/Don't网格、手机模型）
- 安全网 CSS + JS
- 深色模式支持
- 响应式设计

将 `[BRAND]`、`[SLOGAN]` 和占位路径替换为你自己的内容即可使用。

## 文件结构

```
html-brand-manual/
├── SKILL.md                          # 主文件（完整工作流程）
├── README.md                         # 本说明文档
├── LICENSE                           # MIT开源协议
├── references/
│   ├── cjk-typography.md             # CJK排版完整参考指南
│   ├── svg-logo-system.md            # SVG矢量架构深度指南
│   └── common-pitfalls.md            # 12+真实Bug案例集
├── scripts/
│   ├── validate-manual.py            # 自动化QA检测脚本（12项检查）
│   └── example.py                    # 使用示例脚本
└── assets/
    └── template/
        └── index.html               # 干净的骨架模板（~600行）
```

## 核心经验总结

### CJK中文排版

中文品牌手册中最大的Bug来源：

| 反模式 | 症状 | 解决方案 |
|--------|------|----------|
| 全局 `* { word-break: keep-all }` | 段落文字不填满容器宽度 | 正文用 `normal`，标题才用 `keep-all` |
| 矛盾的安全网规则（`break-word` + `keep-all`） | 行为不可预测 | 单一数据源：CSS和JS必须一致 |
| `text-align: justify` 用于中文 | 字符间距丑陋 | 绝不要对中文两端对齐 |
| `<p>` 标签上的行内 `max-width` | 与周围内容宽度不匹配 | 删除；在容器层级约束宽度 |

### SVG Logo

通过 opentype.js 将字体转换为SVG路径时，输出的viewBox通常包含**负Y坐标**：

```xml
<!-- 字体转换后会生成这种结构 -->
<symbol id="brand-wordmark" viewBox="-8.6 -85.4 456.0 91.0">
<!--                              ^^^^^^ ^^^^^^              -->
<!--                              负坐标！这就是Bug的根源        -->
```

**必须使用显式的 width + height + overflow:visible** — 永远不要依赖 `height:auto`。

### 更多核心经验（v1.0 → v7.5 全周期）

| 经验领域 | 版本 | 关键教训 |
|----------|------|----------|
| Logo架构决策 | **v2.3⭐** | PNG→SVG矢量系统是必经之路，opentype.js转字体为路径 |
| 竞品配色审计 | **v3.2⭐** | 选色前先分析11+竞品，避免副色与竞品主色撞车 |
| 副色选型 | **v3.3→v3.5** | 用户可能连续否决多轮备选，提供3-4组方案 |
| 品牌故事语气 | **v6.2⭐** | "草根逆袭"叙事可能增加信任成本，B2C靠专业不靠示弱 |
| 字体版权陷阱 | **贯穿v2.x-v3.x** | 商业字体Logo→SVG路径嵌入；系统字体用SIL OFL免费款 |
| CSS语法静默失败 | **v2.9** | 冒号代替分号导致整块CSS被跳过，15000行中极难发现 |
| overflow:hidden裁切 | **v2.8/v3.0** | 神秘内容消失的元凶，全文搜索逐一评估 |
| 大规模变量重命名 | **v3.3→v3.5** | 单次≈40处，需IDE全局重命名+grep零残留确认 |

> 完整20个Pitfall详细分析和版本时间线图见 `references/common-pitfalls.md`

## 验证脚本

对你的品牌手册运行自动化检查：

```bash
python scripts/validate-manual.py path/to/your/manual/index.html
```

检查项目包括：
- [ ] 矛盾的 word-break / overflow-wrap 规则
- [ ] 全局 keep-all 反模式
- [ ] 负坐标 viewBox 上使用了 height:auto
- [ ] Unicode 12+ emoji（Windows上可能显示为方块）
- [ ] 内容段落上使用了行内 max-width
- [ ] 章节编号缺失或跳跃
- [ ] 版本号一致性
- [ ] 安全网CSS与JS的一致性

退出码：`0` = 全部通过，`1` = 有警告，`2` = 有错误。

## 数据脱敏声明

本Skill从一个真实的商业项目中提取。所有专有信息已被移除：

- ✅ 无品牌名称（已替换为 `[BRAND]`）
- ✅ 无产品描述或品类信息
- ✅ 无创始人/高管姓名
- ✅ 无口号/Slogan内容
- ✅ 无地理市场信息
- ✅ 无竞品引用
- ✅ 无吉祥物/角色详情
- ✅ 无实际Logo路径数据（仅占位几何图形）
- ✅ 无自定义字体文件引用

仅保留通用技术知识：CSS模式、SVG技术、排版系统、组件代码、调试工作流。

## 许可证

MIT License — 自由使用、修改和分发。

## 贡献指南

发现了新的坑？找到了更好的模式？欢迎贡献：

1. Fork 本仓库
2. 将你的发现添加到 `references/common-pitfalls.md` 或更新 `SKILL.md`
3. 提交 PR

## 致谢

基于制作41章、约15000行交互式品牌手册的真实经验构建，历经 **v1.0 → v7.5 共20+轮版本迭代**，融合了数十轮截图评审反馈中的改进。关键里程碑包括：v2.3 SVG矢量架构迁移、v3.2→v3.5 竞品配色审计与3轮副色选型、v6.2 品牌故事第4版重写、v7.x CJK排版系统定型。完整版本时间线和20个已记录陷阱详见 `references/common-pitfalls.md`。
