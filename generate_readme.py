from __future__ import annotations

import json
import urllib.parse
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SECTIONS_FILE = DATA_DIR / "sections.json"
OUTPUT_FILE = ROOT / "README.md"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


ICON_MAP = {
    "C": "c",
    "Python": "python",
    "Java": "java",
    "SQL": "sql",
    "HTML": "html5",
    "AWT": "java",
    "Flask": "flask",
    "Maven": "maven",
    "PyCharm": "pycharm",
    "IntelliJ": "intellij",
    "Jupyter": "jupyter",
    "Git": "git",
    "VS Code": "vscode",
    "Eclipse": "eclipse",
    "Dev C++": "cplusplus"
}


def load_sections() -> list[dict[str, Any]]:
    if SECTIONS_FILE.exists():
        return load_json(SECTIONS_FILE)
    return [
        {"id": "profile", "filename": "profile.json", "title": "Profile", "renderer": "profile"},
        {"id": "about", "filename": "about.json", "title": "About Me", "renderer": "about"},
        {"id": "current_goals", "filename": "current_goals.json", "title": "Current Sprint", "renderer": "current_goals"},
        {"id": "featured_project", "filename": "featured_project.json", "title": "Spotlight Project", "renderer": "featured_project"},
        {"id": "github_stats", "filename": "github_stats.json", "title": "GitHub Pulse", "renderer": "github_stats"},
        {"id": "expertise", "filename": "expertise.json", "title": "Strengths", "renderer": "expertise"},
        {"id": "what_i_do", "filename": "what_i_do.json", "title": "How I Work", "renderer": "what_i_do"},
        {"id": "tech_stack", "filename": "tech_stack.json", "title": "Tech Stack & Tools", "renderer": "tech_stack"},
        {"id": "projects", "filename": "projects.json", "title": "Featured Builds", "renderer": "projects"},
        {"id": "achievements", "filename": "achievements.json", "title": "Open Source Moments", "renderer": "achievements"},
    ]


def icon_url(name: str) -> str:
    slug = ICON_MAP.get(name, name.lower().replace(" ", "").replace("++", "plusplus"))
    return f"https://raw.githubusercontent.com/devicons/devicon/master/icons/{slug}/{slug}-original.svg"


def shields_badge_url(
    label: str,
    message: str,
    color: str = "2f80ed",
    style: str = "for-the-badge",
    logo: str | None = None,
    logo_color: str = "white",
) -> str:
    label_slug = urllib.parse.quote(label)
    message_slug = urllib.parse.quote(message)
    url = f"https://img.shields.io/badge/{label_slug}-{message_slug}-{color}?style={style}"
    if logo:
        url += f"&logo={urllib.parse.quote(logo)}&logoColor={urllib.parse.quote(logo_color)}"
    return url


def render_link_badges(links: list[dict[str, str]]) -> str:
    badges = []
    for link in links:
        label = link.get("label")
        message = link.get("message", "Open")
        url = link.get("url")
        if not label or not url:
            continue
        badge = shields_badge_url(
            label,
            message,
            color=link.get("color", "2f80ed"),
            logo=link.get("logo"),
            logo_color=link.get("logo_color", "white"),
        )
        badges.append(f"<a href=\"{url}\" target=\"_blank\"><img src=\"{badge}\" alt=\"{label}\" /></a>")
    return " ".join(badges)


def render_image(path: str, alt: str) -> str:
    return f"<img src=\"{path}\" alt=\"{alt}\" />"


def typing_svg_url(lines: list[str]) -> str:
    params = urllib.parse.urlencode(
        {
            "font": "JetBrains Mono",
            "weight": 600,
            "size": 22,
            "duration": 2800,
            "pause": 900,
            "color": "2563EB",
            "center": "true",
            "vCenter": "true",
            "repeat": "true",
            "width": 700,
            "lines": lines,
        },
        doseq=True,
    )
    return f"https://readme-typing-svg.demolab.com?{params}"


def render_stack_badges(items: list[str]) -> str:
    return " ".join(f"`{item}`" for item in items)


def render_icon_table(items: list[str]) -> str:
    cells = []
    for item in items:
        url = icon_url(item)
        cells.append(
            f"<td align=\"center\" width=\"120\">\n"
            f"  <img src=\"{url}\" width=64 height=64 alt=\"{item}\" />\n"
            f"  <br>{item}\n"
            f"</td>"
        )
    rows = []
    for i in range(0, len(cells), 5):
        rows.append("<tr>" + "".join(cells[i:i+5]) + "</tr>")
    return "<table><tbody>" + "".join(rows) + "</tbody></table>\n"


