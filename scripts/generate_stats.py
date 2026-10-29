
import json
import urllib.request
from pathlib import Path
from html import escape

USER = "BrunoGasparr"
BASE = Path("assets")
BASE.mkdir(exist_ok=True)

BG = "#0D0B12"
PURPLE = "#A78BFA"
VIOLET = "#8B5CF6"
TEXT = "#D4D4D8"
MUTED = "#92909D"
BORDER = "#30263F"


def get_json(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def card(title, width=495, height=165):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect x="1" y="1" width="{width-2}" '
        f'height="{height-2}" rx="12" fill="{BG}" '
        f'stroke="{BORDER}"/>'
        f'<text x="22" y="32" fill="{PURPLE}" '
        f'font-family="Segoe UI,Arial,sans-serif" '
        f'font-size="15" font-weight="600">'
        f'{escape(title)}</text>'
        f'<rect x="22" y="43" width="42" height="3" '
        f'rx="1.5" fill="{VIOLET}"/>'
    )


profile = get_json(f"https://api.github.com/users/{USER}")
repos = get_json(
    f"https://api.github.com/users/{USER}/repos"
    "?per_page=100&sort=updated"
)

own_repos = [
    repo for repo in repos
    if not repo.get("fork", False)
]

stars = sum(repo.get("stargazers_count", 0) for repo in own_repos)
followers = profile.get("followers", 0)
public_repos = profile.get("public_repos", 0)

# Card 1: general statistics
svg = card("PROFILE / STATISTICS")

items = [
    ("PUBLIC REPOS", public_repos),
    ("FOLLOWERS", followers),
    ("TOTAL STARS", stars),
]

for index, (label, value) in enumerate(items):
    x = 24 + index * 158
    svg += (
        f'<text x="{x}" y="91" fill="{MUTED}" '
        f'font-family="Segoe UI,Arial,sans-serif" '
        f'font-size="10">{label}</text>'
        f'<text x="{x}" y="124" fill="{TEXT}" '
        f'font-family="Segoe UI,Arial,sans-serif" '
        f'font-size="27" font-weight="600">{value}</text>'
        f'<rect x="{x}" y="140" width="112" height="3" '
        f'rx="1.5" fill="{BORDER}"/>'
        f'<rect x="{x}" y="140" width="{min(112, value * 5)}" '
        f'height="3" rx="1.5" fill="{VIOLET}"/>'
    )

(BASE / "stats.svg").write_text(svg + "</svg>", encoding="utf-8")

# Card 2: primary language across public repositories
language_counts = {}
for repo in own_repos:
    language = repo.get("language")
    if language:
        language_counts[language] = language_counts.get(language, 0) + 1

top_languages = sorted(
    language_counts.items(),
    key=lambda item: item[1],
    reverse=True
)[:5]

svg = card("CODE / LANGUAGES")
total = sum(count for _, count in top_languages) or 1
bar_x = 22
bar_y = 57
bar_width = 451
colors = ["#8B5CF6", "#A78BFA", "#6D28D9", "#C4B5FD", "#4C1D95"]

for index, (language, count) in enumerate(top_languages):
    segment_width = bar_width * count / total
    svg += (
        f'<rect x="{bar_x}" y="{bar_y}" '
        f'width="{segment_width:.2f}" height="7" '
        f'rx="2" fill="{colors[index]}"/>'
    )
    bar_x += segment_width

for index, (language, count) in enumerate(top_languages):
    x = 24 + (index % 2) * 230
    y = 91 + (index // 2) * 25
    svg += (
        f'<circle cx="{x+4}" cy="{y-4}" r="4" '
        f'fill="{colors[index]}"/>'
        f'<text x="{x+15}" y="{y}" fill="{TEXT}" '
        f'font-family="Segoe UI,Arial,sans-serif" '
        f'font-size="11">{escape(language)}</text>'
        f'<text x="{x+195}" y="{y}" fill="{PURPLE}" '
        f'text-anchor="end" '
        f'font-family="Segoe UI,Arial,sans-serif" '
        f'font-size="11">{count} repos</text>'
    )

if not top_languages:
    svg += (
        f'<text x="22" y="88" fill="{MUTED}" '
        f'font-family="Segoe UI,Arial,sans-serif" '
        f'font-size="12">No language data yet</text>'
    )

(BASE / "languages.svg").write_text(svg + "</svg>", encoding="utf-8")

print("Profile cards generated successfully.")

