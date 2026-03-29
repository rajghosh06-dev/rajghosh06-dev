from __future__ import annotations

from html import escape
import json
import os
import re
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "github_stats.json"
ASSETS_DIR = ROOT / "assets"
MONTHLY_BANNER = ASSETS_DIR / "github-pulse-monthly.svg"
YEARLY_BANNER = ASSETS_DIR / "github-pulse-yearly.svg"
GRAPH_URL = "https://github.com/users/{username}/contributions"
GRAPHQL_URL = "https://api.github.com/graphql"


def load_data() -> dict:
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_data(data: dict) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def month_bounds(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


def year_bounds(year: int, end_date: date | None = None) -> tuple[date, date]:
    start = date(year, 1, 1)
    end = end_date if end_date is not None else date(year, 12, 31)
    return start, end


def github_graphql_commit_total(username: str, start: date, end: date, token: str) -> int:
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
        }
      }
    }
    """
    payload = json.dumps(
        {
            "query": query,
            "variables": {
                "login": username,
                "from": f"{start.isoformat()}T00:00:00Z",
                "to": f"{end.isoformat()}T23:59:59Z",
            },
        }
    ).encode("utf-8")
    request = Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "rajghosh06-dev-profile-refresh",
        },
    )
    with urlopen(request) as response:
        data = json.load(response)

    if "errors" in data:
        raise RuntimeError(f"GraphQL error: {data['errors']}")

    user = data.get("data", {}).get("user")
    if user is None:
        raise RuntimeError("GraphQL response did not include user data.")

    return int(user["contributionsCollection"]["totalCommitContributions"])


def fetch_public_contribution_entries(username: str) -> list[tuple[date, int]]:
    with urlopen(GRAPH_URL.format(username=username)) as response:
        html = response.read().decode("utf-8", errors="ignore")

    pattern = re.compile(
        r'data-date="(?P<date>\d{4}-\d{2}-\d{2})"[^>]*id="(?P<id>[^"]+)"[^>]*></td>\s*'
        r'<tool-tip[^>]*for="(?P=id)"[^>]*>(?P<tip>.*?)</tool-tip>',
        re.S,
    )

    entries: list[tuple[date, int]] = []
    for match in pattern.finditer(html):
        day = date.fromisoformat(match.group("date"))
        tip = re.sub(r"<.*?>", "", match.group("tip")).strip()
        count_match = re.search(r"(\d+) contribution", tip)
        count = int(count_match.group(1)) if count_match else 0
        entries.append((day, count))
    return entries


def scrape_public_contribution_total(username: str, start: date, end: date) -> int:
    entries = fetch_public_contribution_entries(username)
    return sum(count for day, count in entries if start <= day <= end)


def commit_total(username: str, start: date, end: date) -> int:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        try:
            return github_graphql_commit_total(username, start, end, token)
        except (HTTPError, URLError, RuntimeError, KeyError, ValueError) as exc:
            print(f"Falling back to public contribution scrape: {exc}")
    return scrape_public_contribution_total(username, start, end)


def write_svg(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def svg_safe(value: str) -> str:
    return escape(value, quote=True)


def create_two_panel_banner(title: str, items: list[dict[str, str]]) -> str:
    width = 920
    height = 276
    outer_x = 14
    outer_y = 14
    outer_w = width - (outer_x * 2)
    outer_h = height - (outer_y * 2)
    panel_gap = 20
    panel_x = 36
    panel_y = 102
    panel_w = (width - panel_x * 2 - panel_gap) // 2
    panel_h = 134
    bg = "#0d1117"
    border = "#30415f"
    card_bg = "#101827"
    panel_bg = "#0f1729"
    text = "#e6edf7"
    muted = "#93a4ba"
    title_color = "#60a5fa"
    divider = "#233047"
    divider_y = panel_y + panel_h - 22
    note_y = panel_y + panel_h - 7

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{svg_safe(title)}">',
        f'<rect width="{width}" height="{height}" fill="{bg}"/>',
        f'<rect x="{outer_x}" y="{outer_y}" width="{outer_w}" height="{outer_h}" rx="14" fill="{card_bg}" stroke="{border}" stroke-width="2"/>',
        f'<text x="40" y="62" fill="{title_color}" font-family="Segoe UI, Arial, sans-serif" font-size="29" font-weight="700">{svg_safe(title)}</text>',
        f'<line x1="36" y1="80" x2="{width - 36}" y2="80" stroke="{divider}" stroke-width="1"/>',
    ]

    for index, item in enumerate(items[:2]):
        x = panel_x + index * (panel_w + panel_gap)
        accent = item.get("accent", "#2563eb")
        label = svg_safe(item.get("label", ""))
        value = svg_safe(item.get("value", ""))
        suffix = svg_safe(item.get("suffix", ""))
        note = svg_safe(item.get("note", ""))

        svg.extend(
            [
                f'<rect x="{x}" y="{panel_y}" width="{panel_w}" height="{panel_h}" rx="14" fill="{panel_bg}" stroke="{border}" stroke-width="1.5"/>',
                f'<rect x="{x}" y="{panel_y}" width="8" height="{panel_h}" rx="8" fill="{accent}"/>',
                f'<text x="{x + 28}" y="{panel_y + 34}" fill="{muted}" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="600">{label}</text>',
                f'<text x="{x + 28}" y="{panel_y + 76}" fill="{text}" font-family="Segoe UI, Arial, sans-serif" font-size="39" font-weight="700">{value}</text>',
                f'<text x="{x + 28}" y="{panel_y + 106}" fill="{text}" font-family="Segoe UI, Arial, sans-serif" font-size="18" font-weight="600">{suffix}</text>',
                f'<line x1="{x + 28}" y1="{divider_y}" x2="{x + panel_w - 28}" y2="{divider_y}" stroke="{divider}" stroke-width="1"/>',
                f'<text x="{x + 28}" y="{note_y}" fill="{muted}" font-family="Segoe UI, Arial, sans-serif" font-size="13">{note}</text>',
            ]
        )

    svg.append("</svg>")
    return "".join(svg)


def main() -> None:
    data = load_data()
    username = data.get("username")
    if not isinstance(username, str) or not username.strip():
        raise SystemExit("github_stats.json is missing a valid 'username'.")

    today = datetime.now(UTC).date()
    current_month_start, _ = month_bounds(today.year, today.month)
    previous_month_year = today.year - 1 if today.month == 1 else today.year
    previous_month_month = 12 if today.month == 1 else today.month - 1
    previous_month_start, previous_month_end = month_bounds(previous_month_year, previous_month_month)

    current_year_start, _ = year_bounds(today.year, today)
    previous_year_start, previous_year_end = year_bounds(today.year - 1)

    current_month_commits = commit_total(username, current_month_start, today)
    previous_month_commits = commit_total(username, previous_month_start, previous_month_end)
    current_year_commits = commit_total(username, current_year_start, today)
    previous_year_commits = commit_total(username, previous_year_start, previous_year_end)

    monthly_svg = create_two_panel_banner(
        "Monthly Commit Window",
        [
            {
                "label": previous_month_start.strftime("%B %Y"),
                "value": str(previous_month_commits),
                "suffix": "commits",
                "note": "Previous month activity",
                "accent": "#14b8a6",
            },
            {
                "label": current_month_start.strftime("%B %Y"),
                "value": str(current_month_commits),
                "suffix": "commits",
                "note": "Current month so far",
                "accent": "#3b82f6",
            },
        ],
    )
    yearly_svg = create_two_panel_banner(
        "Two-Year Commit View",
        [
            {
                "label": str(previous_year_start.year),
                "value": str(previous_year_commits),
                "suffix": "commits",
                "note": "Previous full year",
                "accent": "#8b5cf6",
            },
            {
                "label": str(current_year_start.year),
                "value": str(current_year_commits),
                "suffix": "commits",
                "note": "Current year so far",
                "accent": "#fb923c",
            },
        ],
    )

    write_svg(MONTHLY_BANNER, monthly_svg)
    write_svg(YEARLY_BANNER, yearly_svg)

    data["monthly_banner"] = str(MONTHLY_BANNER.relative_to(ROOT)).replace("\\", "/")
    data["yearly_history_banner"] = str(YEARLY_BANNER.relative_to(ROOT)).replace("\\", "/")
    save_data(data)

    print(
        "Updated banners: "
        f"{previous_month_start.strftime('%B %Y')}={previous_month_commits}, "
        f"{current_month_start.strftime('%B %Y')}={current_month_commits}, "
        f"{previous_year_start.year}={previous_year_commits}, "
        f"{current_year_start.year}={current_year_commits}"
    )


if __name__ == "__main__":
    main()