def render_profile(profile: dict[str, Any]) -> str:
    greeting = profile.get("greeting", "Hi, I'm")
    lines = ["<div align=\"center\">", ""]
    lines.append(f"<h1>{greeting} {profile['name']}</h1>")
    lines.append("")
    subtitle = profile.get("subtitle")
    if subtitle:
        lines.append(f"<p><strong>{subtitle}</strong></p>")
        lines.append("")
    typing_lines = profile.get("typing_lines")
    if isinstance(typing_lines, list) and typing_lines:
        lines.append(f"<img src=\"{typing_svg_url(typing_lines)}\" alt=\"Typing SVG\" />")
        lines.append("")
        lines.append("<br />")
        lines.append("")
    intro = profile.get("intro")
    if intro:
        lines.append(f"<p>{intro}</p>")
        lines.append("")
        lines.append("<br />")
        lines.append("")
    cta_links = profile.get("cta_links")
    if isinstance(cta_links, list) and cta_links:
        lines.append(render_link_badges(cta_links))
        lines.append("")
        lines.append("<br />")
        lines.append("")
    points = profile.get("profile_points")
    hero_badges = profile.get("hero_badges")
    if isinstance(hero_badges, list) and hero_badges:
        lines.append(" ".join(hero_badges))
        lines.append("")
        lines.append("<br />")
        lines.append("")
    location = profile.get("location")
    education = profile.get("education")
    if location or education:
        details = " · ".join(item for item in [location, education] if item)
        lines.append(f"<p><sub>{details}</sub></p>")
        lines.append("")
    lines.append("</div>")
    lines.append("")
    lines.append("<br />")
    lines.append("")
    terminal_lines = profile.get("terminal_lines")
    if isinstance(terminal_lines, list) and terminal_lines:
        lines.append("```bash")
        lines.extend(terminal_lines)
        lines.append("```")
        lines.append("")
        lines.append("<br />")
        lines.append("")
    if isinstance(points, list) and points:
        lines.extend(f"- {point}" for point in points)
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_about(items: list[str]) -> str:
    lines = ["## About Me", ""]
    for item in items:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_expertise(items: list[dict[str, str]]) -> str:
    lines = ["## Strengths", "", "| Focus Area | What It Looks Like |", "| --- | --- |"]
    for item in items:
        lines.append(f"| **{item['name']}** | {item['description']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_what_i_do(items: list[dict[str, str]]) -> str:
    lines = ["## How I Work", "", "| Approach | In Practice |", "| --- | --- |"]
    for item in items:
        emoji = item.get("emoji", "")
        title = item.get("title", "")
        label = f"{emoji} {title}".strip()
        lines.append(f"| **{label}** | {item['description']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_tech_stack(stack: dict[str, list[str]]) -> str:
    lines = ["## Tech Stack & Tools", "", "### Languages", "", "<div align=\"center\">", ""]
    lines.append(render_icon_table(stack["languages"]))
    lines.append("</div>")
    lines.append("")
    lines.append("### Frameworks")
    lines.append("")
    lines.append("<div align=\"center\">")
    lines.append("")
    lines.append(render_icon_table(stack["frameworks"]))
    lines.append("</div>")
    lines.append("")
    lines.append("### Tools")
    lines.append("")
    lines.append("<div align=\"center\">")
    lines.append("")
    lines.append(render_icon_table(stack["tools"]))
    lines.append("</div>")
    lines.append("")
    specialties = stack.get("specialties", [])
    if specialties:
        lines.append("### What I Optimize For")
        lines.append("")
        lines.extend(f"- {item}" for item in specialties)
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_projects(projects: list[dict[str, str]]) -> str:
    lines = ["## Featured Builds", "", "| Project | Snapshot |", "| --- | --- |"]
    for project in projects:
        details = project["description"]
        stack = project.get("stack")
        if isinstance(stack, list) and stack:
            details += f"<br /><sub>{' • '.join(stack)}</sub>"
        lines.append(f"| [{project['name']}]({project['url']}) | {details} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_featured_project(project: dict[str, Any]) -> str:
    lines = ["## Spotlight Project", "", f"### [{project['name']}]({project['url']})", "", project['description'], ""]
    stack = project.get("stack")
    if isinstance(stack, list) and stack:
        lines.append(render_stack_badges(stack))
        lines.append("")
    highlights = project.get("highlights")
    if isinstance(highlights, list) and highlights:
        lines.append("**Why it stands out:**")
        for highlight in highlights:
            lines.append(f"- {highlight}")
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_achievements(data: dict[str, list[dict[str, str]]]) -> str:
    lines = ["## Open Source Moments", ""]
    for badge in data.get("badges", []):
        width = badge.get("width")
        width_attr = f' width="{width}"' if width else ""
        lines.append("<div align=\"center\">")
        lines.append("")
        lines.append(
            f"<a href=\"{badge['url']}\" target=\"_blank\"><img src=\"{badge['image']}\" alt=\"{badge['title']}\"{width_attr} /></a>"
        )
        lines.append("")
        lines.append("</div>")
        lines.append("")
        lines.append(f"**{badge['title']}** — {badge.get('description', '')}")
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_current_goals(goals: list[str]) -> str:
    lines = ["## Current Sprint", ""]
    for goal in goals:
        lines.append(f"- [ ] {goal}")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_contact(contact: dict[str, str]) -> str:
    lines = ["## Let's Connect", "", "<div align=\"center\">", ""]
    links = []
    if contact.get("portfolio"):
        links.append(
            f"<a href=\"{contact['portfolio']}\" target=\"_blank\"><img src=\"{shields_badge_url('Portfolio', 'Visit', color='111827', logo='googlechrome')}\" alt=\"Portfolio\" /></a>"
        )
    if contact.get("linkedin"):
        links.append(
            f"<a href=\"{contact['linkedin']}\" target=\"_blank\"><img src=\"{shields_badge_url('LinkedIn', 'Connect', color='0A66C2', logo='linkedin')}\" alt=\"LinkedIn\" /></a>"
        )
    if contact.get("email"):
        links.append(
            f"<a href=\"mailto:{contact['email']}\" target=\"_blank\"><img src=\"{shields_badge_url('Email', 'Write to me', color='EA4335', logo='gmail')}\" alt=\"Email\" /></a>"
        )
    if contact.get("discord"):
        links.append(
            f"<a href=\"{contact['discord']}\" target=\"_blank\"><img src=\"{shields_badge_url('Discord', 'Say hi', color='5865F2', logo='discord')}\" alt=\"Discord\" /></a>"
        )
    if contact.get("twitter"):
        links.append(
            f"<a href=\"{contact['twitter']}\" target=\"_blank\"><img src=\"{shields_badge_url('X', 'Follow', color='000000', logo='x')}\" alt=\"X\" /></a>"
        )
    lines.append(" ".join(links))
    lines.append("")
    lines.append("</div>")
    lines.append("")
    lines.append("I enjoy connecting with people who care about thoughtful software, AI/ML experimentation, and well-presented projects.")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_footer(profile: dict[str, str]) -> str:
    return f"> _\"{profile['quote']}\"_\n"


def render_badges(data: dict[str, Any]) -> str:
    lines = ["## Profile Metrics", "", "<div align=\"center\">", ""]
    badges = data.get("badges", [])
    lines.append(" ".join(badges) if isinstance(badges, list) else str(badges))
    lines.append("")
    lines.append("</div>")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_github_summary(data: dict[str, Any]) -> str:
    lines = ["## GitHub Insights", ""]
    joined = data.get("joined")
    years_active = data.get("years_active")
    repositories = data.get("repositories")
    stars = data.get("stars")
    followers = data.get("followers")

    if joined:
        lines.append(f"- Joined GitHub: {joined}")
    if years_active:
        lines.append(f"- Active for: {years_active}")
    if repositories is not None:
        lines.append(f"- Repositories: {repositories}")
    if stars is not None:
        lines.append(f"- Stars received: {stars}")
    if followers is not None:
        lines.append(f"- Followers: {followers}")

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def badge_url(label: str, value: str, color: str = "2f80ed", style: str = "for-the-badge") -> str:
    label_slug = urllib.parse.quote(label.replace(" ", "_"))
    value_slug = urllib.parse.quote(str(value).replace(" ", "_"))
    return f"https://img.shields.io/badge/{label_slug}-{value_slug}-{color}?style={style}"


def render_github_stats(data: dict[str, Any]) -> str:
    title = data.get("title", "GitHub Stats")
    subtitle = data.get("subtitle")
    lines = [f"## {title}", ""]
    if isinstance(subtitle, str) and subtitle.strip():
        lines.append(subtitle)
        lines.append("")
        lines.append("<br />")
        lines.append("")
    badges = data.get("badges")
    if isinstance(badges, list) and badges:
        lines.append("<div align=\"center\">")
        lines.append("")
        lines.extend(badges)
        lines.append("")
        lines.append("</div>")
        lines.append("")
        lines.append("<br />")
        lines.append("")
    username = data.get("username")
    if isinstance(username, str) and username.strip():
        lines.append("<div align=\"center\">")
        lines.append("")
        if data.get("show_summary_card", True):
            hidden_stats = data.get(
                "summary_card_hide",
                [
                    "stars",
                    "prs",
                    "issues",
                    "streak",
                    "week",
                    "trend",
                    "avg",
                    "active_day",
                    "grade",
                    "repos",
                    "followers",
                ],
            )
            hide_param = ",".join(hidden_stats)
            card_size = data.get("summary_card_size", "compact")
            custom_title = data.get("summary_card_title")
            title_param = ""
            if isinstance(custom_title, str) and custom_title.strip():
                title_param = f"&custom_title={urllib.parse.quote(custom_title)}"
            lines.append(
                f"<img src=\"https://ghstats.dev/api/card?username={urllib.parse.quote(username)}&size={urllib.parse.quote(str(card_size))}&hide={urllib.parse.quote(hide_param)}{title_param}\" alt=\"{username} yearly GitHub stats\" />"
            )
            lines.append("")
            lines.append("<br /><br />")
            lines.append("")
        monthly_banner = data.get("monthly_banner")
        if isinstance(monthly_banner, str) and monthly_banner.strip():
            lines.append(render_image(monthly_banner, "Monthly Commit Window"))
            lines.append("")
            lines.append("<br /><br />")
            lines.append("")
        yearly_history_banner = data.get("yearly_history_banner")
        if isinstance(yearly_history_banner, str) and yearly_history_banner.strip():
            lines.append(render_image(yearly_history_banner, "Yearly Commit Snapshot"))
            lines.append("")
            lines.append("<br /><br />")
            lines.append("")
        lines.append(
            f"<img src=\"https://github-readme-activity-graph.vercel.app/graph?username={urllib.parse.quote(username)}&bg_color=ffffff00&color=2563eb&line=0f766e&point=f97316&hide_border=true&area=true\" alt=\"{username} activity graph\" />"
        )
        lines.append("")
        lines.append("</div>")
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_generic_section(section: dict[str, Any], data: Any) -> str:
    title = section.get("title") or section["id"].replace("_", " ").title()
    header = f"## {title}\n\n"

    if isinstance(data, list):
        if all(isinstance(item, str) for item in data):
            return header + "\n".join(f"- {item}  " for item in data) + "\n\n---\n\n"
        if all(isinstance(item, dict) for item in data):
            lines = [header]
            for item in data:
                name = item.get("name") or item.get("title") or item.get("label")
                url = item.get("url")
                description = item.get("description")
                if name and url:
                    lines.append(f"- [{name}]({url})  ")
                    if description:
                        lines.append(f"  {description}")
                elif name:
                    lines.append(f"- **{name}**  ")
                    if description:
                        lines.append(f"  {description}")
                else:
                    lines.append(f"- {json.dumps(item, ensure_ascii=False)}")
            return "\n".join(lines) + "\n\n---\n\n"

    if isinstance(data, dict):
        lines = [header]
        for key, value in data.items():
            label = key.replace("_", " ").title()
            if isinstance(value, list):
                lines.append(f"- **{label}**:")
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"- **{label}**: `{json.dumps(value, ensure_ascii=False)}`  ")
            else:
                lines.append(f"- **{label}**: {value}  ")
        return "\n".join(lines) + "\n\n---\n\n"

    return header + "```json\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n```\n\n---\n\n"


def render_section(section: dict[str, Any], data: Any) -> str:
    renderer = section.get("renderer", "generic")
    if renderer == "profile":
        return render_profile(data)
    if renderer == "badges":
        return render_badges(data)
    if renderer == "github_summary":
        return render_github_summary(data)
    if renderer == "about":
        return render_about(data)
    if renderer == "expertise":
        return render_expertise(data)
    if renderer == "github_stats":
        return render_github_stats(data)
    if renderer == "featured_project":
        return render_featured_project(data)
    if renderer == "what_i_do":
        return render_what_i_do(data)
    if renderer == "tech_stack":
        return render_tech_stack(data)
    if renderer == "projects":
        return render_projects(data)
    if renderer == "achievements":
        return render_achievements(data)
    if renderer == "current_goals":
        return render_current_goals(data)
    if renderer == "contact":
        return render_contact(data)
    return render_generic_section(section, data)


def main() -> None:
    sections = load_sections()
    content = ["<!-- THIS FILE IS GENERATED. Edit files in data/ and run `python generate_readme.py`. -->\n\n"]
    profile_data: dict[str, str] | None = None

    for section in sections:
        path = DATA_DIR / section["filename"]
        if not path.exists():
            print(f"Warning: missing section file {section['filename']}, skipping.")
            continue
        data = load_json(path)
        content.append(render_section(section, data))
        if section.get("renderer") == "profile":
            profile_data = data

    if profile_data:
        content.append(render_footer(profile_data))

    OUTPUT_FILE.write_text("".join(content), encoding="utf-8")
    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
