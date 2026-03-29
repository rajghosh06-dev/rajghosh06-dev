from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SECTIONS_FILE = DATA_DIR / "sections.json"
KNOWN_RENDERERS = {
    "profile",
    "what_i_do",
    "tech_stack",
    "projects",
    "achievements",
    "current_goals",
    "contact",
    "badges",
    "about",
    "expertise",
    "github_summary",
    "github_stats",
    "featured_project",
    "generic",
}
RENDERER_PROMPT = (
    "Choose renderer "
    "(profile, about, expertise, what_i_do, tech_stack, projects, achievements, "
    "current_goals, github_stats, github_summary, badges, contact, generic)"
)


def load_json_file(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json_file(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_sections() -> list[dict[str, Any]]:
    sections = load_json_file(SECTIONS_FILE)
    if sections is not None:
        return sections
    return []


def ask(prompt: str, default: str | None = None) -> str:
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    answer = input(prompt).strip()
    return answer or (default or "")


def confirm(prompt: str, default: bool = False) -> bool:
    default_label = "Y/n" if default else "y/N"
    answer = input(f"{prompt} ({default_label}): ").strip().lower()
    if not answer:
        return default
    return answer.startswith("y")


def ask_int(prompt: str, default: int) -> int:
    answer = ask(prompt, str(default))
    try:
        return int(answer)
    except ValueError:
        print(f"Invalid number: {answer}")
        sys.exit(1)


def slugify(value: str) -> str:
    return "_".join(value.strip().lower().split())


def choose_placement(sections: list[dict[str, Any]]) -> int:
    if not sections:
        return 0
    print("Where should the new section appear?")
    print("1) Top")
    print("2) Bottom")
    print("3) After an existing section")
    choice = ask("Choose 1, 2, or 3", "2")
    if choice == "1":
        return 0
    if choice == "3":
        for index, section in enumerate(sections, start=1):
            print(f"{index}) {section['title']} ({section['id']})")
        after_index = ask_int("Enter the number to insert after", 1)
        return min(max(after_index, 0), len(sections))
    return len(sections)


def build_stub(renderer: str) -> Any:
    if renderer == "profile":
        return {
            "name": "Your Name",
            "greeting": "Hi, I'm",
            "subtitle": "Your role or tagline",
            "typing_lines": [
                "A short animated headline",
                "Another line about what you build"
            ],
            "intro": "Short introduction text.",
            "profile_points": [
                "A short point about how you build",
                "Another point about your focus"
            ],
            "hero_badges": [
                "<img src=\"https://img.shields.io/badge/Focus-Clean%20Architecture-f97316?style=for-the-badge\" alt=\"Focus\" />"
            ],
            "cta_links": [
                {
                    "label": "LinkedIn",
                    "message": "Connect",
                    "url": "https://linkedin.com/in/you",
                    "color": "0A66C2",
                    "logo": "linkedin"
                }
            ],
            "terminal_lines": [
                "you@github:~$ focus",
                "What you are building right now"
            ],
            "location": "City",
            "education": "Education details",
            "quote": "A short personal quote."
        }
    if renderer == "what_i_do":
        return [
            {
                "emoji": "⚡",
                "title": "Example skill",
                "description": "A short description."
            }
        ]
    if renderer == "tech_stack":
        return {
            "languages": ["Python", "Java"],
            "frameworks": ["Flask"],
            "tools": ["Git", "VS Code"],
            "specialties": ["Modularity", "Debugging"]
        }
    if renderer == "projects":
        return [
            {
                "name": "Project Name",
                "url": "https://github.com/your/project",
                "description": "A short project description.",
                "stack": ["Python", "Flask"]
            }
        ]
    if renderer == "achievements":
        return {
            "badges": [
                {
                    "title": "Achievement Title",
                    "url": "https://example.com",
                    "image": "https://example.com/image.png",
                    "description": "A short achievement description."
                }
            ]
        }
    if renderer == "badges":
        return {
            "badges": [
                "![Followers](https://img.shields.io/github/followers/rajghosh06-dev?label=Followers&style=social)",
                "![Stars](https://img.shields.io/github/stars/rajghosh06-dev?style=social)",
                "![Profile Views](https://komarev.com/ghpvc/?username=rajghosh06-dev&color=blue)"
            ]
        }
    if renderer == "about":
        return [
            "Start with a short high-level introduction.",
            "Add a sentence about what you build and how you think.",
            "Keep it concise and personal."
        ]
    if renderer == "expertise":
        return [
            {
                "name": "Software Architecture",
                "description": "Design modular systems with clear separation of concerns."
            },
            {
                "name": "AI/ML Workflows",
                "description": "Build reliable preprocessing, evaluation, and deployment pipelines."
            },
            {
                "name": "Developer Productivity",
                "description": "Create tooling and automation for collaborative engineering."
            }
        ]
    if renderer == "github_summary":
        return {
            "joined": "Aug 2024",
            "years_active": "2 years",
            "repositories": 18,
            "stars": 42,
            "followers": 24
        }
    if renderer == "github_stats":
        return {
            "title": "GitHub Pulse",
            "subtitle": "A quick look at the repositories, languages, and contribution patterns behind my profile.",
            "username": "your-github-username",
            "show_summary_card": True,
            "summary_card_title": "This Year on GitHub",
            "summary_card_size": "default",
            "summary_card_hide": [
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
                "followers"
            ],
            "monthly_banner": "assets/github-pulse-monthly.svg",
            "yearly_history_banner": "assets/github-pulse-yearly.svg",
            "badges": [
                "<img src=\"https://img.shields.io/github/followers/your-github-username?style=for-the-badge&logo=github&label=Followers&color=2563eb\" alt=\"Followers\" />",
                "<img src=\"https://img.shields.io/badge/Public%20Repos-18-7c3aed?style=for-the-badge&logo=github&logoColor=white\" alt=\"Public Repos\" />"
            ]
        }
    if renderer == "featured_project":
        return {
            "name": "Featured Project Name",
            "url": "https://github.com/your/project",
            "description": "A short description of your featured project.",
            "stack": [
                "Python",
                "Flask"
            ],
            "highlights": [
                "Why this project stands out",
                "Key technical achievement",
                "Impact or outcome"
            ]
        }
    if renderer == "current_goals":
        return [
            "A new goal to achieve",
            "Another goal"
        ]
    if renderer == "contact":
        return {
            "email": "you@example.com",
            "linkedin": "https://linkedin.com/in/you",
            "portfolio": "https://your-portfolio.example.com",
            "discord": "https://discord.com/users/yourid",
            "twitter": "https://x.com/yourhandle"
        }
    return ["Enter one item per line."]


def create_section() -> None:
    ensure_data_dir()
    sections = load_sections()

    section_id = ask("Enter a short section ID (example: achievements)").strip()
    if not section_id:
        print("Section ID cannot be empty.")
        sys.exit(1)

    section_id = slugify(section_id)
    filename = f"{section_id}.json"
    section_file = DATA_DIR / filename

    if section_file.exists():
        if not confirm(f"{filename} already exists. Overwrite?"):
            print("Canceled.")
            return

    title = ask("Enter the section title", section_id.replace("_", " ").title())
    renderer = ask(RENDERER_PROMPT, "generic")
    if renderer not in KNOWN_RENDERERS:
        print(f"Unknown renderer: {renderer}")
        sys.exit(1)

    stub = build_stub(renderer)
    save_json_file(section_file, stub)

    insert_at = choose_placement(sections)
    sections.insert(insert_at, {
        "id": section_id,
        "filename": filename,
        "title": title,
        "renderer": renderer,
    })
    save_json_file(SECTIONS_FILE, sections)
    print(f"Created {filename} and added section '{title}' at position {insert_at + 1}.")

    if confirm("Generate README.md now?", True):
        run_generator()


def remove_section() -> None:
    sections = load_sections()
    if not sections:
        print("No sections configured in sections.json.")
        return

    for index, section in enumerate(sections, start=1):
        print(f"{index}) {section['title']} ({section['id']})")

    selection = ask_int("Enter the number of the section to remove", 1)
    if selection < 1 or selection > len(sections):
        print("Invalid selection.")
        return

    section = sections.pop(selection - 1)
    save_json_file(SECTIONS_FILE, sections)
    print(f"Removed section '{section['title']}' from ordering.")

    section_file = DATA_DIR / section["filename"]
    if section_file.exists() and confirm(f"Delete {section['filename']} from disk?", False):
        section_file.unlink()
        print(f"Deleted {section['filename']}")

    if confirm("Generate README.md now?", True):
        run_generator()


def list_sections() -> None:
    sections = load_sections()
    if not sections:
        print("No sections configured in sections.json.")
        return
    print("Current section order:")
    for index, section in enumerate(sections, start=1):
        print(f"{index}. {section['title']} ({section['id']}) -> {section['filename']}")


def audit_sections() -> None:
    ensure_data_dir()
    sections = load_sections()
    if not sections:
        print("No sections configured in sections.json.")
        return

    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    issues: list[str] = []

    for section in sections:
        section_id = section.get("id", "")
        filename = section.get("filename", "")
        renderer = section.get("renderer", "generic")

        if section_id in seen_ids:
            issues.append(f"Duplicate section id: {section_id}")
        seen_ids.add(section_id)

        if filename in seen_files:
            issues.append(f"Duplicate filename reference: {filename}")
        seen_files.add(filename)

        if renderer not in KNOWN_RENDERERS:
            issues.append(f"Unknown renderer '{renderer}' in section '{section_id}'")

        path = DATA_DIR / filename
        if not path.exists():
            issues.append(f"Missing data file: {filename}")
            continue
        try:
            load_json_file(path)
        except json.JSONDecodeError as exc:
            issues.append(f"Invalid JSON in {filename}: {exc}")

    unreferenced = sorted(
        path.name
        for path in DATA_DIR.glob("*.json")
        if path.name not in seen_files and path.name != SECTIONS_FILE.name
    )

    if issues:
        print("Audit found issues:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("Audit passed: section config and referenced JSON files are valid.")

    if unreferenced:
        print("Unreferenced data files:")
        for filename in unreferenced:
            print(f"- {filename}")


def run_generator() -> None:
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "generate_readme.py")], check=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or remove data-driven README sections.")
    parser.add_argument("action", choices=["create", "remove", "list", "audit"], help="Action to perform")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.action == "create":
        create_section()
    elif args.action == "remove":
        remove_section()
    elif args.action == "audit":
        audit_sections()
    else:
        list_sections()


if __name__ == "__main__":
    main()
