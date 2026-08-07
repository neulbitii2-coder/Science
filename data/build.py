# -*- coding: utf-8 -*-
"""
app/core.html + data/messages_1000.csv  ->  index.html (단일 파일 웹앱)

부가로 dist/artifact.html (head/body 래퍼 없는 본문 전용) 도 만듭니다.

사용법:
    python3 data/generate_dataset.py
    python3 data/build.py
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CORE = os.path.join(ROOT, "app", "core.html")
CSV = os.path.join(HERE, "messages_1000.csv")
COLLECT = os.path.join(HERE, "collect_url.txt")
OUT_HTML = os.path.join(ROOT, "index.html")
OUT_ART = os.path.join(ROOT, "dist", "artifact.html")

HEAD = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
{head_extra}</head>
<body>
"""

TAIL = "</body>\n</html>\n"


def main():
    core = open(CORE, encoding="utf-8").read()
    csv_text = open(CSV, encoding="utf-8-sig").read().replace("\r\n", "\n").strip()

    # 템플릿 리터럴 안에서 문제되는 문자만 최소로 이스케이프
    safe = csv_text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    injected = re.sub(
        r"/\*DATA_START\*/.*?/\*DATA_END\*/",
        lambda _m: safe,
        core,
        flags=re.S,
    )
    if "/*DATA_START*/" in injected:
        raise SystemExit("데이터 주입 실패: 마커를 찾지 못했습니다.")

    # 공유 수집함 주소 (비어 있으면 방문자 브라우저에만 보관)
    url = ""
    if os.path.exists(COLLECT):
        lines = [l.strip() for l in open(COLLECT, encoding="utf-8").read().splitlines()]
        url = next((l for l in lines if l and not l.startswith("#")), "")
    if url and not url.startswith("https://script.google.com/"):
        raise SystemExit(f"collect_url.txt 가 구글 Apps Script 주소가 아닙니다: {url}")
    injected = injected.replace("__COLLECT_URL__", url.replace('"', ""))
    print("공유 수집함  :", url or "(설정 안 함 — 방문자 브라우저에만 보관)")

    # <title> / <meta description> 은 단일 파일 버전에서 <head> 로 옮긴다
    head_extra = ""
    for pat in (r"^<title>.*?</title>\n", r"^<meta name=\"description\"[^>]*>\n"):
        m = re.search(pat, injected, flags=re.M)
        if m:
            head_extra += m.group(0)
            injected = injected.replace(m.group(0), "", 1)

    os.makedirs(os.path.dirname(OUT_ART), exist_ok=True)

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(HEAD.format(head_extra=head_extra) + injected.lstrip("\n") + TAIL)

    # 아티팩트/임베드용: 래퍼 없이 본문만 (title 은 다시 앞에 붙임)
    with open(OUT_ART, "w", encoding="utf-8") as f:
        f.write(head_extra + injected.lstrip("\n"))

    rows = csv_text.count("\n")
    print(f"index.html        생성 ({os.path.getsize(OUT_HTML)/1024:.0f} KB, 데이터 {rows}행)")
    print(f"dist/artifact.html 생성 ({os.path.getsize(OUT_ART)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
