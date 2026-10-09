#!/usr/bin/env python3
"""Generate the SVG assets used by the profile README.

Edit the data below (projects, stack, about) and run:

    python3 assets/build.py

Every SVG is self-contained (no external fonts, images or scripts), so it
renders identically through GitHub's image proxy. Text is monospace so that
layout widths stay predictable across operating systems.
"""

from __future__ import annotations

import math
import random
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------- palette ---
BG = "#0A0F1E"
PANEL = "#0F1629"
EDGE = "#1C2747"
TEXT = "#E6EAF5"
MUTED = "#8A94B4"
DIM = "#4B5677"
CYAN = "#5EEAD4"
AMBER = "#FBBF24"
PINK = "#F472B6"
VIOLET = "#A78BFA"
GREEN = "#4ADE80"

MONO = "ui-monospace,'JetBrains Mono','SF Mono',Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"
CHAR_W = 0.61  # average advance of a monospace glyph, in em


def tw(text: str, size: float) -> float:
    """Approximate rendered width of monospace text."""
    return len(text) * size * CHAR_W


def t(text: str) -> str:
    return escape(text, quote=False)


def svg(width: int, height: int, body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">\n'
        f"<title>{t(title)}</title>\n"
        f"<style>text{{font-family:{MONO};}}</style>\n"
        f"{body}\n</svg>\n"
    )


def dot_grid(width: int, height: int, gap: int = 24, pid: str = "grid") -> str:
    return (
        f'<defs><pattern id="{pid}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{EDGE}"/></pattern></defs>'
        f'<rect width="{width}" height="{height}" fill="url(#{pid})"/>'
    )


def chip(x: float, y: float, label: str, color: str, size: int = 13, h: int = 26) -> tuple[str, float]:
    w = tw(label, size) + 22
    out = (
        f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" '
        f'fill="{color}" fill-opacity="0.10" stroke="{color}" stroke-opacity="0.45"/>'
        f'<text x="{x + w/2:.1f}" y="{y + h/2 + size*0.36:.1f}" font-size="{size}" '
        f'fill="{color}" text-anchor="middle">{t(label)}</text>'
    )
    return out, w


# ----------------------------------------------------------------- header ---
def header() -> str:
    W, H = 1200, 340
    rnd = random.Random(7)

    # Mesh: nodes on the right half, each linked to its nearest neighbours.
    nodes = []
    while len(nodes) < 15:
        p = (rnd.uniform(700, 1160), rnd.uniform(36, H - 36))
        if all(math.dist(p, q) > 70 for q in nodes):
            nodes.append(p)
    edges = set()
    for i, p in enumerate(nodes):
        near = sorted(range(len(nodes)), key=lambda j: math.dist(p, nodes[j]))[1:3]
        for j in near:
            edges.add(tuple(sorted((i, j))))
    edges = sorted(edges)

    parts = [f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>', dot_grid(W, H, pid="hgrid")]
    parts.append(
        '<defs><linearGradient id="fade" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{BG}" stop-opacity="1"/>'
        f'<stop offset="0.55" stop-color="{BG}" stop-opacity="0.92"/>'
        f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>'
        '<radialGradient id="glow"><stop offset="0" stop-color="#5EEAD4" stop-opacity="0.18"/>'
        '<stop offset="1" stop-color="#5EEAD4" stop-opacity="0"/></radialGradient></defs>'
    )
    parts.append(f'<circle cx="930" cy="170" r="260" fill="url(#glow)"/>')

    for k, (i, j) in enumerate(edges):
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        length = math.dist(nodes[i], nodes[j])
        parts.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{EDGE}" stroke-width="1.5"/>')
        if k % 2 == 0:  # travelling packet
            dur = 2.4 + (k % 5) * 0.5
            color = CYAN if k % 4 else AMBER
            parts.append(
                f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{color}" '
                f'stroke-width="2" stroke-linecap="round" stroke-dasharray="10 {length:.0f}">'
                f'<animate attributeName="stroke-dashoffset" from="{length + 10:.0f}" to="0" '
                f'dur="{dur:.1f}s" begin="{k * 0.37:.2f}s" repeatCount="indefinite"/></line>'
            )
    for n, (x, y) in enumerate(nodes):
        color = AMBER if n in (3, 9) else CYAN
        parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{color}" fill-opacity="0.12"/>')
        parts.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4" fill="{color}">'
            f'<animate attributeName="opacity" values="1;0.35;1" dur="{2 + n % 4}s" '
            f'begin="{n * 0.3:.1f}s" repeatCount="indefinite"/></circle>'
        )
    parts.append(f'<rect width="760" height="{H}" fill="url(#fade)"/>')

    # Left: terminal-style identity block.
    parts.append(f'<text x="64" y="86" font-size="17" fill="{MUTED}"><tspan fill="{CYAN}">~/rishon-g</tspan> $ whoami</text>')
    parts.append(f'<text x="62" y="152" font-size="58" font-weight="700" fill="{TEXT}">Rishon Ghosh</text>')
    cursor_x = 62 + tw("Rishon Ghosh", 58) + 10
    parts.append(
        f'<rect x="{cursor_x:.0f}" y="110" width="22" height="48" fill="{CYAN}">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>'
    )
    parts.append(f'<text x="64" y="196" font-size="19" fill="{MUTED}">Computer Science + Business @ Simon Fraser University</text>')
    parts.append(f'<text x="64" y="228" font-size="19" fill="{TEXT}">backend <tspan fill="{DIM}">·</tspan> distributed systems <tspan fill="{DIM}">·</tspan> cloud</text>')

    label = "open to software engineering co-op"
    pw = tw(label, 15) + 50
    parts.append(f'<rect x="64" y="258" width="{pw:.0f}" height="36" rx="18" fill="{GREEN}" fill-opacity="0.10" stroke="{GREEN}" stroke-opacity="0.5"/>')
    parts.append(
        f'<circle cx="86" cy="276" r="5" fill="{GREEN}"><animate attributeName="r" values="5;8;5" dur="1.8s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="1;0.4;1" dur="1.8s" repeatCount="indefinite"/></circle>'
    )
    parts.append(f'<text x="102" y="281" font-size="15" fill="{GREEN}">{t(label)}</text>')
    parts.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{EDGE}"/>')
    return svg(W, H, "".join(parts), "Rishon Ghosh — CS + Business at SFU, open to software engineering co-op")


