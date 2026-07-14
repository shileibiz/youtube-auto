# TubeForge

YouTube 长视频全自动生产线：选题 → 原创英文文案（公有领域原典）→ AI 配音 →
AI 配图 → FFmpeg 自动剪辑（Ken Burns + 字幕 + BGM）→ 成品 + SEO 元数据 + 封面。

目标形态：`tubeforge make --channel buddhism --topic "..."` 一分钟出一条 10–15 分钟成品。

## 与参考方法论的三处关键差异

1. **不洗稿**：对标账号只做元数据情报，正文从公有领域原典原创生成。
   规避 YPP "reused content" 拒审与版权风险，且省掉 fine-tune 全套成本。
2. **成本趋近零**：Gemini 免费生图 API + edge-tts 免费配音 + DeepSeek 文案 +
   自有 VPS 渲染。参考方案月成本 $60–80 → 本方案 ≈ $0。
3. **句子级 TTS 定时间轴**：逐句合成使字幕与切图点由数据直接推导，
   免去语音对齐环节，自动剪辑模块复杂度减半。

## 快速开始

```bash
pip install requests pillow pyyaml edge-tts yt-dlp
export GEMINI_API_KEY=...  DEEPSEEK_API_KEY=...
python -m tubeforge intel --channel buddhism        # 对标情报+选题库
python -m tubeforge make  --channel buddhism --topic "Why Letting Go Sets You Free"
```

## 文档索引

- CLAUDE.md — AI 执行规范（架构/模块契约/参数/规则）
- ROADMAP.md — 阶段计划与 Gate（当前：Phase 0）
- FORBIDDEN.md — 禁止重犯清单
- config/channels/ — 频道配置（赛道/风格例句/声音/封面模板）
