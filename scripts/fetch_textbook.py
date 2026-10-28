#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教材下载器 —— 从开源库 TapXWorld/ChinaTextbook 取得教材 PDF。

用法:
  python fetch_textbook.py --subject math --grade 初一 --term 上册 --version 人教版 --out ./textbooks

参数:
  --subject   math | chinese | english  (也接受 数学/语文/英语)
  --grade     初一 / 七年级 / 一年级 / 高一 ...
  --term      上册 | 下册
  --version   人教版 | 部编版 | 外研版 | 北师大版 ...
  --out       输出目录，默认 ./textbooks
  --name      输出文件名（可选，默认自动生成 科目_年级学期_版本.pdf）
  --list      只列出候选，不下载

行为:
  1. 自动判断学段（小学/初中/高中）
  2. 逐级列 GitHub 目录发现真实路径（三段结构不一致，不拼路径）
  3. 通过 api.github.com blob 通道下载（raw.githubusercontent 国内常被墙）
  4. 校验 %PDF- 头 + 文件大小；截断则重试 1 次
  5. 成功打印 JSON 结果到 stdout

退出码: 0 成功 / 1 失败（stderr 输出原因）
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REPO = "TapXWorld/ChinaTextbook"
API = "https://api.github.com/repos/" + REPO
TIMEOUT = 30

SUBJECT_CN = {"math": "数学", "chinese": "语文", "english": "英语"}
SUBJECT_EN = {v: k for k, v in SUBJECT_CN.items()}

GRADE_TO_JUNIOR = {"初一": "七年级", "初二": "八年级", "初三": "九年级"}

# 版本别名：档案里的说法可能和仓库目录名不同
VERSION_ALIASES = {
    "部编版": ["统编版"],
    "人教统编版": ["统编版"],
    "外研版": ["外研社版"],
    "人教版": ["人教版"],
}


def api_get(url, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, headers={
        "Accept": accept,
        "User-Agent": "ai-kids-tutor",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.load(r)


def ls(path):
    """列目录，返回 list[dict]"""
    url = API + "/contents/" + urllib.parse.quote(path)
    try:
        data = api_get(url)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"列目录失败 {path}: HTTP {e.code}")
    if isinstance(data, dict):
        raise RuntimeError(f"列目录失败 {path}: {data.get('message', 'unknown')}")
    return data


def detect_stage(grade):
    if "初" in grade or any(g in grade for g in ("七年级", "八年级", "九年级")):
        return "初中"
    if "高" in grade:
        return "高中"
    return "小学"


def version_candidates(version):
    return VERSION_ALIASES.get(version, [version])


def pick_dir(dirs, keywords):
    """版本目录：目录名包含任一关键词即命中"""
    for kw in keywords:
        hit = [d for d in dirs if d["type"] == "dir" and kw in d["name"]]
        if hit:
            return hit[0]
    return None


def resolve(subject_cn, grade, term, version):
    """返回 (pdf_item, 实际路径描述)"""
    stage = detect_stage(grade)
    grade_dir = GRADE_TO_JUNIOR.get(grade, grade)  # 初一 -> 七年级

    # 1) 学段/科目 下的版本目录
    ver = pick_dir(ls(f"{stage}/{subject_cn}"), version_candidates(version))
    if not ver:
        avail = [d["name"] for d in ls(f"{stage}/{subject_cn}") if d["type"] == "dir"]
        raise RuntimeError(
            f"未找到版本「{version}」。{stage}/{subject_cn} 下可用版本：{avail}"
        )

    base = f"{stage}/{subject_cn}/{ver['name']}"

    # 2) 是否有年级子目录（初中才有）
    entries = ls(base)
    subdirs = [e for e in entries if e["type"] == "dir"]
    if subdirs:
        gd = pick_dir(subdirs, [grade_dir])
        if not gd:
            raise RuntimeError(
                f"未找到年级目录「{grade_dir}」。{base} 下有：{[d['name'] for d in subdirs]}"
            )
        entries = ls(gd["path"])
        base = gd["path"]

    # 3) 找 pdf
    pdfs = [e for e in entries if e["name"].lower().endswith(".pdf")]
    hit = [p for p in pdfs if term in p["name"]]
    if not hit:
        raise RuntimeError(
            f"未找到「{term}」教材。{base} 下有：{[p['name'] for p in pdfs]}"
        )
    if len(hit) > 1:
        hit.sort(key=lambda p: len(p["name"]))
    return hit[0], base


def download(item, out_path, retries=1):
    """通过 blob 通道下载，返回 (ok, msg)"""
    sha, expect = item["sha"], item["size"]
    url = f"{API}/git/blobs/{sha}"

    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={
                "Accept": "application/vnd.github.raw",
                "User-Agent": "ai-kids-tutor",
            })
            with urllib.request.urlopen(req, timeout=300) as r, \
                    open(out_path, "wb") as f:
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
        except Exception as e:
            if attempt >= retries:
                return False, f"下载异常: {e}"
            time.sleep(2)
            continue

        actual = os.path.getsize(out_path)
        if actual == expect:
            with open(out_path, "rb") as f:
                if f.read(5) == b"%PDF-":
                    return True, f"OK {actual} bytes"
            if attempt >= retries:
                return False, f"文件头不是 %PDF-（疑似 HTML 错误页），大小 {actual}"
        else:
            if attempt >= retries:
                return False, (
                    f"下载被截断：{actual}/{expect} bytes"
                    f"（期望 {expect/1048576:.1f}MB，实得 {actual/1048576:.1f}MB）"
                )
        time.sleep(2)
    return False, "未知失败"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True)
    ap.add_argument("--grade", required=True)
    ap.add_argument("--term", default="上册")
    ap.add_argument("--version", default="人教版")
    ap.add_argument("--out", default="./textbooks")
    ap.add_argument("--name", default=None)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    subject_cn = SUBJECT_CN.get(a.subject, a.subject)
    subject_en = SUBJECT_EN.get(subject_cn, a.subject)

    try:
        item, base = resolve(subject_cn, a.grade, a.term, a.version)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    info = {
        "ok": True,
        "path": item["path"],
        "size": item["size"],
        "size_mb": round(item["size"] / 1048576, 1),
        "sha": item["sha"],
    }

    if a.list:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return

    os.makedirs(a.out, exist_ok=True)
    gb = GRADE_TO_JUNIOR.get(a.grade, a.grade)
    short = gb.replace("年级", "").replace("初", "").replace("高", "")
    name = a.name or f"{subject_en}_{short}{a.term}_{a.version}.pdf"
    out_path = os.path.join(a.out, name)

    ok, msg = download(item, out_path)
    info.update({"saved": out_path, "result": msg, "ok": ok})
    print(json.dumps(info, ensure_ascii=False, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
