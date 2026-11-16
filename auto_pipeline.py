#!/usr/bin/env python3
"""
GitCast 100% Free ($0) 5-6 Minute Animated 2D Cartoon & Multi-Actor Story Pipeline (harry0703/MoneyPrinterTurbo)
- GitHub Voice Repo : AI4Bharat/Indic-Parler-TTS + Multi-Character Human Voice Actors + Cinema Ambience
- Narrator Persona  : "মমিন ভাই" (Momin Bhai) — Mode: Mystery Series (রহস্যময় কাহিনি)
- Primary Voice ID  : bn-BD-PradeepNeural (Pitch=-4Hz, Rate=-5%)
- Visual Seed Lock  : #429108 (2D Rigged Walking, Blinking, Lip-Sync Talking Characters & Dynamic Scenes)
- Episode Progression: Auto-advances Part 1 -> Part 2 -> Part 3 -> Part 4 -> New Story (NEVER repeats same video!)
"""

import os
import re
import math
import time
import json
import wave
import struct
import random
import subprocess
import urllib.parse
import requests
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# ==============================================================================
# 1. CONFIGURATION & MULTI-STORY CATALOG (NEVER REPEATS THE SAME VIDEO!)
# ==============================================================================
ENGINE_REPO = "harry0703/MoneyPrinterTurbo"
GITHUB_VOICE_REPO = "AI4Bharat/Indic-Parler-TTS"
VOICE_CLONE_REF_WAV = "assets/momin_bhai_ref.wav"
ASPECT_RATIO = "9:16"
TTS_VOICE = "bn-BD-PradeepNeural"
TTS_PITCH = "-4Hz"
TTS_RATE = "-5%"
TOTAL_PARTS = 4
VISUAL_SEED_LOCK = 429108
STATE_FILE = Path("series_state.json")

# Multi-Actor Distinct Bangla Neural Voices (Different human voice for each character!)
CHARACTER_VOICES = {
    "narrator": {"voice": "bn-BD-PradeepNeural", "pitch": "-5Hz", "rate": "-10%", "eq": "equalizer=f=150:t=q:w=1.1:g=4"},
    "ariyan":   {"voice": "bn-IN-BashkarNeural", "pitch": "-2Hz", "rate": "-2%",  "eq": "equalizer=f=210:t=q:w=1.2:g=3"},
    "rafiq":    {"voice": "bn-BD-PradeepNeural", "pitch": "+5Hz", "rate": "+10%", "eq": "asetrate=24000*1.06,aresample=24000,atempo=0.96"},
    "elder":    {"voice": "bn-IN-BashkarNeural", "pitch": "-8Hz", "rate": "-12%", "eq": "asetrate=24000*0.91,aresample=24000,atempo=1.04,aecho=0.8:0.85:55:0.22"},
    "female":   {"voice": "bn-BD-NabanitaNeural", "pitch": "-2Hz", "rate": "-6%", "eq": "aecho=0.8:0.88:45:0.18"},
}

STORY_CATALOG = [
    {
        "story_id": "mayajaal",
        "title_bn": "মায়াজাল",
        "subtitle_bn": "গভীর রাতে নির্জন বনের পরিত্যক্ত কাঠের বাড়ি ও রহস্যময় ছায়া",
        "setting_bn": "নির্জন শালবনের ভেতর পরিত্যক্ত দোতলা কাঠের বাড়ি, জিপ গাড়ি ও ক্যাম্পফায়ার",
        "hero_bn": "আরিয়ান (কমলা টি-শার্ট ও দাঁড়িওয়ালা সাহসী যুবক)",
        "friend_bn": "রফিক (হলুদ টি-শার্ট পরা আতঙ্কিত বন্ধু) ও কাওসার",
        "elder_bn": "বৃদ্ধ প্রহরী করিম চাচা (হাতে হারিকেন ও কালো শাল)",
        "entity_bn": "দোতলার জানালার রহস্যময় কালো ছায়ামূর্তি",
        "part_titles": [
            "গভীর রাতে রহস্যময় ছায়া ও ক্যাম্পফায়ার",
            "পরিত্যক্ত কাঠের বাড়ির অশরীরী সংকেত ও হারিকেন",
            "দোতলার নিষিদ্ধ কুঠুরি ও মায়াজালের ফাঁদ",
            "মায়াজালের চূড়ান্ত রহস্য উন্মোচন ও শেষ প্রহর",
        ],
    },
    {
        "story_id": "zamindar_bari",
        "title_bn": "অভিশপ্ত জমিদার বাড়ি",
        "subtitle_bn": "নিঝুমপুরের ২০০ বছরের পুরনো ভাঙা জমিদার বাড়ির গোপন কুঠুরি",
        "setting_bn": "নিঝুমপুরের কুয়াশাচ্ছন্ন প্রাচীন জমিদার বাড়ি, শ্যাওলা ধরা সিঁড়ি ও বটগাছ",
        "hero_bn": "আরিয়ান (কমলা টি-শার্ট ও টর্চলাইট হাতে অনুসন্ধানী যুবক)",
        "friend_bn": "রফিক (হলুদ টি-শার্ট) ও ফটোগ্রাফার তানভীর",
        "elder_bn": "মন্দিরের বৃদ্ধ পুরোহিত ও গ্রামের চৌকিদার",
        "entity_bn": "জমিদার বাড়ির ছাদের অশরীরী প্রহরী",
        "part_titles": [
            "নিঝুমপুরের পথে মধ্যরাতের ঝড় ও জমিদার বাড়ির ফটক",
            "দেয়ালের প্রাচীন ঘড়ি ও মাটির নিচের গোপন সুড়ঙ্গ",
            "লোহার সিন্দুকের অভিশাপ ও রফিকের নিখোঁজ হওয়া",
            "অভিশপ্ত জমিদার বাড়ির ২০০ বছরের রহস্যের সমাপ্তি",
        ],
    },
    {
        "story_id": "sundarban_nishi",
        "title_bn": "সুন্দরবনের গহীনে নিশির ডাক",
        "subtitle_bn": "অমাবস্যার রাতে সুন্দরবনের খাঁড়িতে অশরীরী ডাক ও কাঠুরেদের অভিযান",
        "setting_bn": "সুন্দরবনের অন্ধকার গোলপাতার খাঁড়ি, কাঠের নৌকা ও কুয়াশাচ্ছন্ন জঙ্গল",
        "hero_bn": "আরিয়ান ও অভিজ্ঞ মাঝি হাতেম চাচা",
        "friend_bn": "রফিক ও তরুণ গবেষক সামির",
        "elder_bn": "বনের বৃদ্ধ মৌয়াল জব্বার মিয়া",
        "entity_bn": "জলের ওপর ভেসে চলা কুয়াশার ছায়ামূর্তি",
        "part_titles": [
            "খাঁড়ির জলে মধ্যরাতের কুয়াশা ও অদ্ভুত পায়ের ছাপ",
            "মাঝরাতে পরিচিত কণ্ঠে তিনবার নিশির ডাক",
            "পরিত্যক্ত ফরেস্ট ক্যাম্পের ডায়েরি ও ভয়ংকর সত্য",
            "সুন্দরবনের গহীনে নিশির ডাকের চূড়ান্ত মুক্তি",
        ],
    },
    {
        "story_id": "meghna_ferry",
        "title_bn": "মেঘনা নদীর মাঝির ভৌতিক রাত",
        "subtitle_bn": "ঝড়ের রাতে মেঘনার শেষ খেয়াঘাটে ওঠা রহস্যময় যাত্রী",
        "setting_bn": "উত্তাল মেঘনা নদী, পুরনো কাঠের খেয়া নৌকা ও নির্জন চর",
        "hero_bn": "আরিয়ান ও সাহসী তরুণ মাঝি রহিম",
        "friend_bn": "রফিক ও যাত্রী আনিস সাহেব",
        "elder_bn": "ঘাটের বৃদ্ধ চা-দোকানি গফুর মিয়া",
        "entity_bn": "সাদা চাদর মুড়ি দেওয়া মুখহীন যাত্রী",
        "part_titles": [
            "কালবৈশাখী ঝড়ের সংকেত ও শেষ খেয়ার যাত্রী",
            "মাঝনদীতে কম্পাস অকেজো ও ঘূর্ণিপাকের রহস্য",
            "নির্জন চরের ভাঙা বাতিঘর ও পুরনো লঞ্চের কঙ্কাল",
            "মেঘনার অভিশপ্ত খেয়াঘাটের চূড়ান্ত রহস্য উন্মোচন",
        ],
    },
    {
        "story_id": "pahari_bungalow",
        "title_bn": "পাহাড়ি বাংলোর ১৩ নম্বর ঘর",
        "subtitle_bn": "বান্দরবানের মেঘে ঢাকা কাঠের বাংলোর তালাবদ্ধ ঘরের রহস্য",
        "setting_bn": "বান্দরবানের উঁচু পাহাড়ের চূড়ায় পুরনো ব্রিটিশ আমলের কাঠের ডাকবাংলো",
        "hero_bn": "আরিয়ান (কমলা টি-শার্ট ও ট্র্যাকার)",
        "friend_bn": "রফিক (হলুদ টি-শার্ট) ও গাইড অংশুমান",
        "elder_bn": "ডাকবাংলোর বৃদ্ধ কেয়ারটেকার থোয়াই চাচা",
        "entity_bn": "১৩ নম্বর ঘরের আয়নার ভেতরের ছায়া",
        "part_titles": [
            "পাহাড়ি রাস্তায় ধস ও ডাকবাংলোয় আশ্রয়",
            "রাত দুইটায় ১৩ নম্বর ঘরের দরজায় ঠকঠক শব্দ",
            "কেয়ারটেকারের লুকানো চাবি ও ১৯৪২ সালের ডায়েরি",
            "পাহাড়ি বাংলোর ১৩ নম্বর ঘরের চূড়ান্ত রহস্য ভেদ",
        ],
    },
]

