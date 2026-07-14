# TubeForge — CLAUDE.md（AI 执行规范）

> 本文件面向 AI（Claude Code / Opus）。人类文档见 README.md，进度见 ROADMAP.md。
> 框架约束：AI能力 = 模型能力 × 约束质量 × 语料上下文。本文件是"约束质量"层，必须严格遵守。

## 1. 项目目标

全自动生产 YouTube 长视频（不出镜/不出声/AI图片轮播+AI配音+字幕+BGM），
面向欧美英语受众的高RPM赛道（佛学/预言/基督教等公有领域内容赛道），
目标：单条视频从选题到成品 ≤ 2 分钟人工介入，边际成本趋近 $0。

商业逻辑（不可遗忘的前提）：
- 收入 = 播放量 × RPM。RPM 由赛道、观众地区、视频类型决定。
- 只做长视频（10-15分钟），8分钟以上可插中段广告，RPM 比短视频高 30-100 倍。
- YPP 门槛：1000 粉丝 + 12个月内 4000 小时公开播放。

## 2. 核心设计决策（不可推翻，如需变更先与人类确认）

### D1. 内容来源 = 公有领域原典 + 原创生成，禁止洗稿
- **禁止**下载对标视频、禁止转写对标音频、禁止对他人文稿做任何形式的改写/伪原创。
- 对标账号只采集**元数据**（标题/播放量/发布频率/封面URL/标签），用于选题和包装情报。
- 正文从 `corpus/` 公有领域文本（佛经英译、KJV圣经、诺查丹玛斯等）+ 选题出发原创生成。
- 理由：YPP 拒审第一大原因是 "reused content"；洗稿链路 = 账号资产建立在流沙上。

### D2. 供应商全部走抽象层，默认免费档
| 能力 | 默认（免费） | Fallback | 付费升级位 |
|---|---|---|---|
| 文案LLM | DeepSeek API | — | Claude(QC用) |
| 生图 | Gemini `gemini-2.5-flash-image`（AI Studio免费key, ~10RPM） | Cloudflare Workers AI Flux schnell | Runware+FluxDev($0.002/张) |
| TTS | edge-tts（免费，如 en-US-AndrewNeural） | — | ElevenLabs / OpenAI TTS |
| 渲染 | FFmpeg 本地 | — | — |

所有 provider 实现统一接口，配置文件切换，业务代码零改动。

### D3. 句子级 TTS 驱动整条时间轴（渲染架构支点）
逐句合成配音 → 每句精确时长已知 → 由此**推导**（而非检测）：
- 字幕时间轴（每句 = 一条字幕cue）
- 切图点（图片切换只发生在句子结束处，满足"说完一句话再切"）
禁止引入 whisper/强制对齐等检测方案，属于不必要的复杂度。

### D4. 阶段产物落盘，全流程可断点续跑
每条视频一个工作目录，每个 stage 的输出是下一个 stage 的输入文件。
stage 运行前检查输出是否已存在，存在则跳过（`--force` 覆盖）。
生图/TTS 单张/单句失败只重试该项，不重跑整个 stage。

## 3. 架构与目录

```
tubeforge/
├── CLAUDE.md / README.md / ROADMAP.md / FORBIDDEN.md   # FORBIDDEN.md = 禁止重犯清单
├── config/
│   ├── channels/<channel>.yaml      # 每频道一份：赛道/风格/声音/prompt模板
│   └── render.yaml                  # 渲染参数（见 §5，来自实测值，改前先问人类）
├── corpus/<niche>/                  # 公有领域原典，纯txt/md，按主题分文件
├── bgm/                             # 无版权BGM池（≥10首），每首附 LICENSE.txt 来源记录
├── tubeforge/
│   ├── cli.py                       # 入口：tubeforge make/script/tts/images/render/thumb/intel
│   ├── pipeline.py                  # stage 编排 + 断点续跑
│   ├── stages/
│   │   ├── intel.py      # M0 对标元数据采集（yt-dlp --flat-playlist，仅元数据）
│   │   ├── script.py     # M1 文案+SEO元数据生成
│   │   ├── tts.py        # M2 逐句配音
│   │   ├── images.py     # M3 分段生图
│   │   ├── render.py     # M4 FFmpeg 合成
│   │   ├── thumbnail.py  # M5 封面
│   │   └── publish.py    # M6 发布（Phase 4 前只输出人工上传包）
│   └── providers/
│       ├── llm.py / images.py / tts_engines.py   # 统一接口 + 各家实现
└── videos/<date>_<slug>/            # 工作目录（见 §4 产物契约）
```

## 4. 模块规格（I/O 契约）

