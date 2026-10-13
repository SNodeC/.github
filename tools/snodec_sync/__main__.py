"""Offline catalog validation and deterministic organization-profile rendering."""
import argparse
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parents[2]
AREAS = {
    "framework": "Framework",
    "suites": "Suites",
    "applications": "Applications",
    "learn": "Learn",
    "community": "Community projects",
    "infrastructure": "Distribution & infrastructure",
    "forks": "Upstream forks",
}
KINDS = {"product", "app", "example", "learning", "community", "infra", "fork"}
REQUIRED = {"name", "area", "kind", "summary", "depends_on", "status"}
OPTIONAL = {"packaged", "site", "pinned", "accent", "note", "upstream", "confirm", "tier", "title", "purpose", "student"}
NAME = re.compile(r"[A-Za-z0-9_.-]+")
UPSTREAM = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9_.-]+")


def validate(catalog):
    """Return all errors, without suppressing later entries after a failure."""
    errors = []
    if not isinstance(catalog, list):
        return ["catalog must be a list"]
    names = set()
    for index, entry in enumerate(catalog):
        label = f"entry {index + 1}"
        if not isinstance(entry, dict):
            errors.append(f"{label}: must be a mapping")
            continue
        for key in sorted(REQUIRED - entry.keys()):
            errors.append(f"{label}: missing {key}")
        for key in sorted(entry.keys() - REQUIRED - OPTIONAL, key=str):
            errors.append(f"{label}: unknown identity field {key}")
        name = entry.get("name")
        if not isinstance(name, str) or not NAME.fullmatch(name):
            errors.append(f"{label}: invalid name")
        elif name in names:
            errors.append(f"{label}: duplicate name {name}")
        else:
            names.add(name)
        for key, choices in [("area", AREAS), ("kind", KINDS),
                             ("status", {"active", "retiring", "retired"})]:
            if not isinstance(entry.get(key), str) or entry[key] not in choices:
                errors.append(f"{label}: unknown {key}")
        for key in ["summary", "accent", "note", "upstream", "title", "purpose"]:
            if key in entry and (not isinstance(entry[key], str)
                                 or not entry[key].strip()
                                 or any(c in entry[key] for c in "\r\n")):
                errors.append(f"{label}: {key} must be non-empty, single-line text")
        for key in ["packaged", "site", "pinned", "confirm", "student"]:
            if key in entry and type(entry[key]) is not bool:
                errors.append(f"{label}: {key} must be a boolean")
        tier = entry.get("tier", "secondary")
        if not isinstance(tier, str) or tier not in {"product", "learn", "install", "secondary"}:
            errors.append(f"{label}: unknown tier")
        if tier == "product":
            if entry.get("kind") not in ("product", "app"):
                errors.append(f"{label}: product tier requires product or app kind")
            for key in ("title", "purpose"):
                if key not in entry:
                    errors.append(f"{label}: product tier requires {key}")
        if tier == "secondary" and entry.get("kind") == "product" and entry.get("student") is not True:
            errors.append(f"{label}: secondary products require student: true")
        if "accent" in entry and entry.get("kind") != "product":
            errors.append(f"{label}: accent is allowed only on products")
        if entry.get("kind") == "fork":
            if not isinstance(entry.get("upstream"), str) or not UPSTREAM.fullmatch(entry["upstream"]):
                errors.append(f"{label}: forks require upstream owner/repo")
            if entry.get("status") != "active":
                errors.append(f"{label}: upstream forks must stay active")
        deps = entry.get("depends_on")
        if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
            errors.append(f"{label}: depends_on must be a list of names")
    for index, entry in enumerate(catalog):
        if isinstance(entry, dict) and isinstance(entry.get("depends_on"), list):
            for dep in entry["depends_on"]:
                if isinstance(dep, str) and dep not in names:
                    errors.append(f"entry {index + 1}: unknown dependency {dep}")
    return errors


def text(value):
    """Escape authored text for Markdown table cells; never interpret HTML."""
    value = html.escape(value, quote=False)
    return re.sub(r"([\\|\[\]*_`])", r"\\\1", value)


def repo_url(name, fragment=""):
    return f"https://github.com/SNodeC/{quote(name, safe='')}" + (f"#{quote(fragment, safe='')}" if fragment else "")


