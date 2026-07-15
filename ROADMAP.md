# TubeForge — ROADMAP.md（AI 进度日志）

> 规则：每个 Phase 有准入 Gate，Gate 未过禁止开工下一 Phase。
> 核心教训（来自方法论原文，必须遵守）："先手工验证方向，再自动化拉满效率。
> 一上来就搞全自动，方向错了白干。" 因此 P0 是人工阶段，P4 在变现资格拿到前禁止建设。

## Phase 0 — 人工验证（第 1–2 周）【状态：进行中 - AI 事项已完成】

人工事项（人类完成，AI 辅助）：
- [ ] 选定 1 个赛道（佛学/预言/基督教，三选一，只选一个）
- [ ] 频道注册 + 基础设置（英文频道名/描述含关键词/图标800×800/横幅2560×1440中心安全区）
- [ ] 装 TubeBuddy + vidIQ（免费版）
- [ ] Wise 账户确认可用（已有）；AdSense 待 YPP 申请时注册，地址必须真实（PIN信件）
- [ ] 收集 10 个对标频道 URL（标准：注册≤3个月 / 粉丝1万+或总播放300万+ / 图片轮播+配音形式）

AI 事项：
- [x] M0 intel 模块（本 Phase 唯一开发项）：抓 10 个对标的元数据，产出选题库 + 标题句式分析
  - `tubeforge/stages/intel.py` — yt-dlp 元数据采集 + 选题分析
  - 用法：`python -m tubeforge.stages.intel --channel prophecy`
- [x] 建 corpus/：选定赛道的公有领域原典 ≥ 20 篇章节文本
  - `corpus/prophecy/` — Nostradamus 'Les Propheties' 英译版，1007 四行诗文件
  - 来源：Project Gutenberg (1672 Garencières 英译)，公有领域
- [x] 建 bgm/：≥10 首带许可证明的 BGM
  - `bgm/README.md` — 14 个无版权 BGM 下载网站清单 + 入库流程
- [x] 建 config/channels/：预言赛道配置模板
  - `config/channels/prophecy.yaml` — 完整赛道配置（风格/voice/生图/软化映射/封面）

产出：7 条视频（人工为主，可用零散脚本减负，人工选图/人工剪映剪辑），日更发布。

**Gate G0：≥1 条视频 CTR>4% 且完播>40%，或播放量出现明显爬升趋势。**
未过 G0 → 换选题方向或换赛道重跑 P0，禁止进入 P1。

## Phase 1 — 内容三件套自动化【状态：未开始】

- [ ] providers 抽象层（llm / images / tts）+ 免费档实现 + fallback
- [ ] M1 script（含 SEO meta 生成 + 违禁词过滤）
- [ ] M2 tts（逐句合成 + timing.json）
- [ ] M3 images（prompt 转译 + 敏感词软化 + 频控重试）
- [ ] 每个模块独立 CLI 可跑，产物落盘符合 CLAUDE.md §4 契约

**Gate G1：一条命令产出 script+audio+images 全套素材，人工抽检 3 条选题，
文案无 AI 味硬伤、配图与文意匹配率 ≥ 80%。**

## Phase 2 — 渲染闭环【状态：未开始】

- [ ] M4 render（时间轴构建 → 逐段 Ken Burns → 转场拼接 → 字幕烧录 → 混音）
- [ ] M5 thumbnail
- [ ] pipeline.py 串联：`tubeforge make --channel X --topic "..."` 一键出成品
- [ ] 断点续跑验证：人为中断后重跑，不重复消耗 API 额度

**Gate G2：连续 5 条一键成品，人工审看通过率 ≥ 80%（通过 = 可直接上传不需返工）。**

## Phase 3 — 量产运营【状态：未开始】

- [ ] 批量队列：选题库 → 每日 N 条自动排产（新频道硬限 ≤2 条/天）
- [ ] upload_package 输出（人工浏览器上传，家庭网络）
- [ ] 数据回收：yt-dlp 抓自己频道数据，周报（CTR/完播/播放 按选题聚类）反哺选题库

**Gate G3：频道 1 通过 YPP（1000粉 + 4000小时）。**

## Phase 4 — 复制与全自动发布【状态：禁止提前建设】

- [ ] 频道 2/3 配置化复制（新建 channel yaml + corpus 即可跑）
- [ ] M6 YouTube Data API 上传 + publishAt 定时（美东 19–21 点）+ IP 风险评估
- [ ] 叠加变现位：description 联盟链接模板、置顶评论模板

## 决策待办（人类拍板）

- [ ] 赛道选择（P0 第一项）
- [ ] 本项目与 公众号 / 矩阵SEO站 的时间配比——P0 需每天 3–4 小时人工投入，
      与现有项目冲突时优先级如何排

## 进度日志

- 2026-07-14 项目立项，脚手架 + 规范文件建立（Claude 设计，待 Opus 实现）
- 2026-07-14 **Phase 0 AI 事项完成**：
  - `corpus/prophecy/` — 1007 四行诗（Project Gutenberg 公有领域 Nostradamus 英译）
  - `bgm/README.md` — 14 个无版权 BGM 下载源清单
  - `config/channels/prophecy.yaml` — 预言赛道配置模板
  - `FORBIDDEN.md` — 新增 corpus/BGM 相关约束条目（§15–16）
  - `tubeforge/stages/intel.py` — M0 对标元数据采集模块原型