### M0 intel — 对标情报
- 输入：频道URL列表（config/channels/*.yaml 的 `competitors:`）
- 行为：`yt-dlp --flat-playlist -J` 抓元数据；**禁止下载任何视频/音频文件**
- 输出：`intel/<channel>.json`（标题、播放、时长、发布时间、标签）+ `intel/topics.md`
  （DeepSeek 分析：高播放标题的共同句式、选题聚类、发布频率，生成 30 条候选选题）

### M1 script — 文案 + SEO
- 输入：`--topic` + channel 配置（风格指南）+ corpus 相关篇章（检索：关键词匹配即可，不上RAG）
- 生成约束：
  - 英文 1500–2200 词（≈ 10–15 分钟 @ 140wpm）
  - 前 5 秒必须有 Hook（悬念/问题/反直觉陈述），前 30 秒不得平铺直叙
  - 风格指南用**具体例句**表达，不用形容词（channel yaml 内维护）
  - 违禁词过滤清单：graphic violence 词汇、争议性话题词（影响广告适投性）
- QC 环节：字数校验、违禁词扫描、可选 Claude 复核"AI味"（Phase 2 起）
- 输出：
  - `script.md`（正文，按空行分段落）
  - `segments.json`（分段结果：每段 40–70 词，每段对应一张图，目标 18–28 段）
  - `meta.json`（title ≤60字符且核心关键词前置 / description 首行含关键词 / tags 10–15个由精准到宽泛 / category / language=en）

### M2 tts — 逐句配音
- 输入：`segments.json`
- 行为：每段按句切分（句号/问号/叹号，不得在句中切断）→ edge-tts 逐句合成
  （同一 voice + rate + pitch，禁止中途换参数）→ 按序拼接
- 输出：`audio/voice.wav` + `audio/timing.json`
  （结构：`[{seg: i, sentences: [{text, start, end}]}]`，start/end 为全局时间轴秒）

### M3 images — 分段生图
- 输入：`segments.json` + channel 风格预设
- 行为：每段先由 DeepSeek 生成"图片描述prompt"（不是直译！是转译为适合生图的场景描述），
  套用风格预设前后缀；宗教内容敏感词软化映射表（hell→"vast dark valley" 等，
  维护在 channel yaml）；调 provider 生图，429 退避重试，单图重试 3 次；
  失败超限自动降级到 fallback provider
- 频控：Gemini 免费档 10 RPM，串行 + 6.5s 间隔
- 输出：`images/seg_001.jpg ...`（与段号一一对应）+ `images/prompts.json`

### M4 render — FFmpeg 合成（最复杂模块，按此拆解实现）
- 输入：timing.json + images/ + voice.wav + bgm/
- 步骤：
  1. **时间轴构建**：每段图片的展示时长 = 该段所有句子音频总时长；不足 5s 的段与相邻段合并图片
  2. **逐段渲染**：每张图 → zoompan 滤镜做 Ken Burns（参数见 render.yaml）→ 中间片段 mp4
  3. **拼接**：xfade 转场（每条视频固定一种，从四种中随机选定）
  4. **字幕**：由 timing.json 生成 .ass（样式见 render.yaml）→ 烧录
  5. **混音**：voice + BGM（随机选 1 首循环），BGM 音量、淡入淡出见 render.yaml
  6. 输出 `final.mp4`
- 实现约束：直接调 ffmpeg subprocess，**禁用 moviepy**（长视频慢且易崩）；
  中间片段保留在 `render_tmp/` 便于断点续跑，成功后清理

### M5 thumbnail — 封面
- 输入：meta.json + channel 封面模板
- 行为：生图（1280×720 或裁切）+ PIL 叠加大号标题词（≤4个词，高对比描边），
  模板参数（字体/字号/位置/描边色）在 channel yaml
- 输出：`thumb.jpg`

### M6 publish — 发布
- Phase 4 之前：只生成"人工上传包" `upload_package/`
  （final.mp4 + thumb.jpg + meta.txt 复制粘贴版），由人在**浏览器/家庭网络**上传
- Phase 4：YouTube Data API `videos.insert`（注意配额：每次上传 1600 units，默认日配额 10000
  ≈ 6条/天/project）+ 定时发布（publishAt 设为美东 19:00–21:00）
- **禁止**在 VPS（数据中心IP）上执行发布动作，API 上传亦须评估 IP 风险后再启用

## 5. 渲染参数（config/render.yaml 初始值，实测值不得随意改）

```yaml
image_min_display_sec: 5        # 每图最短展示
kenburns_pan_pct: 21            # 位移 ±21%
kenburns_zoom: [1.0, 1.15]      # 缩放区间
transition: random_fixed        # 渐显/缩放/弹跳/雨刷 四选一，单视频内固定
transition_duration_sec: 0.7
subtitle: {position: bottom_center, font: sans, color: white, outline: black}
bgm_volume_pct: 25              # 人声的 20–30%
bgm_fade_in_sec: 3
bgm_fade_out_sec: 5             # 结束前 5 秒淡出
output: {resolution: 1920x1080, fps: 30, vcodec: libx264, acodec: aac}
video_target_minutes: [10, 15]  # 硬约束：>8min 开中段广告；<20min 保完播
```

## 6. 编码规则

- Python 3.11+，只用标准库 + requests + Pillow + PyYAML + edge-tts + yt-dlp；不引框架
- 每个 stage 可独立 CLI 运行：`python -m tubeforge <stage> --dir videos/xxx`
- 所有外部 API 调用：超时 + 重试(退避) + 失败落日志 `videos/<dir>/pipeline.log`
- 密钥全部走环境变量（GEMINI_API_KEY / DEEPSEEK_API_KEY / CF_API_TOKEN），禁止入库
- 每次实现/修改模块后更新 ROADMAP.md 进度；踩坑写入 FORBIDDEN.md
- 生成文案的风格指南修改：只允许增删**例句**，不允许写抽象形容词

## 7. 风险清单（设计层面已知，实现时不得引入对应行为）

1. 版权音乐 = 头号翻车原因 → 只用 bgm/ 池内文件，每首必须有 LICENSE.txt，缺证不入池
2. 发布后禁止修改标题/封面（重置推流）→ publish 模块不提供"更新已发布视频"功能
3. 新频道 ≤2 条/天 → pipeline 队列层做硬限制
4. 零播放排查顺序：版权音乐→水印→违禁词→数据中心IP→删视频过多（写入 FORBIDDEN.md）
5. AdSense 地址必须真实（PIN 实体信件验证）→ 属人工事项，ROADMAP P0 清单内
6. 生图内容审核：宗教词触发过滤 → 敏感词软化映射表，命中过滤自动换措辞重试