def render_profile(catalog, metadata, template=None):
    errors = validate(catalog)
    if errors:
        raise ValueError("\n".join(errors))
    template = (ROOT / "profile/template.md").read_text() if template is None else template
    products = ["| Project | What it is for | Status |", "| --- | --- | --- |"]
    learn = ["| Project | Purpose |", "| --- | --- |"]
    groups = {title: [] for title in ("Examples", "Student projects", "Standalone applications",
                                     "Infrastructure", "Upstream forks", "Archive")}
    for entry in catalog:
        name, tier = entry["name"], entry.get("tier", "secondary")
        info, url = metadata.get(name, {}), repo_url(name)
        if tier == "product":
            anchor = info.get("readme_anchor", "")
            links = [f"[Quick start]({url}#quick-start)", f"[Install]({url}#install)"] if anchor else []
            if info.get("release"):
                links.append(f"[Releases]({url}/releases)")
            purpose = text(entry["purpose"]) + ("<br>" + " · ".join(links) if links else "")
            badge = ""
            if info.get("workflow"):
                workflow = f"{url}/actions/workflows/{quote(Path(info['workflow']).name, safe='')}"
                branch = quote(info["default_branch"], safe="")
                badge = f"[![CI]({workflow}/badge.svg?branch={branch})]({workflow})"
            products.append(f"| **[{text(entry['title'])}]({repo_url(name, anchor)})** | {purpose} | {badge} |")
        elif tier == "learn":
            learn.append(f"| **[{text(entry.get('title', name))}]({url})** | {text(entry['summary'])} |")
        if tier != "secondary" and entry.get("student") is not True:
            continue
        group = ("Archive" if entry["status"] != "active" else "Student projects"
                 if entry["kind"] == "community" or entry.get("student") is True else
                 {"example": "Examples", "app": "Standalone applications", "infra": "Infrastructure",
                  "fork": "Upstream forks"}.get(entry["kind"]))
        if group:
            purpose = (f"[{text(entry['upstream'])}](https://github.com/{entry['upstream']})"
                       if group == "Upstream forks" else text(entry["summary"]))
            if group == "Archive":
                purpose += f" · {entry['status']}"
            groups[group].append(f"| [{text(name)}]({url}) | {purpose} |")
    summaries = ["small programs built on SNode.C", "built in courses and projects", "not built on SNode.C",
                 "package pipeline and organization control", "kept for future work", "retiring and retired"]
    more = []
    for (title, rows), summary in zip(groups.items(), summaries):
        if rows:
            purpose = "Upstream" if title == "Upstream forks" else "Purpose"
            more.append("\n".join(["<details>", f"<summary><b>{title}</b> — {summary}</summary>", "",
                                   f"| Project | {purpose} |", "| --- | --- |", *rows, "", "</details>"]))
    for marker, replacement in [("products", "\n".join(products)), ("learn", "\n".join(learn)),
                                ("more", "\n\n".join(more))]:
        token = f"<!-- profile:{marker} -->"
        if template.count(token) != 1 or template.splitlines().count(token) != 1:
            raise ValueError(f"Template requires exactly one standalone {token}")
        template = template.replace(token, replacement)
    branch = quote(metadata[".github"]["default_branch"], safe="")
    template = template.replace(f"{repo_url('.github')}/blob/main/", f"{repo_url('.github')}/blob/{branch}/")
    return ("<!-- Generated by tools/snodec_sync profile from catalog.yml and profile/template.md; edit those, not this file. -->\n"
            + template.split("\n", 1)[1].rstrip() + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "profile", "page-headers", "docs-audit"])
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--check", action="store_true", help="report header/asset drift without writing")
    parser.add_argument("--catalog", type=Path, default=ROOT / "catalog.yml")
    parser.add_argument("--metadata", type=Path, default=ROOT / "profile/github-metadata.json")
    parser.add_argument("--output", type=Path, default=ROOT / "profile/README.md")
    args = parser.parse_args(argv)
    try:
        if args.command == "docs-audit":
            if args.repo is None:
                raise ValueError("docs-audit requires --repo <checkout>")
            sys.path.insert(0, str(ROOT / "tools"))
            from snodec_sync.docs_audit import docs_audit
            information = []
            errors = docs_audit(args.repo, information=information)
            for line in information:
                print(line)
            if errors:
                raise ValueError("\n".join(errors))
            print("docs-audit: 0 violations")
            return 0
        if args.command == "page-headers":
            if args.repo is None:
                raise ValueError("page-headers requires --repo <checkout>")
            sys.path.insert(0, str(ROOT / "tools"))
            from snodec_sync.navigation import page_headers
            drift = page_headers(args.repo, check=args.check)
            if args.check and drift:
                raise ValueError("page-header drift:\n" + "\n".join(drift))
            return 0
        catalog = yaml.safe_load(args.catalog.read_text(encoding="utf-8"))
        if args.command == "check":
            errors = validate(catalog)
            if errors:
                raise ValueError("\n".join(errors))
        else:
            metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
            args.output.write_text(render_profile(catalog, metadata), encoding="utf-8")
    except (OSError, ValueError, KeyError, yaml.YAMLError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
