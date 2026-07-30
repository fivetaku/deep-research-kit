#!/usr/bin/env python3
"""보고서의 claim/source 태그를 Markdown 각주로 변환한다. deps: stdlib. 실행: python3 scripts/convert_footnotes.py --help"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SOURCE_PATTERN = re.compile(r"\[(src_\d{3,})\]")
CLAIM_PATTERN = re.compile(r"\[(clm_\d{3,})\]")
TAG_GROUP_PATTERN = re.compile(r"((?:\[(?:src|clm)_\d{3,}\]\s*)+)")


def read_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    records = {}
    if not path.is_file():
        return records
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            item_id = item.get("id") or item.get("claim_id")
            if item_id:
                records[str(item_id)] = item
    return records


def format_footnote_content(
    tag_list: list[str],
    sources: dict[str, dict[str, Any]],
    claims: dict[str, dict[str, Any]],
) -> str:
    parts = []
    clm_tags = [t for t in tag_list if t.startswith("clm_")]
    src_tags = [t for t in tag_list if t.startswith("src_")]

    if clm_tags:
        clm_texts = []
        for ct in clm_tags:
            c = claims.get(ct)
            if c:
                clm_texts.append(f"**주장 [{ct}]**: {c.get('text')}")
            else:
                clm_texts.append(f"**주장 [{ct}]**")
        parts.append(" | ".join(clm_texts))

    if src_tags:
        src_texts = []
        for st in src_tags:
            s = sources.get(st)
            if s:
                author = s.get("author", "알 수 없음")
                title = s.get("title", "제목 없음")
                url = s.get("url", "")
                pub = s.get("published_at", "")
                link_str = f"[{title}]({url})" if url else title
                src_texts.append(f"{author}, 《{link_str}》({pub})")
            else:
                src_texts.append(f"출처 [{st}]")
        parts.append("출처: " + "; ".join(src_texts))

    return " — ".join(parts) if parts else ", ".join(tag_list)


def convert_report(
    report_text: str,
    sources: dict[str, dict[str, Any]],
    claims: dict[str, dict[str, Any]],
) -> tuple[str, list[tuple[int, str]]]:
    # 특정 부록/감사 섹션(Confidence, Refuted, Unresolved, 참고문헌) 전까지만 인용 변환
    tag_to_index: dict[str, int] = {}
    footnote_entries: list[tuple[int, str]] = []
    next_index = 1

    def replace_match(match: re.Match) -> str:
        nonlocal next_index
        raw_group = match.group(1).strip()
        tags = re.findall(r"(?:src|clm)_\d{3,}", raw_group)
        if not tags:
            return raw_group

        key = " ".join(sorted(tags))
        if key not in tag_to_index:
            tag_to_index[key] = next_index
            content = format_footnote_content(tags, sources, claims)
            footnote_entries.append((next_index, content))
            next_index += 1

        idx = tag_to_index[key]
        return f"[^{idx}]"

    # 참고문헌 섹션 및 부록 섹션 분리 처리
    split_match = re.search(
        r"^(##\s+(?:Confidence|Refuted|Unresolved|참고문헌|Bibliography).*)$",
        report_text,
        flags=re.MULTILINE,
    )
    if split_match:
        main_body = report_text[: split_match.start()]
        tail_body = report_text[split_match.start() :]
    else:
        main_body = report_text
        tail_body = ""

    converted_main = TAG_GROUP_PATTERN.sub(replace_match, main_body)

    # 각주 목록 형성
    footnotes_section = "\n\n## 각주 (Footnotes)\n"
    for idx, content in footnote_entries:
        footnotes_section += f"[^{idx}]: {content}\n"

    result_text = (
        converted_main.rstrip() + footnotes_section + "\n" + tail_body.lstrip()
    )
    return result_text, footnote_entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True, help="세션 디렉터리 경로")
    parser.add_argument("--report", required=True, help="대상 마크다운 보고서 경로")
    parser.add_argument(
        "--output", help="출력할 Markdown 경로. 생략하면 원본을 덮어쓴다"
    )
    args = parser.parse_args()

    session_path = Path(args.session).expanduser()
    report_path = Path(args.report).expanduser()
    output_path = Path(args.output).expanduser() if args.output else report_path

    if not report_path.is_file():
        print(f"오류: 보고서 파일을 찾을 수 없습니다: {report_path}", file=sys.stderr)
        return 1

    sources = read_jsonl(session_path / "sources/sources.jsonl")
    claims = read_jsonl(session_path / "artifacts/claim_ledger.jsonl")
    report_text = report_path.read_text(encoding="utf-8")

    converted_text, entries = convert_report(report_text, sources, claims)
    output_path.write_text(converted_text, encoding="utf-8")

    print(f"성공적으로 각주 변환을 완료했습니다 ({len(entries)}개의 각주 생성).")
    print(f"저장 위치: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