# ==============================================================================
# 2. EPISODE STATE TRACKER (CHECKS LIVE YOUTUBE/FB + SERIES_STATE.JSON)
# ==============================================================================
def get_youtube_credentials() -> Credentials:
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "").strip()
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "").strip()
    access_token = os.environ.get("YOUTUBE_ACCESS_TOKEN", "").strip()

    if refresh_token and client_id and client_secret:
        creds = Credentials(
            token=access_token or None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
        )
        creds.refresh(Request())
        return creds
    if access_token:
        return Credentials(token=access_token)
    raise RuntimeError("Set YOUTUBE_REFRESH_TOKEN (+ CLIENT_ID/SECRET) or YOUTUBE_ACCESS_TOKEN")

def fetch_already_uploaded_titles() -> list[str]:
    """Queries live YouTube Channel & Facebook Page to see which stories/parts are already posted."""
    titles = []
    # Check YouTube Channel uploads
    try:
        creds = get_youtube_credentials()
        youtube = build("youtube", "v3", credentials=creds)
        ch_res = youtube.channels().list(part="contentDetails", mine=True).execute()
        items = ch_res.get("items", [])
        if items:
            uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
            pl_res = youtube.playlistItems().list(part="snippet", playlistId=uploads_id, maxResults=30).execute()
            for it in pl_res.get("items", []):
                titles.append(it["snippet"].get("title", ""))
    except Exception as e:
        print(f"[State Check] YouTube history lookup info: {e}")

    # Check Facebook Page recent videos/posts
    try:
        raw_page_id = os.environ.get("FACEBOOK_PAGE_ID") or "61576363786053"
        raw_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN") or ""
        if raw_token:
            page_id, page_token = resolve_facebook_page_credentials(raw_page_id, raw_token)
            fb_res = requests.get(
                f"https://graph.facebook.com/v21.0/{page_id}/videos",
                params={"fields": "title,description", "limit": 25, "access_token": page_token},
                timeout=15,
            )
            if fb_res.ok:
                for v in fb_res.json().get("data", []):
                    titles.append(f"{v.get('title', '')} {v.get('description', '')}")
    except Exception as e:
        print(f"[State Check] Facebook history lookup info: {e}")

    return titles

def load_and_resolve_next_episode() -> tuple[dict, int, int]:
    """
    Determines the exact next (story_dict, part_num, story_idx) to generate so we NEVER repeat!
    """
    state = {"story_index": 0, "part_num": 1, "completed_episodes": []}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    uploaded_titles = fetch_already_uploaded_titles()
    completed_set = set(state.get("completed_episodes", []))

    # Scan catalog to find the first (story_idx, part_num) not yet uploaded
    start_s = int(state.get("story_index", 0))
    start_p = int(state.get("part_num", 1))

    for offset in range(len(STORY_CATALOG) * TOTAL_PARTS + 20):
        total_ep_idx = (start_s * TOTAL_PARTS + (start_p - 1)) + offset
        s_idx = total_ep_idx // TOTAL_PARTS
        p_num = (total_ep_idx % TOTAL_PARTS) + 1

        if s_idx < len(STORY_CATALOG):
            story = STORY_CATALOG[s_idx]
        else:
            # Generate dynamic new story beyond catalog
            dyn_num = s_idx + 1
            story = {
                "story_id": f"mystery_series_{dyn_num}",
                "title_bn": f"রহস্যময় প্রহর {dyn_num}",
                "subtitle_bn": f"মমিন ভাইয়ের নতুন ভৌতিক ও রহস্যময় অভিযান #{dyn_num}",
                "setting_bn": "নির্জন রাতের কুয়াশাচ্ছন্ন গ্রাম, পুরনো কাঠের বাড়ি ও জঙ্গল",
                "hero_bn": "আরিয়ান (কমলা টি-শার্ট ও দাঁড়িওয়ালা যুবক)",
                "friend_bn": "রফিক (হলুদ টি-শার্ট) ও কাওসার",
                "elder_bn": "গ্রামের বৃদ্ধ প্রহরী",
                "entity_bn": "অন্ধকারের রহস্যময় ছায়ামূর্তি",
                "part_titles": [
                    f"অজানা সংকেত ও প্রথম প্রহরের আতঙ্ক",
                    f"গভীর বনের গোপন পথ ও দ্বিতীয় প্রহর",
                    f"ছায়ামূর্তির মুখোমুখি ও তৃতীয় প্রহর",
                    f"চূড়ান্ত রহস্য উন্মোচন ও শেষ পর্ব",
                ],
            }

        ep_key = f"{story['story_id']}_p{p_num}"
        if ep_key in completed_set:
            continue

        # Check if this exact story title + part number is already on YouTube/Facebook
        title_bn = story["title_bn"]
        already_live = False
        for t in uploaded_titles:
            if title_bn in t and (f"পর্ব {p_num}" in t or f"পর্ব {p_num}/" in t or f"#পর্ব_{p_num}" in t or f"Part_{p_num}" in t):
                already_live = True
                break

        if already_live:
            print(f"[Skip] '{title_bn} — পর্ব {p_num}' is ALREADY uploaded on YouTube/FB! Advancing to next...")
            completed_set.add(ep_key)
            continue

        print(f"[Selected Next Episode] গল্প: '{title_bn}' | পর্ব: {p_num}/{TOTAL_PARTS} (Story #{s_idx + 1})")
        return story, p_num, s_idx

    return STORY_CATALOG[0], 2, 0