# ---------------------------------------------------------------- buttons ---
BUTTONS = {
    "linkedin": ("LinkedIn", CYAN, "in"),
    "resume": ("Resume", AMBER, "cv"),
    "email": ("Email", PINK, "@"),
}


def button(name: str) -> str:
    label, color, glyph = BUTTONS[name]
    W, H = 168, 46
    body = (
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="{PANEL}" stroke="{color}" stroke-opacity="0.55"/>'
        f'<rect x="10" y="9" width="28" height="28" rx="8" fill="{color}" fill-opacity="0.15"/>'
        f'<text x="24" y="28" font-size="14" font-weight="700" fill="{color}" text-anchor="middle">{t(glyph)}</text>'
        f'<text x="52" y="29" font-size="16" fill="{TEXT}">{t(label)}</text>'
        f'<text x="{W-18}" y="29" font-size="16" fill="{color}" text-anchor="end">↗</text>'
    )
    return svg(W, H, body, label)


# ------------------------------------------------------------ section bar ---
def section(title: str, color: str, light: bool = False) -> str:
    W, H = 1200, 56
    fg, line = ("#1F2328", "#D0D7DE") if light else (TEXT, EDGE)
    lw = tw(f"// {title}", 22)
    body = (
        f'<text x="2" y="36" font-size="22" font-weight="700" fill="{fg}"><tspan fill="{color}">//</tspan> {t(title)}</text>'
        f'<line x1="{lw + 26:.0f}" y1="29" x2="{W - 2}" y2="29" stroke="{line}" stroke-width="2"/>'
        f'<line x1="{lw + 26:.0f}" y1="29" x2="{W - 2}" y2="29" stroke="{color}" stroke-width="2" stroke-dasharray="40 {W}">'
        f'<animate attributeName="stroke-dashoffset" from="{W:.0f}" to="0" dur="5s" repeatCount="indefinite"/></line>'
    )
    return svg(W, H, body, title)


# ------------------------------------------------------------------ about ---
ABOUT = [
    ("const", " rishon = {", None),
    ("key", "school", '"Simon Fraser University"'),
    ("key", "major", '"Computer Science + Business (joint), class of 2028"'),
    ("key", "standing", '"3.9 CGPA · Dean\'s & President\'s Honour Roll"'),
    ("key", "focus", '["backend", "distributed systems", "cloud infra"]'),
    ("key", "building", '"MatchMesh: a fault-tolerant C++20 matchmaking cluster"'),
    ("key", "openTo", '"Software Engineering Co-op"'),
    ("key", "offline", '["strength training", "the markets", "sports"]'),
    ("close", "};", None),
]


