#!/usr/bin/env python3
"""
TubeForge M0 — Intel Stage
===========================
对标频道元数据采集模块。
只抓元数据（yt-dlp --flat-playlist -J），禁止下载任何视频/音频文件。

输入：channel yaml 中的 competitors 列表
输出：intel/<channel>.json（结构化元数据）+ intel/topics.md（选题分析）

用法：
    python -m tubeforge.stages.intel --channel prophecy
    python -m tubeforge.stages.intel --url "https://www.youtube.com/@channel" --output intel/single.json
"""

import json
import os
import subprocess
import sys
import time
import random
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INTEL_DIR = PROJECT_ROOT / "intel"
CONFIG_DIR = PROJECT_ROOT / "config" / "channels"


def load_channel_config(channel_id: str) -> dict:
    """从 config/channels/<channel_id>.yaml 加载频道配置"""
    import yaml
    path = CONFIG_DIR / f"{channel_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Channel config not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


def fetch_channel_metadata(channel_url: str, output_path: Path) -> dict:
    """
    用 yt-dlp --flat-playlist -J 抓对标频道元数据。
    仅抓取：标题、播放量、时长、发布时间、标签。
    禁止下载任何视频/音频文件。
    """
    cmd = [
        "yt-dlp",
        "--flat-playlist",       # 只采列表不下载
        "-J",                    # JSON 输出
        "--no-warnings",
        "--ignore-errors",
        "--extractor-args", "youtube:skip=webpage,player_client=android",  # 加速+反限速
        "--geo-bypass",
        channel_url,
    ]

    print(f"  Fetching: {channel_url}")
    start = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=45,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
    except subprocess.TimeoutExpired:
        print(f"  ⚠ Timeout: {channel_url}")
        return {"url": channel_url, "error": "timeout"}
    except FileNotFoundError:
        print("  ✗ yt-dlp not found. Install: pip install yt-dlp")
        return {"url": channel_url, "error": "yt-dlp not found"}

    if result.returncode != 0:
        print(f"  ⚠ yt-dlp error (rc={result.returncode}): {result.stderr[:200]}")
        return {"url": channel_url, "error": result.stderr[:500]}

    elapsed = time.time() - start
    print(f"  ✓ Done ({elapsed:.1f}s)")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON parse error: {e}")
        return {"url": channel_url, "error": str(e)}

    # 结构化提取元数据
    channel_info = {
        "url": channel_url,
        "channel_name": data.get("channel", data.get("uploader", "unknown")),
        "channel_id": data.get("channel_id", ""),
        "subscriber_count": data.get("channel_subscriber_count", 0),
        "video_count": data.get("channel_video_count", 0),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # 提取视频列表
    entries = data.get("entries", [])
    videos = []
    for entry in entries:
        if entry is None:
            continue
        video = {
            "id": entry.get("id", ""),
            "title": entry.get("title", ""),
            "url": f"https://www.youtube.com/watch?v={entry.get('id', '')}",
            "view_count": entry.get("view_count", 0),
            "duration": entry.get("duration", 0),        # 秒
            "upload_date": entry.get("upload_date", ""),  # YYYYMMDD
            "timestamp": entry.get("timestamp", 0),
            "tags": entry.get("tags", []),
            "description": entry.get("description", ""),
        }
        videos.append(video)

    result_data = {**channel_info, "videos": videos}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    return result_data


def analyze_topics(channel_data_list: list[dict], output_path: Path) -> str:
    """
    简单统计分析：高播放标题共同句式、选题聚类、发布频率。
    输出 topics.md 供人类/后续选题使用。
    """
    # 收集所有视频
    all_videos = []
    for cd in channel_data_list:
        if "videos" in cd and cd["videos"]:
            for v in cd["videos"]:
                v["_channel"] = cd.get("channel_name", "unknown")
                all_videos.append(v)

    # 按播放量排序
    all_videos.sort(key=lambda v: v.get("view_count", 0) or 0, reverse=True)

    top_20 = all_videos[:20]

    lines = []
    lines.append("# Intel Analysis — Topic Candidates\n")
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}\n")
    lines.append(f"Total videos analyzed: {len(all_videos)}\n")
    lines.append(f"Channels: {', '.join(set(v['_channel'] for v in all_videos))}\n")

    lines.append("## Top 20 Videos by Views\n")
    lines.append("| # | Title | Views | Duration | Channel |")
    lines.append("|---|---|---|---|---|")
    for i, v in enumerate(top_20[:20], 1):
        duration_min = v.get("duration", 0) // 60 if v.get("duration") else 0
        views = v.get("view_count", 0)
        title = v.get("title", "")[:60]
        channel = v.get("_channel", "")
        lines.append(f"| {i} | {title} | {views:,} | {duration_min}min | {channel} |")

    # 常见标题句式
    lines.append("\n## Common Title Patterns (high-view)\n")
    lines.append("_(Manual analysis recommended — patterns below are heuristic)_\n")
    # Simple word frequency in top titles
    from collections import Counter
    words = []
    for v in top_20:
        title = v.get("title", "")
        words.extend(title.lower().replace("–", " ").replace("-", " ").replace(":", " ").split())
    common = Counter(w.strip(".,!?\"'()[]{}|/\\").lower() for w in words if len(w.strip(".,!?\"'()[]{}|/\\")) > 3)
    lines.append("### Top Keywords in High-View Titles\n")
    for word, count in common.most_common(30):
        lines.append(f"- {word} ({count}x)")

    lines.append("\n## Candidate Topics (30 ideas)\n")
    lines.append("_(Placeholder — replace with DeepSeek/Claude analysis in full implementation)_\n")
    # Generate placeholder topics based on channel theme
    topics = [
        "The Prophecy That Predicted the French Revolution",
        "Nostradamus and the Rise of Napoleon — What the Quatrains Really Say",
        "Century I, Quatrain 1: Decoding the Secret Study",
        "The Quatrain That Foretold the London Fire of 1666",
        "Hitler in the Prophecies: Did Nostradamus See World War II?",
        "9/11 in Nostradamus: Coincidence or Prophecy?",
        "The Lost Century: Why Nostradamus Wrote Only 942 Quatrains",
        "How Nostradamus Calculated the Future Using Astrology",
        "The Quatrains That Haven't Come True Yet — A Countdown",
        "Nostradamus and the Internet: Could He Predict Modern Technology?",
        "The Kennedy Assassination in the Prophecies",
        "False Prophecies: When Nostradamus Got It Wrong",
        "The Hidden Meaning of Quatrain 2: Rod, Branch, and Water",
        "Nostradamus and the Great Plague: A Doctor's Prophecy",
        "Quatrain 72: The One About the Moon Landing",
        "Comparing Nostradamus to Biblical Prophets",
        "The Year 2026 in Nostradamus: What's Coming?",
        "Century X, Quatrain 72: The Most Famous and Most Misunderstood",
        "The Secret Code: Did Nostradamus Use Anagrams?",
        "Nostradamus's Letter to King Henry II: The Hidden Prophecy",
        "Why Nostradamus Wrote in Obscure French",
        "Quatrains That Predict Natural Disasters",
        "The Prophecies and the Antichrist: What Nostradamus Actually Said",
        "Catherine de Medici: The Queen Who Believed in Nostradamus",
        "How to Read Nostradamus Like a Scholar (Not a Conspiracy Theorist)",
        "Top 10 Quatrains That Predicted Modern Wars",
        "Does Nostradamus Predict the End of the World? (Spoiler: No)",
        "The Zodiac Clues Hidden in Every Quatrain",
        "Century VI, Quatrain 97: The One About the 'Beast'",
        "Nostradamus's Forgotten Medical Writings — The Doctor Behind the Prophet",
    ]
    for i, topic in enumerate(topics, 1):
        lines.append(f"{i}. {topic}")

    lines.append("")

    content = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return content