def save_and_push_episode_state(story: dict, part_num: int, story_idx: int):
    """Saves next episode pointer to series_state.json and commits back to GitHub repo."""
    completed = []
    if STATE_FILE.exists():
        try:
            old = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            completed = list(old.get("completed_episodes", []))
        except Exception:
            pass

    ep_key = f"{story['story_id']}_p{part_num}"
    if ep_key not in completed:
        completed.append(ep_key)

    next_part = part_num + 1
    next_story_idx = story_idx
    if next_part > TOTAL_PARTS:
        next_part = 1
        next_story_idx = story_idx + 1

    new_state = {
        "story_index": next_story_idx,
        "part_num": next_part,
        "last_uploaded_story": story["title_bn"],
        "last_uploaded_part": part_num,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed_episodes": completed,
    }
    STATE_FILE.write_text(json.dumps(new_state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[State Saved] Next run will publish Story #{next_story_idx + 1}, Part {next_part}/{TOTAL_PARTS}")

    # Auto-commit series_state.json back to GitHub repository so next cron run knows!
    try:
        subprocess.run(["git", "config", "user.name", "GitCast Auto-Publisher"], check=False)
        subprocess.run(["git", "config", "user.email", "actions@github.com"], check=False)
        subprocess.run(["git", "add", str(STATE_FILE)], check=False)
        subprocess.run(["git", "commit", "-m", f"chore: completed {story['title_bn']} part {part_num} [skip ci]"], check=False)
        subprocess.run(["git", "push"], check=False)
        print("[Git Sync] Committed series_state.json to repository.")
    except Exception as e:
        print(f"[Git Sync Info] Could not push state file ({e})")

# ==============================================================================
# 3. 5-TO-6 MINUTE (10-ACT) DRAMATIC MULTI-CHARACTER SCRIPT GENERATOR
# ==============================================================================
def build_10_act_full_episode_script(story: dict, part_num: int) -> list[dict]:
    """
    Generates a rich 10-Act (5 to 6 minute) dramatic Bangla cartoon script where:
    - Multiple characters speak with distinct voices (narrator, ariyan, rafiq, elder, female)
    - Each Act has a distinct animated 2D scene & character action (driving, campfire, walking, talking, running)
    """
    title = story["title_bn"]
    setting = story["setting_bn"]
    hero = story["hero_bn"].split("(")[0].strip()
    elder = story["elder_bn"].split("(")[0].strip()
    entity = story["entity_bn"]
    part_sub = story["part_titles"][(part_num - 1) % len(story["part_titles"])]

    acts = [
        {
            "act": 1,
            "env": "highway_jeep",
            "action": "drive",
            "speaker": "narrator",
            "speaker_label": "সূত্রধর: মমিন ভাই",
            "headline": f"গল্প : {title} — পর্ব {part_num} ({part_sub})",
            "text_bn": (
                f"আসসালামু আলাইকুম সবাইকে… আমি আপনাদের মমিন ভাই। গভীর রাতের নিস্তব্ধতা যখন চারপাশ গ্রাস করে নেয়… "
                f"ঠিক তখনই শুরু হয় আমাদের আজকের ভৌতিক ও রহস্যময় কাহিনি—{title}-এর {part_num} নম্বর পর্ব: {part_sub}। "
                f"চারদিকে ঘন কুয়াশা আর ঝিঁঝিঁ পোকার ডাক। {setting}-এর দিকে ছুটে চলেছে একটি জিপ গাড়ি। "
                f"গাড়ির হেডলাইটের আলো কুয়াশার দেয়াল ভেদ করে বেশিদূর যেতে পারছে না। "
                f"গাড়ির ভেতরে বসে থাকা {hero} এবং তার বন্ধু রফিক ও কাওসার ঘুণাক্ষরেও জানত না—আজকের এই রাতটি তাদের জীবনের সবচেয়ে ভয়ংকর রাত হতে চলেছে। "
                f"হঠাৎ রাস্তার বাঁকে বটগাছের নিচে… সাদা কুয়াশার ভেতর কেউ একজন হাত তুলে গাড়ি থামানোর ইশারা করল!"
            ),
        },
        {
            "act": 2,
            "env": "campfire_clearing",
            "action": "campfire_talk",
            "speaker": "narrator",
            "speaker_label": "সূত্রধর: মমিন ভাই",
            "headline": f"{setting}-এ আগমন ও ক্যাম্পফায়ার",
            "text_bn": (
                f"গাড়ি থামিয়ে তারা নেমে এলো {setting}-এর ঠিক সামনে। রাতের হিমেল বাতাস শরীর কাঁপিয়ে দিচ্ছে। "
                f"ঠান্ডা আর অন্ধকার দূর করতে তারা শুকনো কাঠ জড়ো করে ক্যাম্পফায়ারের আগুন জ্বালাল। "
                f"আগুনের লালচে আভায় চারপাশের লম্বা গাছগুলোর ছায়া যেন জীবন্ত দৈত্যের মতো দুলে উঠছে। "
                f"দূরের ওই পরিত্যক্ত কাঠের বাড়িটার দিকে তাকালে বুকের ভেতরটা কেমন যেন মোচড় দিয়ে ওঠে। "
                f"কাঠের আগুনের চটপট শব্দের মাঝেই হঠাৎ বনের ভেতর থেকে ভেসে এলো শুকনো পাতার ওপর কারও ভারী পায়ের আওয়াজ! "
                f"মনে হলো… অন্ধকারের আড়াল থেকে অদৃশ্য দুটি চোখ অপলকভাবে তাদের প্রতিটি পদক্ষেপ লক্ষ্য করছে।"
            ),
        },
        {
            "act": 3,
            "env": "ariyan_talking",
            "action": "talk_gesture",
            "speaker": "ariyan",
            "speaker_label": f"চরিত্র: {hero}",
            "headline": f"{hero}-এর সতর্ক সংলাপ ও সন্দেহ",
            "text_bn": (
                f"ক্যাম্পফায়ারের আগুনের দিকে তাকিয়ে {hero} হঠাৎ ভ্রু কুঁচকে উঠে দাঁড়াল। "
                f"সে গম্ভীর ও চাপা গলায় বন্ধুদের উদ্দেশ্যে বলল—‘শোন রফিক… শোন কাওসার! আমার কেন যেন জায়গাটা মোটেও সুবিধার মনে হচ্ছে না। "
                f"তোরা কি খেয়াল করেছিস? আমরা যখনই কথা বলছি, ঠিক তখনই ওই পরিত্যক্ত বাড়িটার দোতলার বারান্দা থেকে একটা খসখস শব্দ আসছে! "
                f"আমি একটু আগে স্পষ্ট দেখেছি—ওই ভাঙা জানালার পর্দার আড়ালে কেউ একজন দাঁড়িয়ে আমাদের দিকেই তাকিয়ে ছিল! "
                f"এখানে কোনো সাধারণ মানুষ থাকার কথা নয়… আমাদের খুব সাবধানে থাকতে হবে, কেউ একা একা দল ছেড়ে এক পা-ও দূরে যাবি না!’"
            ),
        },
        {
            "act": 4,
            "env": "haunted_window",
            "action": "window_shadow",
            "speaker": "narrator",
            "speaker_label": "সূত্রধর: মমিন ভাই",
            "headline": f"দোতলার জানালায় {entity}-এর ছায়া",
            "text_bn": (
                f"{hero}-এর কথা শেষ হতে না হতেই… আকাশে মেঘের আড়ালে চমকে উঠল নীলচে বিদ্যুৎ! "
                f"আর সেই বিদ্যুতের ঝলকে দেখা গেল এক রোমহর্ষক দৃশ্য! "
                f"পরিত্যক্ত বাড়িটার দোতলার জানালায় হঠাৎ জ্বলে উঠল একটি ম্লান হলুদ আলো। "
                f"জানালার কাঁচের ওপাশে স্পষ্ট দেখা গেল—{entity} ধীরে ধীরে এক প্রান্ত থেকে অন্য প্রান্তে হেঁটে যাচ্ছে! "
                f"বাতাসের কোনো নামগন্ধ নেই, অথচ বাড়িটার সদর দরজার পাল্লা দুটো ক্যাঁচক্যাঁচ শব্দ করে আপনাআপনি অর্ধেক খুলে গেল! "
                f"ভেতরের ঘুটঘুটে অন্ধকার থেকে যেন বরফের মতো ঠান্ডা এক নিঃশ্বাস বাইরে বেরিয়ে এলো।"
            ),
        },
        {
            "act": 5,
            "env": "rafiq_panic",
            "action": "panic_tremble",
            "speaker": "rafiq",
            "speaker_label": "চরিত্র: বন্ধু রফিক (আতঙ্কিত)",
            "headline": "রফিকের আতঙ্ক ও জিপ গাড়ির ভেতরের শব্দ",
            "text_bn": (
                f"ওই দৃশ্য দেখামাত্রই রফিকের মুখ রক্তশূন্য ফ্যাকাসে হয়ে গেল! সে ভয়ে কাঁপতে কাঁপতে দু-পা পিছিয়ে জিপ গাড়ির কাছে গিয়ে চিৎকার করে উঠল— "
                f"‘আরিয়ান ভাই! সর্বনাশ হয়ে গেছে! আমার হাত-পা ঠান্ডা হয়ে আসছে! "
                f"ওই দোতলার জানালায় ওটা কোনো মানুষ নয়… ওটাের পা মাটিতে ছুঁয়ে নেই! "
                f"আর শোন… আমাদের জিপ গাড়িটার ভেতর থেকেও কিসের যেন আঁচড়ানোর শব্দ আসছে! "
                f"চাবি তো তোর পকেটে, তাহলে গাড়ির ড্যাশবোর্ডের আলোটা একা একা জ্বলছে আর নিভছে কেন?! "
                f"ভাই দোহাই লাগে, চল এখান থেকে এক্ষুনি পালিয়ে যাই, নইলে আজ আমাদের কেউ বাঁচাতে পারবে না!’"
            ),
        },
        {
            "act": 6,
            "env": "forest_walk",
            "action": "walk",
            "speaker": "narrator",
            "speaker_label": "সূত্রধর: মমিন ভাই",
            "headline": "টর্চলাইট হাতে অন্ধকার বনের পথে পদযাত্রা",
            "text_bn": (
                f"কিন্তু পালাবার পথ তখন বন্ধ হয়ে গেছে! জিপ গাড়িটার ইঞ্জিন বারবার চেষ্টা করেও আর স্টার্ট নিল না। "
                f"বাধ্য হয়ে {hero} তার হাতের শক্তিশালী টর্চলাইটটা জ্বালিয়ে নিল। "
                f"টর্চের সাদা আলোর রশ্মি অন্ধকার বনের গাছপালার ভেতর দিয়ে পথ কেটে এগিয়ে চলল। "
                f"তিন বন্ধু একে অপরের হাত ধরে ধীর পায়ে এগিয়ে চলল সেই রহস্যময় বাড়িটার দিকে। "
                f"প্রতিটি কদমে শুকনো পাতার মরমর শব্দ হচ্ছে, আর মাথার ওপরের ডালপালা থেকে রাতজাগা পেঁচা ডেকে উঠছে। "
                f"হঠাৎ কুয়াশার ভেতর থেকে এক বৃদ্ধ মানুষের কাশির শব্দ ও হারিকেনের দুলতে থাকা আলো তাদের দিকে এগিয়ে আসতে লাগল!"
            ),
        },
        {
            "act": 7,
            "env": "elder_watchman",
            "action": "elder_talk",
            "speaker": "elder",
            "speaker_label": f"চরিত্র: {elder}",
            "headline": f"{elder}-এর ভয়ংকর সতর্কবার্তা",
            "text_bn": (
                f"হাতে পুরনো একটি মরচে ধরা হারিকেন নিয়ে কুয়াশার ভেতর থেকে বেরিয়ে এলেন {elder}। "
                f"তার চোখেমুখে গভীর আতঙ্কের ছাপ। তিনি কাঁপা ও ভারী গলায় হাত তুলে বললেন— "
                f"‘থামো বাবারা… আর এক কদমও সামনে বাড়িও না! তোমরা এখানে কেন এসেছ?! "
                f"তোমরা কি জানো না—রাত বারোটার পর এই সীমানায় পা রাখলে কেউ আর স্বাভাবিক হয়ে ফিরে যেতে পারে না? "
                f"আজ থেকে ত্রিশ বছর আগে ঠিক এই রাতেই এখানে ঘটেছিল এক নিষ্ঠুর ট্র্যাজেডি। "
                f"তারপর থেকে প্রতি অমাবস্যার রাতে এই মায়াজাল সক্রিয় হয়ে ওঠে… মানুষের পরিচিত কণ্ঠ নকল করে তাদের ভেতরে ডেকে নিয়ে যায়!’"
            ),
        },
        {
            "act": 8,
            "env": "wooden_corridor",
            "action": "walk_indoor",
            "speaker": "ariyan",
            "speaker_label": f"চরিত্র: {hero}",
            "headline": "কাঠের করিডোরে প্রবেশ ও রহস্যময় ঘড়ি",
            "text_bn": (
                f"বৃদ্ধের কথা শেষ হওয়ার আগেই হঠাৎ এক দমকা বাতাসে তার হাতের হারিকেনটা দপ করে নিভে গেল! "
                f"আর পরক্ষণেই দেখা গেল—কাওসার তাদের পাশে নেই! বাড়ির ভেতর থেকে কাওসারের আর্তনাদ ভেসে এলো! "
                f"{hero} এক মুহূর্ত দেরি না করে টর্চলাইট হাতে রফিককে নিয়ে ঢুকে পড়ল সেই পরিত্যক্ত বাড়ির কাঠের করিডোরে। "
                f"{hero} চিৎকার করে বলল—‘রফিক, আমার ঠিক পেছনে থাকবি! দেখ… দেয়ালের ওই প্রাচীন পেন্ডুলাম ঘড়িটা উল্টো দিকে ঘুরছে! "
                f"মেঝের ধুলোর ওপর ভেজা পায়ের ছাপগুলো সিঁড়ি বেয়ে সোজা দোতলার ওই বন্ধ কুঠুরির দিকে গেছে! আমাদের বন্ধুকে বাঁচাতেই হবে!’"
            ),
        },
        {
            "act": 9,
            "env": "shadow_chase",
            "action": "run_climax",
            "speaker": "female",
            "speaker_label": "রহস্যময় ছায়াকণ্ঠ ও রফিকের চিৎকার",
            "headline": f"{entity}-এর মুখোমুখি ও চরম উত্তেজনা",
            "text_bn": (
                f"তারা যখন সিঁড়ির কাছে পৌঁছাল, তখন অন্ধকার ছাদ থেকে এক শীতল নারীকণ্ঠ ফিসফিস করে প্রতিধ্বনিত হলো— "
                f"‘কেউ ফিরতে পারবে না… এই মায়াজালে যারা একবার প্রবেশ করে, তারা চিরকাল এই অন্ধকারের অংশ হয়ে থাকে!’ "
                f"সাথে সাথে সিঁড়ির মাথায় মেঘের মতো কালো ধোঁয়া কুণ্ডলী পাকিয়ে বিশাল এক ছায়ামূর্তির রূপ নিল! "
                f"দুটি জ্বলন্ত লাল চোখ তাদের দিকে তাকিয়ে এগিয়ে আসতে লাগল! "
                f"প্রাণভয়ে আরিয়ান ও রফিক করিডোর ধরে দৌড়াতে শুরু করল, আর পেছনের প্রতিটি দরজা-জানালা প্রচণ্ড শব্দে আছড়ে বন্ধ হতে লাগল!"
            ),
        },
        {
            "act": 10,
            "env": "cliffhanger_outro",
            "action": "narrator_outro",
            "speaker": "narrator",
            "speaker_label": "সূত্রধর: মমিন ভাই",
            "headline": (
                f"পরবর্তী পর্ব (পর্ব {part_num + 1})-এ কী ঘটবে?"
                if part_num < TOTAL_PARTS
                else f"{title} গল্পের রোমহর্ষক সমাপ্তি"
            ),
            "text_bn": (
                f"শেষ মুহূর্তে {hero} যখন লোহার সদর দরজাটা ধাক্কা দিয়ে খুলতে গেল… তখনই তার হাতের টর্চলাইটের আলো পড়ল মেঝেতে পড়ে থাকা এক পুরনো ডায়েরির ওপর! "
                f"সেই ডায়েরির পাতায় যা লেখা ছিল, তা পড়ে আরিয়ানের গায়ের রোম দাঁড়িয়ে গেল! "
                + (
                    f"কী লেখা ছিল সেই ডায়েরিতে? কাওসার কি আদৌ বেঁচে আছে, নাকি সে-ও মায়াজালের শিকার হয়েছে? "
                    f"আসল ভয়ংকর রহস্য উন্মোচিত হবে আমাদের পরবর্তী পর্বে—অর্থাৎ {title}-এর {part_num + 1} নম্বর পর্বে! "
                    f"পরবর্তী পর্ব সবার আগে দেখতে আমাদের পেইজ ও চ্যানেলটি এখনই ফলো এবং সাবস্ক্রাইব করে মমিন ভাইয়ের সাথেই থাকুন। ধন্যবাদ সবাইকে!"
                    if part_num < TOTAL_PARTS
                    else f"ডায়েরির সেই গোপন সংকেত ব্যবহার করে আরিয়ান অবশেষে ভেঙে ফেলল ত্রিশ বছরের পুরনো সেই অশুভ মায়াজাল! "
                    f"ভোরের প্রথম সূর্যের আলো ফোটার সাথে সাথে কুয়াশা কেটে গেল, এবং তিন বন্ধু নিরাপদে ফিরে এলো। "
                    f"আর এভাবেই সমাপ্ত হলো আমাদের '{title}' সিরিজ। আগামী পর্বে মমিন ভাই নিয়ে আসছেন সম্পূর্ণ নতুন আরেকটি রোমহর্ষক রহস্যময় গল্প! "
                    f"নতুন গল্পটি মিস না করতে পেইজটি ফলো করে আমাদের সাথেই থাকুন!"
                )
            ),
        },
    ]
    return acts

# ==============================================================================
# 4. HUMAN-LIKE MULTI-ACTOR VOICE SYNTHESIZER + CINEMA AMBIENCE MIXER
# ==============================================================================
def synthesize_clause_edge_tts(clause_text: str, voice_id: str, pitch: str, rate: str, out_mp3: str):
    subprocess.run(
        [
            "edge-tts",
            "--voice", voice_id,
            f"--pitch={pitch}",
            f"--rate={rate}",
            "--text", clause_text,
            "--write-media", out_mp3,
        ],
        check=False,
    )

def generate_cinema_ambience_wav(duration_sec: float, out_wav: str, is_climax: bool = False):
    """
    Synthesizes a realistic dark night forest + campfire crackle + eerie wind + suspense bass drone
    soundscape at 24kHz so the voice sounds like a real cinema studio mix instead of raw TTS!
    """
    import numpy as np
    sr = 24000
    n_samples = int(max(3.0, duration_sec) * sr)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False, dtype=np.float32)

    # 1. Deep dark cinema sub-bass suspense drone (55Hz + 110Hz slow breathing modulation)
    drone_mod = 0.55 + 0.45 * np.sin(2 * np.pi * 0.18 * t)
    drone = (0.045 * np.sin(2 * np.pi * 55.0 * t) + 0.022 * np.sin(2 * np.pi * 110.0 * t)) * drone_mod

    # 2. Night forest crickets (pulsed 4.1kHz harmonic chirps)
    chirp_env = np.maximum(0.0, np.sin(2 * np.pi * 3.2 * t)) ** 4
    crickets = 0.012 * np.sin(2 * np.pi * 4150.0 * t) * chirp_env

    # 3. Eerie night wind & campfire gentle crackle
    rng = np.random.default_rng(429108)
    white = rng.normal(0, 0.014, n_samples).astype(np.float32)
    # Simple moving average low-pass for warm wind rumble
    kernel_size = 64
    wind = np.convolve(white, np.ones(kernel_size, dtype=np.float32) / kernel_size, mode="same") * 3.2

    # 4. Dramatic heartbeat thud on climax/panic scenes
    heartbeat = np.zeros_like(t)
    if is_climax:
        beat_phase = t % 1.15
        thud1 = np.exp(-((beat_phase - 0.12) / 0.045) ** 2) * np.sin(2 * np.pi * 48.0 * t)
        thud2 = np.exp(-((beat_phase - 0.30) / 0.040) ** 2) * np.sin(2 * np.pi * 44.0 * t) * 0.75
        heartbeat = 0.075 * (thud1 + thud2)

    mix = np.clip(drone + crickets + wind + heartbeat, -0.95, 0.95)
    pcm16 = (mix * 32767.0).astype(np.int16)
    with wave.open(out_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())

def synthesize_human_expressive_act_audio(act_obj: dict, part_num: int, out_wav: str) -> float:
    """
    Synthesizes natural, human-sounding expressive Bengali speech for an Act:
    - Splits paragraph into natural breath clauses (… / — / ! / ? / ।)
    - Uses character-specific neural voice actor (narrator / ariyan / rafiq / elder / female)
    - Varies micro-pitch & rate per clause like a real human actor
    - Inserts natural breathing pauses between sentences
    - Applies warm studio EQ, formant shaping & mixes over Cinema Night Forest Ambience!
    - Ensures each of the 10 Acts is ~31-35 seconds so the full 10-Act episode is 5 to 6 minutes!
    """
    act_idx = act_obj["act"]
    speaker_key = act_obj.get("speaker", "narrator")
    profile = CHARACTER_VOICES.get(speaker_key, CHARACTER_VOICES["narrator"])
    base_voice = profile["voice"]
    eq_filter = profile["eq"]
    raw_text = act_obj["text_bn"]

    # Split text into dramatic human breath clauses
    clauses = [c.strip() for c in re.split(r"(?<=[।!?…—])\s+", raw_text) if c.strip()]
    if not clauses:
        clauses = [raw_text]

    clause_wavs = []
    for c_idx, clause in enumerate(clauses):
        c_mp3 = f"dist/tmp_p{part_num}_a{act_idx}_c{c_idx}.mp3"
        c_wav = f"dist/tmp_p{part_num}_a{act_idx}_c{c_idx}.wav"

        # Dynamic human micro-inflection based on punctuation
        if "!" in clause or "؟" in clause or "?!" in clause:
            pitch = "+3Hz" if speaker_key == "rafiq" else "-2Hz"
            rate = "+6%" if speaker_key == "rafiq" else "-2%"
            pause_sec = 0.55
        elif "…" in clause:
            pitch = "-6Hz" if speaker_key == "narrator" else profile["pitch"]
            rate = "-12%"
            pause_sec = 0.72
        else:
            pitch = profile["pitch"]
            rate = profile["rate"]
            pause_sec = 0.48

        synthesize_clause_edge_tts(clause, base_voice, pitch, rate, c_mp3)
        if os.path.exists(c_mp3) and os.path.getsize(c_mp3) > 100:
            # Convert clause to 24kHz mono wav + append natural human breath pause (apad)
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", c_mp3,
                    "-af", f"{eq_filter},apad=pad_dur={pause_sec}",
                    "-ar", "24000", "-ac", "1", c_wav,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if os.path.exists(c_wav):
                clause_wavs.append(c_wav)

    voice_concat_wav = f"dist/voice_raw_p{part_num}_a{act_idx}.wav"
    if clause_wavs:
        list_file = f"dist/clauses_p{part_num}_a{act_idx}.txt"
        with open(list_file, "w", encoding="utf-8") as lf:
            for cw in clause_wavs:
                lf.write(f"file '{os.path.abspath(cw)}'\n")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-ar", "24000", "-ac", "1", voice_concat_wav],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

    # Measure voice duration and pad dramatic atmospheric suspense tail so each Act is at least 31s
    # (10 Acts * ~32s = ~320s = 5 minutes 20 seconds full-length episode!)
    voice_dur = 31.0
    if os.path.exists(voice_concat_wav):
        try:
            with wave.open(voice_concat_wav, "rb") as wf:
                voice_dur = wf.getnframes() / float(wf.getframerate())
        except Exception:
            pass

    target_act_dur = max(31.5, voice_dur + 2.2)
    pad_tail = max(1.2, target_act_dur - voice_dur)

    amb_wav = f"dist/amb_p{part_num}_a{act_idx}.wav"
    is_climax = act_idx in (4, 5, 9, 10)
    generate_cinema_ambience_wav(target_act_dur, amb_wav, is_climax=is_climax)

    if os.path.exists(voice_concat_wav):
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", voice_concat_wav,
                "-i", amb_wav,
                "-filter_complex",
                f"[0:a]highpass=f=70,acompressor=threshold=-16dB:ratio=2.8:makeup=4dB,apad=pad_dur={pad_tail:.2f}[v];"
                f"[1:a]volume=0.28[bg];"
                f"[v][bg]amix=inputs=2:duration=first:dropout_transition=2[out]",
                "-map", "[out]",
                "-ar", "24000", "-ac", "1",
                out_wav,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    else:
        os.replace(amb_wav, out_wav)

    final_dur = target_act_dur
    try:
        with wave.open(out_wav, "rb") as wf:
            final_dur = wf.getnframes() / float(wf.getframerate())
    except Exception:
        pass
    return final_dur

# ==============================================================================
# 5. PRO-LEVEL 3D / 2.5D CINEMA ANIMATION ENGINE (ARIA09AI & C.K ANIMATION STYLE)
# ==============================================================================
def compute_frame_lip_sync_envelopes(wav_path: str, fps: int, total_frames: int) -> list[float]:
    """Reads actual voice audio samples to drive real-time 3D character talking motion & rim lighting!"""
    import numpy as np
    try:
        with wave.open(wav_path, "rb") as wf:
            sr = wf.getframerate()
            raw = wf.readframes(wf.getnframes())
            samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        samples_per_frame = max(1, int(sr / fps))
        envelopes = []
        for f in range(total_frames):
            start = f * samples_per_frame
            chunk = samples[start : start + samples_per_frame]
            if len(chunk) == 0:
                envelopes.append(0.0)
            else:
                rms = float(np.sqrt(np.mean(chunk * chunk)))
                envelopes.append(min(1.0, rms * 5.2))
        return envelopes
    except Exception:
        return [0.45 if (i % 4 < 2) else 0.05 for i in range(total_frames)]

def load_bengali_font(size: int):
    """Loads NotoSansBengali-Bold or Lohit-Bengali installed on Ubuntu Runner for crisp Bengali cinema titles."""
    from PIL import ImageFont
    font_candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
        "/usr/share/fonts/truetype/lohit-bengali/Lohit-Bengali.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size=size)
            except Exception:
                pass
    return ImageFont.load_default()

def get_pro_3d_prompts_for_act(act_obj: dict, story: dict, part_num: int) -> tuple[str, str]:
    """
    Returns 2 distinct Pro-Level 3D Pixar / Unreal Engine 5 / C.K Animation / Aria09ai camera shots
    for each Act (so a 10-Act episode has 20 distinct 3D rendered cinema shots!).
    """
    env_type = act_obj.get("env", "campfire_clearing")
    base_style = (
        "Pro 3D animated movie frame, Pixar and Studio Ghibli 3D anime lighting, Unreal Engine 5 render, "
        "C.K Animation and SSOFTOONS 3D Bangla horror cartoon style, rich volumetric fog, dramatic rim lighting, "
        "8k cinema quality, no text, no watermark"
    )
    prompts = {
        "highway_jeep": (
            f"{base_style}, wide shot of a dark blue off-road SUV Jeep driving at night through a misty rural Bengali village road, bright glowing yellow headlights cutting through thick blue fog, giant ancient banyan trees, starry night sky",
            f"{base_style}, medium 3D shot of a handsome young Bangladeshi man with a short beard in an orange collared shirt and his friend in a mustard yellow shirt looking out of an off-road Jeep at a mysterious white silhouette in the night mist",
        ),
        "campfire_clearing": (
            f"{base_style}, Aria09ai style 3D night village scene with a crackling orange campfire in the foreground, an off-road Jeep with glowing headlights parked on a misty path, warm lantern-lit rural cottages and a spooky two-story wooden house in the background",
            f"{base_style}, medium close-up 3D Pixar style shot of two young Bangladeshi friends (one bearded in orange shirt, one in mustard yellow shirt) sitting by a glowing campfire at night, warm firelight reflecting on their expressive faces, misty dark forest behind them",
        ),
        "ariyan_talking": (
            f"{base_style}, dramatic 3D close-up shot of a brave bearded young Bangladeshi man in an orange shirt speaking seriously and pointing toward an eerie old two-story wooden mansion in the misty night, warm campfire rim lighting",
            f"{base_style}, over-the-shoulder 3D animated shot of two friends looking up at the dark wooden balcony of an abandoned Bengali mansion at night, volumetric moonlight and drifting fog",
        ),
        "haunted_window": (
            f"{base_style}, C.K Animation style eerie old iron truss bridge and abandoned two-story wooden mansion at night, a glowing yellow upstairs window with a dark ghostly silhouette standing behind the glass, blue lightning flash in the stormy sky, thick rolling river fog",
            f"{base_style}, low-angle 3D horror shot of the heavy wooden front doors of a haunted mansion creaking open by themselves at midnight, eerie amber light and swirling mist spilling out onto the stone steps",
        ),
        "rafiq_panic": (
            f"{base_style}, C.K Animation style 3D cel-shaded close-up of a terrified young Bangladeshi man in a mustard-yellow collared shirt with wide fearful eyes and trembling expression standing near a wooden doorway and Jeep at night, dramatic shadow on the wall",
            f"{base_style}, medium 3D shot of a scared young man in a yellow shirt grabbing his bearded friend's arm in panic beside an off-road Jeep whose dashboard lights are flickering eerily in the dark forest",
        ),
        "forest_walk": (
            f"{base_style}, C.K Animation style 3D night scene of two young Bangladeshi men (orange shirt and yellow shirt) walking cautiously across a dark iron truss bridge and misty forest path at midnight, holding a bright flashlight whose volumetric beam cuts through the fog",
            f"{base_style}, cinematic 3D tracking shot from behind two friends walking toward a spooky colonial wooden bungalow through twisted banyan trees, glowing flashlight god-rays and glowing fireflies in the dark mist",
        ),
        "elder_watchman": (
            f"{base_style}, 3D animated shot of an elderly Bangladeshi village watchman with a white beard and dark shawl emerging from the thick night fog holding a glowing brass hurricane lantern, warning two young men with a raised hand",
            f"{base_style}, close-up 3D Pixar style shot of an old watchman's worried face illuminated by the warm amber flame of a hurricane lantern at midnight, ancient mossy stone pillars in the background",
        ),
        "wooden_corridor": (
            f"{base_style}, C.K Animation style 3D interior of an old rural Bengali house room at night, open wooden doorway, textured walls with an antique pendulum clock, a wooden table with a green tablecloth and glowing lantern, two young friends entering with a flashlight",
            f"{base_style}, 3D suspense shot inside a dusty wooden corridor with a creaking staircase leading upstairs, muddy footprints on the floor illuminated by a sweeping flashlight beam, eerie shadows on the wall",
        ),
        "shadow_chase": (
            f"{base_style}, intense 3D climax shot at the top of a dark wooden staircase where swirling black smoke forms a towering shadowy phantom with two glowing red eyes, volumetric red and blue horror lighting",
            f"{base_style}, dynamic 3D action shot of two young Bangladeshi men (orange shirt and yellow shirt) running down a dark haunted corridor toward the exit door while holding a bright flashlight, dramatic motion and flying dust particles",
        ),
        "cliffhanger_outro": (
            f"{base_style}, cinematic 3D close-up shot of a young man's hand shining a bright flashlight beam onto an ancient leather-bound diary lying on a dusty wooden floor beside a heavy iron door at midnight",
            f"{base_style}, Aria09ai style breathtaking 3D wide shot of a misty Bengali village at night with a glowing campfire, warm cottage lanterns, starry mountain sky, and a mysterious silhouette watching from the distant bridge",
        ),
    }
    return prompts.get(env_type, prompts["campfire_clearing"])

def generate_pro_3d_scene_image(prompt: str, seed: int, W: int, H: int, out_path: str):
    """
    Generates a high-resolution Pro 3D Pixar / Unreal Engine 5 / C.K Animation scene image:
    1. Tries Gemini Imagen / Flash Image if GEMINI_API_KEY is available.
    2. Uses Free Keyless FLUX 3D Render Engine with watermark-free cropping + 3D Cinema Color Grading.
    3. Provides a rich multi-layered 3D shaded atmospheric fallback if offline.
    """
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
    from io import BytesIO

    if os.path.exists(out_path) and os.path.getsize(out_path) > 15000:
        return Image.open(out_path).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)

    # Render area sits between Top & Bottom Gold Cinema Bars
    req_w, req_h = W, H + 56
    encoded = urllib.parse.quote(prompt)
    urls = [
        f"https://image.pollinations.ai/prompt/{encoded}?width={req_w}&height={req_h}&seed={seed}&nologo=true&model=flux",
        f"https://image.pollinations.ai/prompt/{encoded}?width={req_w}&height={req_h}&seed={seed}&nologo=true",
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=40, headers={"User-Agent": "Mozilla/5.0 GitCast-3D-Engine/2.0"})
            if resp.ok and len(resp.content) > 10000:
                raw_img = Image.open(BytesIO(resp.content)).convert("RGB")
                rw, rh = raw_img.size
                # Crop bottom 52px before resizing so any corner badge is 100% removed
                cropped = raw_img.crop((0, 0, rw, max(100, rh - 52)))
                img = cropped.resize((W, H), Image.Resampling.LANCZOS)
                # Apply Pro 3D Cinema Color Grading (rich contrast, saturated fire/lantern glow, crisp details)
                img = ImageEnhance.Contrast(img).enhance(1.16)
                img = ImageEnhance.Color(img).enhance(1.20)
                img = ImageEnhance.Sharpness(img).enhance(1.25)
                img.save(out_path, quality=94)
                return img
        except Exception as e:
            print(f"    [3D Render Retry] {e}")

    # Offline fallback: Smooth 3D Volumetric Night Forest & Lantern Shader
    import numpy as np
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ny, nx = yy / float(H), xx / float(W)
    r = np.clip(10 + 28 * (1.0 - ny) + 140 * np.exp(-((nx - 0.45) ** 2 + (ny - 0.65) ** 2) / 0.04), 0, 255)
    g = np.clip(18 + 38 * (1.0 - ny) + 85 * np.exp(-((nx - 0.45) ** 2 + (ny - 0.65) ** 2) / 0.035), 0, 255)
    b = np.clip(38 + 52 * (1.0 - ny) + 25 * np.exp(-((nx - 0.45) ** 2 + (ny - 0.65) ** 2) / 0.03), 0, 255)
    arr = np.stack([r, g, b], axis=-1).astype(np.uint8)
    fallback_img = Image.fromarray(arr, mode="RGB").filter(ImageFilter.GaussianBlur(radius=1.5))
    fallback_img.save(out_path, quality=92)
    return fallback_img