def about() -> str:
    W = 1200
    line_h = 30
    top = 64
    H = top + line_h * len(ABOUT) + 30
    p = [
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="{BG}" stroke="{EDGE}"/>',
        f'<path d="M0.5 16.5 a16 16 0 0 1 16 -16 H{W-16.5} a16 16 0 0 1 16 16 V44 H0.5 Z" fill="{PANEL}"/>',
        f'<line x1="0" y1="44" x2="{W}" y2="44" stroke="{EDGE}"/>',
    ]
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        p.append(f'<circle cx="{26 + i * 20}" cy="22" r="6" fill="{c}"/>')
    p.append(f'<text x="{W/2}" y="27" font-size="14" fill="{MUTED}" text-anchor="middle">about.ts</text>')
    for n, (kind, a, b) in enumerate(ABOUT):
        y = top + 20 + n * line_h
        p.append(f'<text x="28" y="{y}" font-size="15" fill="{DIM}" text-anchor="end">{n + 1}</text>')
        if kind == "const":
            p.append(f'<text x="52" y="{y}" font-size="17" fill="{TEXT}"><tspan fill="{VIOLET}">const</tspan><tspan fill="{CYAN}"> rishon</tspan> = {{</text>')
        elif kind == "close":
            p.append(f'<text x="52" y="{y}" font-size="17" fill="{TEXT}">{t(a)}</text>')
        else:
            p.append(f'<text x="{52 + tw("    ", 17):.0f}" y="{y}" font-size="17" fill="{TEXT}"><tspan fill="{PINK}">{t(a)}</tspan>: <tspan fill="{AMBER}">{t(b)}</tspan>,</text>')
    last_y = top + 20 + (len(ABOUT) - 1) * line_h
    p.append(
        f'<rect x="{52 + tw("};", 17) + 6:.0f}" y="{last_y - 15}" width="10" height="20" fill="{CYAN}">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>'
    )
    return svg(W, H, "".join(p), "About Rishon: SFU CS + Business, focus on backend, distributed systems and cloud")


# --------------------------------------------------------------- projects ---
PROJECTS = [
    {
        "slug": "flashcart", "name": "FlashCart", "tag": "AWS · serverless", "color": AMBER,
        "lines": ["Serverless flash-sale checkout that holds 1,000",
                  "concurrent buyers to exactly the stock that exists."],
        "chips": ["~6.9k req/s", "194 ms p95", "0 oversold"],
        "stack": "Go · Lambda · DynamoDB · SQS · CDK · React",
    },
    {
        "slug": "matchmesh", "name": "MatchMesh", "tag": "in progress", "color": CYAN,
        "lines": ["Fault-tolerant matchmaking cluster: skill-based",
                  "lobbies, consistent hashing, replication."],
        "chips": ["4-player lobbies", "sharded queues", "TSan builds"],
        "stack": "C++20 · gRPC · Protobuf · CMake · Docker",
    },
    {
        "slug": "trustline", "name": "TrustLine", "tag": "StormHacks", "color": PINK,
        "lines": ["Live, in-language scam-call warnings for",
                  "newcomers to Canada: just dial it into the call."],
        "chips": ["real-time STT", "5 languages", "partner portal"],
        "stack": "TypeScript · React · Twilio · Gemini",
    },
    {
        "slug": "graphite-gambit", "name": "Graphite Gambit", "tag": "team lead", "color": GREEN,
        "lines": ["2D top-down stealth game with A* enemy",
                  "pathfinding and a custom collision engine."],
        "chips": ["71% branch cov.", "A* pathing", "agile sprints"],
        "stack": "Java · libGDX · JUnit 5 · Mockito · JaCoCo",
    },
    {
        "slug": "rubiks-cube-solver", "name": "Rubik's Solver", "tag": "algorithms", "color": VIOLET,
        "lines": ["Kociemba-style two-phase solver; compact pruning",
                  "tables give O(1) heuristic lookups."],
        "chips": ["IDA* search", "~2 MB tables", "< 10 s solves"],
        "stack": "Java · Maven",
    },
    {
        "slug": "tindog", "name": "Tindog", "tag": "FallHacks 2025", "color": AMBER,
        "lines": ["Tinder for dogs: profiles, swipes and matches",
                  "gated on shared music taste."],
        "chips": ["built in 12 h", "3-person team", "hashed auth"],
        "stack": "Python · Flask · SQLite · Jinja",
    },
]


