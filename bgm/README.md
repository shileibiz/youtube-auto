# BGM Pool — TubeForge

> 无版权 BGM 下载源清单（CC0 / Royalty-Free）
> 每首 BGM 入库前必须在 bgm/ 内有 LICENSE.txt 记录来源和许可类型。
> 禁止使用池外音乐（见 FORBIDDEN.md §1）。

## 推荐下载网站（≥10）

| # | 网站 | 许可类型 | 需署名？ | 备注 |
|---|------|---------|---------|------|
| 1 | [Pixabay Music](https://pixabay.com/music/) | Pixabay License (≈CC0) | 否 | 海量分类，搜索友好，支持直接下载 |
| 2 | [Uppbeat](https://uppbeat.io/) | Royalty-Free | 否（免费账号） | 每月 6 下载免费，需注册 |
| 3 | [Free Music Archive](https://freemusicarchive.org/) | CC0 / CC BY | 按曲目 | 历史悠久，分类齐全，注意区分许可 |
| 4 | [Incompetech (Kevin MacLeod)](https://incompetech.com/music/royalty-free/) | CC BY 4.0 | 需署名 | 经典 BGM 库，种类极全，需署名 |
| 5 | [Freesound.org](https://freesound.org/) | CC0 / CC BY / CC Sampling+ | 按曲目 | 侧重音效，但也有很多音乐 loop，筛选 CC0 |
| 6 | [Musopen](https://musopen.org/music/) | CC0 / Public Domain | 否 | 古典音乐为主（贝多芬、莫扎特等），公共领域 |
| 7 | [Jamendo](https://www.jamendo.com/) | CC BY / CC0 / CC NC | 按曲目 | 大量独立音乐人作品 |
| 8 | [Chosic](https://www.chosic.com/free-music/) | CC0 / CC BY | 按曲目 | 支持按情绪/风格/乐器搜索 |
| 9 | [YouTube Audio Library](https://www.youtube.com/audiolibrary/music) | Royalty-Free | 否 | YouTube 官方库，需登录 Google 账号下载 |
| 10 | [FreePD](https://freepd.com/) | CC0 / Public Domain | 否 | 全部无版权，不要求署名 |
| 11 | [Purple Planet](https://www.purple-planet.com/) | Royalty-Free | 需署名 | 制作精良，分类清晰 |
| 12 | [Bensound](https://www.bensound.com/royalty-free-music) | Royalty-Free | 需署名（免费版） | 电影感 BGM，需署名 |
| 13 | [Sampld](https://sampld.com/) | Royalty-Free | 否 | 较新平台，分类较现代 |
| 14 | [Royalty Free Music Library](https://www.storyblocks.com/audio) | Royalty-Free (付费) | 否 | 付费订阅，但质量最高，备选 |

## 入库流程

1. 从以上来源下载 BGM（优先 CC0 / 无需署名的曲目）
2. 以 `bgm_01.mp3`, `bgm_02.mp3` ... 命名放入 `bgm/`
3. 每首附带 `bgm_01_LICENSE.txt`，包含：
   - 来源 URL
   - 作者/创作者
   - 许可类型（CC0 / CC BY 4.0 / Royalty-Free 等）
   - 署名要求（如需署名，署名文本）
4. 在 `config/render.yaml` 的 `bgm_pool:` 中引用

## 赛道推荐风格

| 赛道 | 推荐 BGM 风格 |
|------|-------------|
| 预言（Nostradamus） | 神秘 / 氛围 / 中世纪 / 弦乐缓慢 / 低音 drone |
| 佛学 | 冥想 / 藏传 / 颂钵 / 自然 ambient |
| 基督教 | 风琴 / 合唱 / 轻柔管弦乐 |

## 注意

- **禁止使用有版权音乐**（YouTube Content ID 自动检测，版权音乐 = 收益归零）
- 即使 CC BY 需署名，也应在 description 加入「Music: ...」行
- 首选无署名要求的 CC0 曲目，降低人工核对成本