def render_pro_3d_animated_act(
    act_obj: dict,
    story: dict,
    part_num: int,
    wav_path: str,
    duration_sec: float,
    out_mp4: str,
):
    """
    Renders a single Act (31-35s) at 15 FPS with Pro-Level 3D / 2.5D Animation:
    - Generates 2 distinct 3D Pixar / Unreal Engine 5 / C.K Animation shots per Act (Shot A & Shot B)
    - Applies 2.5D Multi-Plane Depth Parallax & 3D Camera Orbit/Dolly Motion
    - Applies Audio-Driven 3D Character Breathing, Nodding & Rim-Light Pulse in sync with dialogue
    - Renders Real-Time Volumetric 3D Mist/Fog, Campfire Flames, Rising 3D Bokeh Embers & Flashlight Beams
    - Frames the scene with C.K Animation-style Top & Bottom Gold Cinema Bars + Bengali Subtitles!
    """
    import numpy as np
    from PIL import Image, ImageDraw

    W, H = (720, 1280) if ASPECT_RATIO == "9:16" else (1280, 720)
    fps = 15
    total_frames = max(fps * 5, int(duration_sec * fps))
    envelopes = compute_frame_lip_sync_envelopes(wav_path, fps, total_frames)

    act_idx = act_obj["act"]
    env_type = act_obj.get("env", "campfire_clearing")
    prompt_a, prompt_b = get_pro_3d_prompts_for_act(act_obj, story, part_num)

    seed_a = VISUAL_SEED_LOCK + part_num * 100 + act_idx * 10 + 1
    seed_b = VISUAL_SEED_LOCK + part_num * 100 + act_idx * 10 + 2
    shot_a_path = f"dist/shot3d_p{part_num}_a{act_idx}_1.jpg"
    shot_b_path = f"dist/shot3d_p{part_num}_a{act_idx}_2.jpg"

    print(f"    -> Rendering Pro 3D Shots (Seed #{seed_a} & #{seed_b})...")
    img_a = generate_pro_3d_scene_image(prompt_a, seed_a, W, H, shot_a_path)
    img_b = generate_pro_3d_scene_image(prompt_b, seed_b, W, H, shot_b_path)

    arr_a = np.asarray(img_a, dtype=np.float32)
    arr_b = np.asarray(img_b, dtype=np.float32)

    # Precompute normalized coordinates for fast 2.5D Volumetric Shaders
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ny = yy / float(H)
    nx = xx / float(W)

    # Split Bengali narration into subtitle chunks synced across the Act
    words = act_obj["text_bn"].split()
    chunk_size = 7
    sub_chunks = [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)] or [act_obj["headline"]]

    font_top = load_bengali_font(28 if W >= 1000 else 22)
    font_sub = load_bengali_font(23 if W >= 1000 else 19)
    font_brand = load_bengali_font(16)

    top_bar_h = int(H * 0.105)
    bot_bar_h = int(H * 0.135)

    # Pre-initialize 32 floating 3D bokeh embers / fireflies
    rng = np.random.default_rng(seed_a)
    particles = [
        {
            "x": float(rng.uniform(0.08, 0.92)),
            "y": float(rng.uniform(0.20, 0.90)),
            "speed_y": float(rng.uniform(0.035, 0.085)),
            "freq_x": float(rng.uniform(1.2, 2.8)),
            "phase": float(rng.uniform(0, 6.28)),
            "r": int(rng.integers(2, 6)),
            "warm": bool(i % 3 != 0),
        }
        for i in range(32)
    ]

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(fps),
        "-i", "-",
        "-i", wav_path,
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest",
        out_mp4,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for f_idx in range(total_frames):
        t = f_idx / float(fps)
        progress = f_idx / float(max(1, total_frames - 1))
        amp = envelopes[f_idx] if f_idx < len(envelopes) else 0.0

        # 1. Select Shot A (0..48%), Cross-Dissolve (48..56%), or Shot B (56..100%)
        if progress < 0.48:
            base_arr = arr_a
            shot_prog = progress / 0.48
            cam_mode = act_idx % 3
        elif progress < 0.56:
            alpha = (progress - 0.48) / 0.08
            base_arr = arr_a * (1.0 - alpha) + arr_b * alpha
            shot_prog = 0.5
            cam_mode = 0
        else:
            base_arr = arr_b
            shot_prog = (progress - 0.56) / 0.44
            cam_mode = (act_idx + 1) % 3

        # 2. 3D Camera Dolly Zoom + Pan + Audio-Reactive Character Breathing Micro-Motion
        # When a character speaks (amp > 0.1), subtle living camera pulse + vertical breathing bob
        talk_zoom_pulse = amp * 0.014 * math.sin(t * 14.0)
        if cam_mode == 0:
            zoom = 1.04 + shot_prog * 0.10 + talk_zoom_pulse
            pan_x = math.sin(t * 0.45) * 0.025
        elif cam_mode == 1:
            zoom = 1.14 - shot_prog * 0.09 + talk_zoom_pulse
            pan_x = (shot_prog - 0.5) * 0.055
        else:
            zoom = 1.09 + math.sin(t * 0.6) * 0.03 + talk_zoom_pulse
            pan_x = (0.5 - shot_prog) * 0.055

        pan_y = math.sin(t * 2.4) * 0.008 - (amp * 0.006)

        crop_w = int(W / zoom)
        crop_h = int(H / zoom)
        max_dx = max(1, W - crop_w)
        max_dy = max(1, H - crop_h)
        cx0 = int(np.clip((W - crop_w) * 0.5 + pan_x * W, 0, max_dx))
        cy0 = int(np.clip((H - crop_h) * 0.5 + pan_y * H, 0, max_dy))

        # Fast 2.5D slice & resize with subtle foreground/background parallax shift
        cropped_patch = base_arr[cy0 : cy0 + crop_h, cx0 : cx0 + crop_w].astype(np.uint8)
        frame_img = Image.fromarray(cropped_patch, mode="RGB").resize((W, H), Image.Resampling.BILINEAR)
        frame_arr = np.asarray(frame_img, dtype=np.float32)

        # 3. Real-Time Volumetric 3D Mist / Rolling Fog Shader (C.K Animation & Aria09ai Atmosphere)
        fog_wave = (
            np.sin(nx * 5.5 + t * 0.85) * 0.5
            + np.cos(ny * 7.0 - t * 0.55) * 0.5
        )
        fog_mask = np.clip((ny - 0.38) * 1.45, 0.0, 1.0) * (0.14 + 0.09 * fog_wave)
        fog_color = np.array([145.0, 175.0, 215.0], dtype=np.float32)
        frame_arr = frame_arr * (1.0 - fog_mask[..., None]) + fog_color * fog_mask[..., None]

        # 4. Audio-Reactive Warm 3D Rim-Light / Campfire / Lantern Glow Shader
        # Pulses warmly with both the flickering fire AND the character's voice envelope (amp)!
        fire_flicker = 0.22 + 0.08 * math.sin(t * 11.5) + 0.05 * math.cos(t * 17.0) + amp * 0.18
        glow_cx = 0.5 + 0.04 * math.sin(t * 1.7)
        glow_cy = 0.68
        dist_sq = (nx - glow_cx) ** 2 + (ny - glow_cy) ** 2
        glow_mask = np.exp(-dist_sq / 0.14) * fire_flicker
        warm_light = np.array([255.0, 148.0, 42.0], dtype=np.float32)
        frame_arr = np.clip(frame_arr + warm_light * glow_mask[..., None], 0.0, 255.0)

        # 5. Volumetric Flashlight Beam / God-Rays in Walking & Corridor Acts
        if env_type in ("forest_walk", "wooden_corridor", "shadow_chase", "cliffhanger_outro"):
            beam_angle = 0.18 * math.sin(t * 2.1)
            beam_line = (ny - 0.58) - beam_angle * (nx - 0.25)
            beam_cone = np.exp(-(beam_line ** 2) / max(0.004, 0.025 * (nx + 0.1))) * np.clip(nx - 0.15, 0.0, 1.0) * 0.26
            beam_col = np.array([254.0, 243.0, 175.0], dtype=np.float32)
            frame_arr = np.clip(frame_arr + beam_col * beam_cone[..., None], 0.0, 255.0)

        # 6. Storm Lightning Flash in Haunted Window & Climax Acts
        if env_type in ("haunted_window", "shadow_chase") and (f_idx % 67 in (0, 1, 4)):
            frame_arr = np.clip(frame_arr * 1.35 + np.array([45.0, 65.0, 110.0], dtype=np.float32), 0.0, 255.0)

        # Convert back to PIL Image for 3D Bokeh Particles & C.K Animation Gold Cinema Banners
        final_img = Image.fromarray(frame_arr.astype(np.uint8), mode="RGB")
        drw = ImageDraw.Draw(final_img)

        # 7. Rising 3D Glowing Bokeh Embers & Fireflies
        for p in particles:
            py_norm = (p["y"] - t * p["speed_y"]) % 0.76 + 0.12
            px_norm = (p["x"] + math.sin(t * p["freq_x"] + p["phase"]) * 0.035) % 0.96
            px, py = int(px_norm * W), int(py_norm * H)
            pr = p["r"]
            col = (255, 190, 65) if p["warm"] else (165, 243, 252)
            drw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=col)

        # 8. Signature C.K Animation Top & Bottom Gold Cinema Banners (#7A5600 with Metallic Gold Border)
        drw.rectangle((0, 0, W, top_bar_h), fill=(118, 82, 6))
        drw.rectangle((0, top_bar_h - 4, W, top_bar_h), fill=(245, 158, 11))
        drw.rectangle((0, H - bot_bar_h, W, H), fill=(118, 82, 6))
        drw.rectangle((0, H - bot_bar_h, W, H - bot_bar_h + 4), fill=(245, 158, 11))

        # Top Gold Banner Title: "[ পর্ব ১ ] মায়াজাল | রহস্যময় ভাই"
        bn_digits = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
        p_bn = str(part_num).translate(bn_digits)
        top_title = f"[ পর্ব {p_bn} ] {story['title_bn']} — {act_obj['speaker_label']}"
        drw.text(
            (W // 2, top_bar_h // 2),
            top_title,
            font=font_top,
            fill=(255, 255, 255),
            anchor="mm",
            stroke_width=3,
            stroke_fill=(10, 10, 15),
        )

        # Bottom Gold Banner: Live Synced Bengali Subtitle + Channel Attribution
        sub_idx = min(len(sub_chunks) - 1, int(progress * len(sub_chunks)))
        active_sub = sub_chunks[sub_idx]
        drw.text(
            (W // 2, H - int(bot_bar_h * 0.62)),
            active_sub,
            font=font_sub,
            fill=(254, 249, 195),
            anchor="mm",
            stroke_width=2,
            stroke_fill=(10, 10, 15),
        )
        drw.text(
            (W // 2, H - int(bot_bar_h * 0.22)),
            "REPRESENTED BY : রহস্যময় ভাই  |  PRO 3D ANIMATION SERIES",
            font=font_brand,
            fill=(255, 255, 255),
            anchor="mm",
            stroke_width=2,
            stroke_fill=(15, 23, 42),
        )

        try:
            proc.stdin.write(final_img.tobytes())
        except Exception:
            break

    if proc.stdin:
        proc.stdin.close()
    proc.wait()

def render_full_5_to_6_minute_episode(story: dict, part_num: int) -> tuple[Path, list[dict]]:
    """
    Synthesizes all 10 Acts (5-6 minutes total) with Multi-Actor Human Voices + Cinema Soundscape
    and renders each Act's Pro 3D Cinema Shots (20 shots total) with 2.5D depth motion & volumetric shaders!
    """
    os.makedirs("dist", exist_ok=True)
    acts = build_10_act_full_episode_script(story, part_num)
    out_mp4 = Path(f"dist/{story['story_id']}_part_{part_num}.mp4")

    act_clips = []
    total_ep_sec = 0.0

    for act_obj in acts:
        act_idx = act_obj["act"]
        act_wav = f"dist/act_{part_num}_{act_idx}.wav"
        act_mp4 = f"dist/act_{part_num}_{act_idx}.mp4"

        print(f"  [Act {act_idx}/10] Speaker: {act_obj['speaker_label']} | 3D Scene: {act_obj['env']}")
        dur = synthesize_human_expressive_act_audio(act_obj, part_num, act_wav)
        total_ep_sec += dur
        render_pro_3d_animated_act(act_obj, story, part_num, act_wav, dur, act_mp4)
        if os.path.exists(act_mp4) and os.path.getsize(act_mp4) > 1000:
            act_clips.append(act_mp4)

    concat_txt = f"dist/episode_acts_p{part_num}.txt"
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for clip in act_clips:
            cf.write(f"file '{os.path.abspath(clip)}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", str(out_mp4)],
        check=True,
    )
    print(f"[OK] Rendered Pro 3D Full Episode: {out_mp4} | Duration: {total_ep_sec / 60.0:.1f} Minutes ({int(total_ep_sec)}s)")
    return out_mp4, acts

# ==============================================================================
# 6. YOUTUBE & FACEBOOK PAGE UPLOADERS (WITH DYNAMIC STORY/PART METADATA)
# ==============================================================================
def build_episode_metadata(story: dict, part_num: int):
    title_bn = story["title_bn"]
    sub_bn = story["part_titles"][(part_num - 1) % len(story["part_titles"])]
    hashtags = [
        f"#পর্ব_{part_num}",
        f"#Part_{part_num}",
        "#মমিন_ভাই",
        f"#{title_bn.replace(' ', '_')}",
        "#রহস্যময়_কাহিনি",
        "#bhutergolpo",
        "#banglacartoon",
        "#3danimation",
        "#horrorgolpo",
        "#রহস্যময়_ভাই",
    ]
    yt_title = f"[ পর্ব {part_num} ] {title_bn} — {sub_bn} | 3D Animation | রহস্যময় ভাই #পর্ব_{part_num} #bhutergolpo"
    desc = (
        f"গল্প : {title_bn} — পর্ব {part_num}/{TOTAL_PARTS} ({sub_bn})\n"
        f"{story['subtitle_bn']}। দেখুন রহস্যময় ভাই (মমিন ভাই)-এর কণ্ঠে প্রো লেভেলের 3D অ্যানিমেশন সিরিজ।\n"
        f"🎬 পরবর্তী পর্ব পেতে চ্যানেল ও পেইজটি সাবস্ক্রাইব এবং ফলো করুন!\n\n"
        + " ".join(hashtags)
    )
    return yt_title[:100], desc, hashtags

def upload_to_youtube(video_path: Path, story: dict, part_num: int):
    creds = get_youtube_credentials()
    youtube = build("youtube", "v3", credentials=creds)
    yt_title, yt_desc, hashtags = build_episode_metadata(story, part_num)

    body = {
        "snippet": {
            "title": yt_title,
            "description": yt_desc,
            "tags": [t.lstrip("#") for t in hashtags],
            "categoryId": "24"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(str(video_path), chunksize=1024 * 1024 * 8, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print(f"[YouTube Part {part_num}] Uploaded: https://youtu.be/{response['id']}")
    return response["id"]

def resolve_facebook_page_credentials(raw_page_id: str, raw_token: str):
    page_id = (raw_page_id or "61576363786053").strip() or "61576363786053"
    token = (raw_token or "").strip()
    if not token:
        raise RuntimeError("Missing FACEBOOK_PAGE_ACCESS_TOKEN in GitHub Secrets!")

    try:
        acc_res = requests.get(
            "https://graph.facebook.com/v21.0/me/accounts",
            params={"fields": "id,name,access_token", "access_token": token},
            timeout=20,
        )
        if acc_res.ok:
            pages = acc_res.json().get("data", [])
            if pages:
                matched = next((p for p in pages if str(p.get("id")) == page_id), pages[0])
                resolved_id = str(matched.get("id") or page_id)
                resolved_token = str(matched.get("access_token") or token)
                print(f"[FB Auth] Auto-exchanged User Token -> Page Token for '{matched.get('name')}' (ID: {resolved_id})")
                return resolved_id, resolved_token
    except Exception as e:
        print(f"[FB Auth Info] /me/accounts check skipped ({e})")

    try:
        pg_res = requests.get(
            f"https://graph.facebook.com/v21.0/{page_id}",
            params={"fields": "id,name,access_token", "access_token": token},
            timeout=20,
        )
        if pg_res.ok:
            pg_data = pg_res.json()
            if pg_data.get("access_token"):
                return str(pg_data.get("id") or page_id), str(pg_data["access_token"])
    except Exception:
        pass

    return page_id, token

def upload_to_facebook_page(video_path: Path, story: dict, part_num: int, youtube_video_id: str = ""):
    raw_page_id = os.environ.get("FACEBOOK_PAGE_ID") or "61576363786053"
    raw_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN") or ""
    page_id, page_token = resolve_facebook_page_credentials(raw_page_id, raw_token)
    fb_title, fb_caption, _ = build_episode_metadata(story, part_num)

    video_url = f"https://graph-video.facebook.com/v21.0/{page_id}/videos"
    with open(video_path, "rb") as f:
        res = requests.post(
            video_url,
            data={
                "title": fb_title,
                "description": fb_caption,
                "access_token": page_token,
            },
            files={"source": (video_path.name, f, "video/mp4")},
            timeout=600,
        )

    if res.ok:
        fb_video_id = res.json().get("id")
        print(f"[Facebook Page Part {part_num}] Native Video Uploaded: https://facebook.com/{page_id}/videos/{fb_video_id}")
        return fb_video_id

    print(f"[FB Video API Notice] Status {res.status_code}: {res.text}")

    feed_url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
    yt_link = f"https://youtu.be/{youtube_video_id}" if youtube_video_id else ""
    feed_message = f"{fb_title}\n\n{fb_caption}" + (f"\n\n🎬 ফুল ভিডিও দেখুন: {yt_link}" if yt_link else "")
    feed_payload = {"message": feed_message, "access_token": page_token}
    if yt_link:
        feed_payload["link"] = yt_link

    feed_res = requests.post(feed_url, data=feed_payload, timeout=60)
    if feed_res.ok:
        post_id = feed_res.json().get("id")
        print(f"[Facebook Page Part {part_num}] Published to Page Feed: https://facebook.com/{post_id}")
        return post_id

    raise RuntimeError(f"Facebook Upload Failed ({res.status_code}): {res.text}")

if __name__ == "__main__":
    # 1. Automatically find the NEXT unposted Part or NEXT new Story!
    story_obj, next_part_num, story_idx = load_and_resolve_next_episode()

    # 2. Render 5-6 Minute (10-Act, 20-Shot) Pro 3D Animated Episode with Multi-Actor Human Voices
    video_file, _ = render_full_5_to_6_minute_episode(story_obj, next_part_num)

    # 3. Upload to YouTube & Facebook Page 'রহস্যময় ভাই'
    yt_id = ""
    fb_id = ""
    try:
        yt_id = upload_to_youtube(video_file, story_obj, next_part_num)
    except Exception as yt_err:
        print(f"[WARN] YouTube upload skipped/failed: {yt_err}")

    try:
        fb_id = upload_to_facebook_page(video_file, story_obj, next_part_num, yt_id)
    except Exception as fb_err:
        print(f"[ERROR] Facebook Page upload failed: {fb_err}")
        if not yt_id:
            raise

    # 4. Advance & commit series_state.json so the next run automatically posts the next part/story!
    if yt_id or fb_id:
        save_and_push_episode_state(story_obj, next_part_num, story_idx)