def run_for_channel(channel_id: str) -> None:
    """处理一个频道：抓元数据 + 分析"""
    print(f"\n{'='*60}")
    print(f"Intel Stage: channel={channel_id}")
    print(f"{'='*60}")

    config = load_channel_config(channel_id)
    competitors = config.get("competitors", [])
    if not competitors:
        print("  No competitors listed in config.")
        return

    channel_data_list = []
    for competitor in competitors:
        if not competitor or competitor.startswith("#"):
            continue
        channel_name = competitor.split("@")[-1].split("/")[0] if "@" in competitor else competitor.split("/")[-1]
        output_file = INTEL_DIR / f"{channel_name}.json"
        data = fetch_channel_metadata(competitor, output_file)
        channel_data_list.append(data)

        # 避免触发速率限制
        if len(channel_data_list) < len(competitors):
            delay = random.uniform(2.0, 5.0)
            time.sleep(delay)

    # 分析
    topics_file = INTEL_DIR / "topics.md"
    analyze_topics(channel_data_list, topics_file)
    print(f"\n✓ Intel done for {channel_id}")
    print(f"  Data: {INTEL_DIR}/")
    print(f"  Topics: {topics_file}")


def run_for_url(url: str, output_path: str | None = None) -> None:
    """处理单个 URL"""
    print(f"\n{'='*60}")
    print(f"Intel Stage: single URL")
    print(f"{'='*60}")

    if output_path:
        out = Path(output_path)
    else:
        channel_name = url.split("@")[-1].split("/")[0] if "@" in url else url.split("/")[-1]
        out = INTEL_DIR / f"{channel_name}.json"

    fetch_channel_metadata(url, out)
    print(f"\n✓ Data saved to {out}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="TubeForge M0 — Intel Stage")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--channel", help="Channel ID (from config/channels/<id>.yaml)")
    group.add_argument("--url", help="Single YouTube channel URL")
    parser.add_argument("--output", help="Output path for --url mode (default: intel/<channel>.json)")
    args = parser.parse_args()

    if args.channel:
        run_for_channel(args.channel)
    elif args.url:
        run_for_url(args.url, args.output)


if __name__ == "__main__":
    main()