def card(p: dict) -> str:
    W, H = 580, 250
    c = p["color"]
    parts = [
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="{BG}" stroke="{EDGE}"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{c}" stroke-opacity="0.9" '
        f'stroke-dasharray="70 {2 * (W + H)}">'
        f'<animate attributeName="stroke-dashoffset" from="{2 * (W + H):.0f}" to="0" dur="9s" repeatCount="indefinite"/></rect>',
        f'<rect x="28" y="30" width="10" height="10" rx="2" fill="{c}"/>',
        f'<text x="50" y="41" font-size="24" font-weight="700" fill="{TEXT}">{t(p["name"])}</text>',
    ]
    tag = p["tag"]
    tw_ = tw(tag, 13) + 20
    parts.append(f'<rect x="{W - 28 - tw_:.0f}" y="24" width="{tw_:.0f}" height="24" rx="6" fill="{PANEL}" stroke="{EDGE}"/>')
    parts.append(f'<text x="{W - 28 - tw_/2:.0f}" y="40.5" font-size="13" fill="{MUTED}" text-anchor="middle">{t(tag)}</text>')
    for i, line in enumerate(p["lines"]):
        parts.append(f'<text x="28" y="{86 + i * 24}" font-size="16" fill="{MUTED}">{t(line)}</text>')
    x = 28.0
    for label in p["chips"]:
        s, w = chip(x, 140, label, c)
        parts.append(s)
        x += w + 10
    parts.append(f'<line x1="28" y1="190" x2="{W-28}" y2="190" stroke="{EDGE}"/>')
    parts.append(f'<text x="28" y="221" font-size="14" fill="{TEXT}"><tspan fill="{c}">&gt;</tspan> {t(p["stack"])}</text>')
    parts.append(f'<text x="{W-28}" y="221" font-size="15" fill="{c}" text-anchor="end">view repo ↗</text>')
    return svg(W, H, "".join(parts), f'{p["name"]}: {" ".join(p["lines"])}')


# ------------------------------------------------------------------ stack ---
STACK = [
    ("languages", CYAN, ["C++", "Go", "Java", "Python", "TypeScript", "JavaScript", "C", "SQL", "HTML/CSS", "x86-64 asm"]),
    ("backend & cloud", AMBER, ["AWS Lambda", "DynamoDB", "SQS", "EventBridge", "API Gateway", "S3 + CloudFront",
                                "gRPC", "Protobuf", "Flask", "Supabase", "Twilio"]),
    ("frontend", PINK, ["React", "Vite", "TanStack Query", "Jinja"]),
    ("infra & devops", VIOLET, ["AWS CDK", "Docker", "CMake", "GitHub Actions", "Vercel", "Maven", "Linux", "Git"]),
    ("testing & perf", GREEN, ["JUnit 5", "Mockito", "JaCoCo", "Jest", "Vitest", "k6", "ThreadSanitizer", "DynamoDB Local"]),
]


def stack() -> str:
    W = 1200
    label_w = 200
    x0, x_max = 28 + label_w, W - 28
    row_h, gap = 36, 10
    parts, y = [], 30
    for name, color, items in STACK:
        parts.append(f'<text x="28" y="{y + 18}" font-size="15" fill="{color}">{t(name)}</text>')
        x = x0
        for item in items:
            w = tw(item, 14) + 22
            if x + w > x_max:
                x, y = x0, y + row_h
            s, w = chip(x, y, item, color, size=14, h=28)
            parts.append(s)
            x += w + gap
        y += row_h + 14
    H = y + 12
    frame = f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="{BG}" stroke="{EDGE}"/>'
    return svg(W, H, frame + "".join(parts), "Tech stack")


# ----------------------------------------------------------------- footer ---
def footer(light: bool = False) -> str:
    W, H = 1200, 90
    fg, accent = ("#59636E", "#0F766E") if light else (MUTED, CYAN)
    msg = "thanks for stopping by: let's build something reliable."
    body = (
        f'<text x="{W/2}" y="52" font-size="17" fill="{fg}" text-anchor="middle">'
        f'<tspan fill="{accent}">$</tspan> echo "{t(msg)}"</text>'
    )
    return svg(W, H, body, msg)


SECTIONS = [
    ("about", "about", CYAN),
    ("projects", "featured projects", AMBER),
    ("stack", "tech stack", VIOLET),
    ("contact", "let's connect", PINK),
]
# Darker accents keep the "//" readable on GitHub's white background.
LIGHT_ACCENT = {CYAN: "#0F766E", AMBER: "#B45309", VIOLET: "#6D28D9", PINK: "#BE185D"}


def main() -> None:
    files = {
        "header.svg": header(),
        "about.svg": about(),
        "stack.svg": stack(),
        "footer.svg": footer(),
        "footer-light.svg": footer(light=True),
    }
    for slug, title, color in SECTIONS:
        files[f"section-{slug}.svg"] = section(title, color)
        files[f"section-{slug}-light.svg"] = section(title, LIGHT_ACCENT.get(color, color), light=True)
    files |= {f"btn-{k}.svg": button(k) for k in BUTTONS}
    files |= {f"project-{p['slug']}.svg": card(p) for p in PROJECTS}
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(files)} files to {OUT}")


if __name__ == "__main__":
    main()
