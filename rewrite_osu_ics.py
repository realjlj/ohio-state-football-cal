#!/usr/bin/env python3
"""Fetch Ohio State official football ICS; rewrite titles to put scores first."""
from __future__ import annotations

import re
import sys
import urllib.request
from datetime import datetime, timezone

SOURCE = "https://ohiostatebuckeyes.com/calendar.ashx/calendar.ics?sport_id=2"
UA = "Mozilla/5.0 (compatible; OSUFootballCal/1.0)"

SCORE_RE = re.compile(r"(?m)^([WL])\s+(\d+-\d+)\s*$")
# Official titles look like:
#   [W] Ohio State Football vs Ball State  - Promo...
#   Ohio State Football at Texas
MATCHUP_RE = re.compile(
    r"(?:\[([WL])\]\s*)?Ohio State Football\s+(vs|at)\s+(.+?)(?:\s+-\s+.+)?\s*$",
    re.I,
)


def unfold(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    out: list[str] = []
    for line in text.split("\n"):
        if line.startswith((" ", "\t")) and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return "\n".join(out)


def fold(line: str, limit: int = 75) -> str:
    if len(line) <= limit:
        return line
    chunks = [line[:limit]]
    rest = line[limit:]
    while rest:
        chunks.append(" " + rest[: limit - 1])
        rest = rest[limit - 1 :]
    return "\r\n".join(chunks)


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")


def unesc(s: str) -> str:
    return (
        s.replace("\\n", "\n")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
    )


def parse_events(ics: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    lines = unfold(ics).split("\n")
    cal_props: dict[str, str] = {}
    events: list[dict[str, str]] = []
    cur: dict[str, str] | None = None
    in_event = False
    for line in lines:
        if line == "BEGIN:VEVENT":
            in_event = True
            cur = {}
            continue
        if line == "END:VEVENT":
            if cur is not None:
                events.append(cur)
            cur = None
            in_event = False
            continue
        if line.startswith("BEGIN:") or line.startswith("END:"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        name = key.split(";", 1)[0]
        if in_event and cur is not None:
            cur[key] = val  # keep full key (with params) for DTSTART etc.
            cur[f"_{name}"] = val
        else:
            cal_props[name] = val
    return cal_props, events


def clean_opponent(raw: str) -> str:
    # Drop trailing promo after " - "
    name = raw.strip()
    if " - " in name:
        name = name.split(" - ", 1)[0].strip()
    return re.sub(r"\s+", " ", name)


def rewrite_summary(summary: str, description: str) -> str:
    summary_u = unesc(summary)
    desc_u = unesc(description)

    score = None
    m = SCORE_RE.search(desc_u)
    if m:
        score = f"{m.group(1)} {m.group(2)}"

    match = MATCHUP_RE.match(summary_u)
    if match:
        wl_in_title, prep, opp = match.group(1), match.group(2).lower(), clean_opponent(match.group(3))
        matchup = f"{prep} {opp}"
        if score:
            return f"{score} · {matchup}"
        if wl_in_title:
            return f"[{wl_in_title}] {matchup}"
        return matchup

    # Fallback: keep short, prepend score if found
    short = summary_u
    if score:
        return f"{score} · {short}"
    return short


def build_ics(events: list[dict[str, str]]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Josh//Ohio State Football Scores//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Ohio State Football",
        "X-WR-TIMEZONE:America/New_York",
        "X-PUBLISHED-TTL:PT1H",
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
    ]
    keep_keys = (
        "DTSTART",
        "DTEND",
        "LOCATION",
        "DESCRIPTION",
        "URL",
        "STATUS",
        "TRANSP",
        "GEO",
        "CATEGORIES",
    )
    for ev in events:
        summary_raw = ev.get("_SUMMARY") or ev.get("SUMMARY") or ""
        desc_raw = ev.get("_DESCRIPTION") or ev.get("DESCRIPTION") or ""
        new_summary = rewrite_summary(summary_raw, desc_raw)

        lines.append("BEGIN:VEVENT")
        uid = ev.get("_UID") or ev.get("UID")
        if uid:
            lines.append(f"UID:{uid}")
        lines.append(f"DTSTAMP:{now}")
        lines.append(f"SUMMARY:{esc(new_summary)}")

        # Prefer original keyed lines (preserve VALUE=DATE / TZID params)
        for base in keep_keys:
            for k, v in ev.items():
                if k.startswith("_"):
                    continue
                if k.split(";", 1)[0] == base:
                    lines.append(f"{k}:{v}")
                    break
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    # CRLF + fold
    folded = []
    for line in lines:
        folded.append(fold(line))
    return "\r\n".join(folded) + "\r\n"


def main() -> int:
    out_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/osu-football-cal/ohio-state-football.ics"
    req = urllib.request.Request(SOURCE, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    _, events = parse_events(raw)
    ics = build_ics(events)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(ics)
    # preview
    print(f"wrote {out_path} events={len(events)}")
    for ev in events:
        s = rewrite_summary(ev.get("_SUMMARY", ""), ev.get("_DESCRIPTION", ""))
        print(" ", s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
