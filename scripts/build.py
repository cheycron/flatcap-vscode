#!/usr/bin/env python3
"""Generate the Flatcap 2.0 themes for Visual Studio Code.

    python3 scripts/build.py              # write the themes, package.json fields and README blocks
    python3 scripts/build.py --check      # fail if any generated output is stale (also runs the contrast gate)
    python3 scripts/build.py --sync       # refresh src/theme.json from ../00-Flatcap, then rebuild
    python3 scripts/build.py --contrast   # print the full contrast report (editor, workbench, overlays, ANSI)

Input  : src/theme.json, a versioned copy of the Flatcap 2.0 core (the only source of values).
         scripts/mapping.py, the role mapping (roles only, no hex).
Outputs: themes/flatcap-slate.theme.json      Flatcap Slate  (vs-dark)
         themes/flatcap-daylight.theme.json   Flatcap Daylight  (vs)
         themes/flatcap-legacy.theme.json     the v1 name "Flatcap", an alias of Slate (see README)
         package.json                         only version, galleryBanner and contributes.themes
         README.md                            only the blocks between <!-- build:NAME --> markers
         docs/mapping.md                      same markers: full role mapping and syntax tables (not in the VSIX)

No hex value is written by hand: every color is a Flatcap role, optionally with an alpha percentage.
Python 3.10+, standard library only. Output is deterministic.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapping as M  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "src" / "theme.json"
README = ROOT / "README.md"
MAPPING_DOC = ROOT / "docs" / "mapping.md"
PACKAGE = ROOT / "package.json"
THEMES_DIR = ROOT / "themes"
UPSTREAM = (ROOT / ".." / "00-Flatcap" / "src" / "theme.json").resolve()

MODES = ("slate", "daylight")
NAME = {"slate": "Flatcap Slate", "daylight": "Flatcap Daylight"}
TYPE = {"slate": "dark", "daylight": "light"}
UI_THEME = {"slate": "vs-dark", "daylight": "vs"}
FILE = {"slate": "flatcap-slate.theme.json", "daylight": "flatcap-daylight.theme.json"}
LEGACY_ID = "Flatcap"                       # what v1 users have in workbench.colorTheme
LEGACY_LABEL = "Flatcap (v1 name, now Slate)"
LEGACY_FILE = "flatcap-legacy.theme.json"
TRANSPARENT = "#00000000"                   # "no color", not a palette value

HEX6 = re.compile(r"^#[0-9A-Fa-f]{6}$")
SPEC = re.compile(r"^(?P<role>[a-z0-9.]+)(?:/(?P<a>\d{1,3}))?$")


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------
def load() -> dict:
    return json.loads(THEME.read_text(encoding="utf-8"))


def shadow_hex(theme: dict, mode: str) -> str:
    m = re.search(r"rgb\((\d+) (\d+) (\d+) / (\d+)%\)", theme["elevation"][mode]["shadow.overlay"])
    if not m:
        raise SystemExit("error: cannot parse elevation shadow.overlay")
    r, g, b, a = (int(x) for x in m.groups())
    return f"#{r:02X}{g:02X}{b:02X}{round(a * 255 / 100):02X}"


def resolve(theme: dict, mode: str, spec: str) -> str:
    if spec == "transparent":
        return TRANSPARENT
    if spec == "shadow":
        return shadow_hex(theme, mode)
    m = SPEC.match(spec)
    if not m:
        raise SystemExit(f"error: bad color spec {spec!r}")
    role = m["role"]
    value = theme["themes"][mode].get(role)
    if value is None:
        raise SystemExit(f"error: unknown Flatcap role {role!r} in spec {spec!r}")
    if m["a"] is None:
        return value
    pct = int(m["a"])
    if not 0 < pct < 100:
        raise SystemExit(f"error: alpha out of range in {spec!r}")
    return f"{value}{round(pct * 255 / 100):02X}"


def ansi_role(mode: str, key: str) -> str:
    for k, _i, s, d in M.ANSI:
        if k == key:
            return s if mode == "slate" else d
    raise KeyError(key)


def workbench_colors(theme: dict, mode: str) -> dict[str, str]:
    out: dict[str, str] = {}
    owner: dict[str, str] = {}
    for group, entries in M.WORKBENCH:
        for spec, keys in entries:
            for key in keys:
                if key in out:
                    raise SystemExit(f"error: color key {key!r} assigned twice ({owner[key]} and {group})")
                out[key] = resolve(theme, mode, spec)
                owner[key] = group
    for key, _i, _s, _d in M.ANSI:
        out["terminal." + key] = resolve(theme, mode, ansi_role(mode, key))
    return out


def token_colors(theme: dict, mode: str) -> list[dict]:
    rules = []
    for name, scopes, role, font in M.TOKENS:
        settings = {"foreground": resolve(theme, mode, role)}
        if font is not None:
            settings["fontStyle"] = font
        rules.append({"name": name, "scope": scopes, "settings": settings})
    return rules


def semantic_colors(theme: dict, mode: str) -> dict:
    out: dict = {}
    for selector, role, font in M.SEMANTIC:
        if role is None:
            out[selector] = {k: True for k in font.split()}
        elif font is None:
            out[selector] = resolve(theme, mode, role)
        else:
            out[selector] = {"foreground": resolve(theme, mode, role), **{k: True for k in font.split()}}
    return out


def theme_file(theme: dict, mode: str, name: str | None = None) -> dict:
    return {
        "$schema": "vscode://schemas/color-theme",
        "name": name or NAME[mode],
        "type": TYPE[mode],
        "semanticHighlighting": True,
        "colors": workbench_colors(theme, mode),
        "tokenColors": token_colors(theme, mode),
        "semanticTokenColors": semantic_colors(theme, mode),
    }


def dumps(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def package_json(theme: dict) -> dict:
    pkg = json.loads(PACKAGE.read_text(encoding="utf-8"))
    pkg["version"] = theme["version"]
    pkg["galleryBanner"] = {"color": theme["themes"]["slate"]["bg.canvas"], "theme": "dark"}
    pkg.setdefault("contributes", {})["themes"] = [
        {"label": NAME[m], "uiTheme": UI_THEME[m], "path": f"./themes/{FILE[m]}"} for m in MODES
    ] + [{"id": LEGACY_ID, "label": LEGACY_LABEL, "uiTheme": UI_THEME["slate"], "path": f"./themes/{LEGACY_FILE}"}]
    return pkg


# ---------------------------------------------------------------------------
# Contrast
# ---------------------------------------------------------------------------
def rgba(h: str) -> tuple[float, float, float, float]:
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
    return r, g, b, a


def over(top: str, base: str) -> str:
    r, g, b, a = rgba(top)
    br, bg_, bb, _ = rgba(base)
    mix = (round(r * a + br * (1 - a)), round(g * a + bg_ * (1 - a)), round(b * a + bb * (1 - a)))
    return "#{:02X}{:02X}{:02X}".format(*mix)


def lum(h: str) -> float:
    c = [v / 255 for v in rgba(h)[:3]]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a: str, b: str) -> float:
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


class Ctx:
    """Resolves 'k:workbench.key' and 'r:role' references to opaque hex, compositing alpha over a base."""

    def __init__(self, theme: dict, mode: str):
        self.theme, self.mode = theme, mode
        self.colors = workbench_colors(theme, mode)

    def get(self, ref: str, base: str | None = None) -> str:
        kind, _, name = ref.partition(":")
        raw = self.colors[name] if kind == "k" else self.theme["themes"][self.mode][name]
        if len(raw) == 9:
            raw = over(raw, base or self.get("k:editor.background"))
        return raw


# (group, label, foreground ref, background ref, target, background composited over)
SYNTAX = ("keyword", "function", "string", "number", "type", "comment")
EDITOR_BG = "k:editor.background"


def checks(theme: dict, mode: str) -> list[dict]:
    c = Ctx(theme, mode)
    rows: list[dict] = []

    def add(group, label, fg, bg, target, base=None, fg_base=None):
        b = c.get(bg, c.get(base) if base else None)
        f = c.get(fg, b)
        rows.append({"group": group, "label": label, "fg": f, "bg": b, "target": target, "ratio": ratio(f, b)})

    for role in ("text.primary",):
        add("Editor", "editor text on editor background", "k:editor.foreground", EDITOR_BG, 7)
    for s in SYNTAX:
        add("Syntax on canvas", f"syntax.{s}", f"r:syntax.{s}", EDITOR_BG, 5)
    add("Syntax on canvas", "text.secondary (separators, brackets)", "r:text.secondary", EDITOR_BG, 5)
    overlays = [
        ("current line", "k:editor.lineHighlightBackground", 5),
        ("text selection", "k:editor.selectionBackground", 0),
        ("inactive selection", "k:editor.inactiveSelectionBackground", 4.5),
        ("selection occurrences", "k:editor.selectionHighlightBackground", 4.5),
        ("current find match", "k:editor.findMatchBackground", 4.5),
        ("other find matches", "k:editor.findMatchHighlightBackground", 4.5),
        ("word highlight", "k:editor.wordHighlightBackground", 4.5),
        ("word highlight (write)", "k:editor.wordHighlightStrongBackground", 4.5),
        ("bracket match", "k:editorBracketMatch.background", 4.5),
        ("inserted line (diff)", "k:diffEditor.insertedLineBackground", 4.5),
        ("removed line (diff)", "k:diffEditor.removedLineBackground", 4.5),
    ]
    for label, ref, target in overlays:
        bg = c.get(ref)
        worst = min(("editor.foreground", *[f"syntax.{s}" for s in SYNTAX]),
                    key=lambda n: ratio(c.get("k:" + n) if n.startswith("editor") else c.get("r:" + n), bg))
        fg = c.get("k:" + worst) if worst.startswith("editor") else c.get("r:" + worst)
        rows.append({"group": "Text over editor overlays (lowest of text + 6 syntax roles)",
                     "label": f"{label} ({worst})", "fg": fg, "bg": bg, "target": target, "ratio": ratio(fg, bg)})
    inserted_text = over(c.colors["diffEditor.insertedTextBackground"], c.get("k:diffEditor.insertedLineBackground"))
    removed_text = over(c.colors["diffEditor.removedTextBackground"], c.get("k:diffEditor.removedLineBackground"))
    rows.append({"group": "Text over editor overlays (lowest of text + 6 syntax roles)",
                 "label": "inserted text (diff, editor text)", "fg": c.get("k:editor.foreground"), "bg": inserted_text,
                 "target": 4.5, "ratio": ratio(c.get("k:editor.foreground"), inserted_text)})
    rows.append({"group": "Text over editor overlays (lowest of text + 6 syntax roles)",
                 "label": "removed text (diff, editor text)", "fg": c.get("k:editor.foreground"), "bg": removed_text,
                 "target": 4.5, "ratio": ratio(c.get("k:editor.foreground"), removed_text)})
    add("Selection pair", "selection.fg on selection.bg", "k:editor.selectionForeground",
        "k:editor.selectionBackground", 4.5)
    add("Gutter and hints", "line numbers", "k:editorLineNumber.foreground", "k:editorGutter.background", 5)
    add("Gutter and hints", "active line number", "k:editorLineNumber.activeForeground", "k:editorGutter.background", 7)
    add("Gutter and hints", "inlay hints", "k:editorInlayHint.foreground", "k:editorInlayHint.background", 5)
    add("Gutter and hints", "ghost text", "k:editorGhostText.foreground", EDITOR_BG, 5)
    add("Gutter and hints", "code lens", "k:editorCodeLens.foreground", EDITOR_BG, 5)
    add("Gutter and hints", "brackets level 2 / 3", "k:editorBracketHighlight.foreground3", EDITOR_BG, 5)
    for k in ("editorError", "editorWarning", "editorInfo", "editorHint"):
        add("Diagnostics", f"{k}.foreground on editor", f"k:{k}.foreground", EDITOR_BG, 5)
    add("Diagnostics", "git added in sidebar", "k:gitDecoration.addedResourceForeground", "k:sideBar.background", 5)
    add("Diagnostics", "git modified in sidebar", "k:gitDecoration.modifiedResourceForeground", "k:sideBar.background", 5)
    add("Diagnostics", "git deleted in sidebar", "k:gitDecoration.deletedResourceForeground", "k:sideBar.background", 5)
    add("Diagnostics", "git renamed in sidebar", "k:gitDecoration.renamedResourceForeground", "k:sideBar.background", 5)
    add("Diagnostics", "git ignored in sidebar", "k:gitDecoration.ignoredResourceForeground", "k:sideBar.background", 5)
    add("Diagnostics", "git modified on selected row", "k:gitDecoration.modifiedResourceForeground",
        "k:list.activeSelectionBackground", 4.5)
    add("Diagnostics", "git deleted on selected row", "k:gitDecoration.deletedResourceForeground",
        "k:list.activeSelectionBackground", 4.5)
    for k in ("error", "warning", "info"):
        add("Feedback pairs", f"inputValidation {k}", f"k:inputValidation.{k}Foreground",
            f"k:inputValidation.{k}Background", 4.5)
    for label, fg, bg, t in [
        ("sidebar text", "k:sideBar.foreground", "k:sideBar.background", 7),
        ("title bar text", "k:titleBar.activeForeground", "k:titleBar.activeBackground", 7),
        ("title bar text (inactive window)", "k:titleBar.inactiveForeground", "k:titleBar.inactiveBackground", 5),
        ("activity bar icons (active)", "k:activityBar.foreground", "k:activityBar.background", 7),
        ("activity bar icons (inactive)", "k:activityBar.inactiveForeground", "k:activityBar.background", 5),
        ("active tab", "k:tab.activeForeground", "k:tab.activeBackground", 7),
        ("inactive tab", "k:tab.inactiveForeground", "k:tab.inactiveBackground", 5),
        ("unfocused inactive tab", "k:tab.unfocusedInactiveForeground", "k:tab.unfocusedInactiveBackground", 5),
        ("tab hover", "k:tab.hoverForeground", "k:tab.hoverBackground", 7),
        ("status bar", "k:statusBar.foreground", "k:statusBar.background", 5),
        ("status bar item hover", "k:statusBarItem.hoverForeground", "k:statusBarItem.hoverBackground", 7),
        ("status bar debugging", "k:statusBar.debuggingForeground", "k:statusBar.debuggingBackground", 4.5),
        ("panel title (inactive)", "k:panelTitle.inactiveForeground", "k:panel.background", 5),
        ("breadcrumbs", "k:breadcrumb.foreground", "k:breadcrumb.background", 5),
        ("hover / widget text", "k:editorHoverWidget.foreground", "k:editorHoverWidget.background", 7),
        ("suggest selected row", "k:editorSuggestWidget.selectedForeground", "k:editorSuggestWidget.selectedBackground", 7),
        ("suggest match highlight on selected", "k:editorSuggestWidget.focusHighlightForeground",
         "k:editorSuggestWidget.selectedBackground", 5),
        ("menu selection", "k:menu.selectionForeground", "k:menu.selectionBackground", 7),
        ("notification text", "k:notifications.foreground", "k:notifications.background", 7),
        ("notification link", "k:notificationLink.foreground", "k:notifications.background", 5),
        ("quick input focused row", "k:quickInputList.focusForeground", "k:quickInputList.focusBackground", 7),
        ("list selection", "k:list.activeSelectionForeground", "k:list.activeSelectionBackground", 7),
        ("list hover", "k:list.hoverForeground", "k:list.hoverBackground", 7),
        ("list match highlight on selection", "k:list.highlightForeground", "k:list.activeSelectionBackground", 5),
        ("link in editor widgets", "k:textLink.foreground", "k:editorHoverWidget.background", 5),
        ("input text", "k:input.foreground", "k:input.background", 7),
        ("input placeholder", "k:input.placeholderForeground", "k:input.background", 5),
        ("peek view title", "k:peekViewTitleLabel.foreground", "k:peekViewTitle.background", 7),
        ("peek view description", "k:peekViewTitleDescription.foreground", "k:peekViewTitle.background", 5),
        ("peek view result row", "k:peekViewResult.selectionForeground", "k:peekViewResult.selectionBackground", 7),
    ]:
        add("Workbench text", label, fg, bg, t)
    for label, fg, bg, t in [
        ("primary button", "k:button.foreground", "k:button.background", 4.5),
        ("primary button hover", "k:button.foreground", "k:button.hoverBackground", 4.5),
        ("secondary button", "k:button.secondaryForeground", "k:button.secondaryBackground", 4.5),
        ("secondary button hover", "k:button.secondaryForeground", "k:button.secondaryHoverBackground", 4.5),
        ("badge", "k:badge.foreground", "k:badge.background", 4.5),
        ("remote indicator", "k:statusBarItem.remoteForeground", "k:statusBarItem.remoteBackground", 4.5),
        ("remote indicator hover", "k:statusBarItem.remoteForeground", "k:statusBarItem.remoteHoverBackground", 4.5),
    ]:
        add("Filled actions (accent.on)", label, fg, bg, t)
    for label, fg, bg, t in [
        ("primary button fill vs sidebar", "k:button.background", "k:sideBar.background", 3),
        ("primary button fill vs editor", "k:button.background", EDITOR_BG, 3),
        ("button outline vs sidebar", "k:button.border", "k:sideBar.background", 3),
        ("button outline vs editor widget", "k:button.border", "k:editorWidget.background", 3),
        ("input border vs sidebar", "k:input.border", "k:sideBar.background", 3),
        ("input border vs editor widget", "k:input.border", "k:editorWidget.background", 3),
        ("checkbox border vs sidebar", "k:checkbox.border", "k:sideBar.background", 3),
        ("focus ring vs editor", "k:focusBorder", EDITOR_BG, 3),
        ("focus ring vs sidebar", "k:focusBorder", "k:sideBar.background", 3),
        ("focus ring vs selected row", "k:focusBorder", "k:list.activeSelectionBackground", 3),
        ("focus ring vs widget", "k:focusBorder", "k:editorWidget.background", 3),
        ("focus ring vs status bar", "k:statusBar.focusBorder", "k:statusBar.background", 3),
        ("caret vs editor", "k:editorCursor.foreground", EDITOR_BG, 3),
        ("active tab indicator vs tab row", "k:tab.activeBorderTop", "k:editorGroupHeader.tabsBackground", 3),
        ("active activity item vs bar", "k:activityBar.activeBorder", "k:activityBar.background", 3),
        ("find match border vs match fill", "k:editor.findMatchBorder", "k:editor.findMatchBackground", 3),
        ("selected row vs sidebar (fill only, informational)", "k:list.activeSelectionBackground", "k:sideBar.background", 1),
        ("command center border vs title bar", "k:commandCenter.border", "k:titleBar.activeBackground", 3),
    ]:
        add("Functional boundaries", label, fg, bg, t)
    # terminal
    bg = c.get("k:terminal.background")
    sel = c.get("k:terminal.selectionBackground")
    neutral = {"ansiBlack", "ansiBrightWhite"}
    hues = [k for k, *_ in M.ANSI if k not in neutral and k != "ansiBrightBlack"]
    worst = min(hues, key=lambda k: ratio(c.get("k:terminal." + k), bg))
    rows.append({"group": "Terminal", "label": f"hues, normal and bright, lowest ({worst}) on background",
                 "fg": c.get("k:terminal." + worst), "bg": bg, "target": 5,
                 "ratio": ratio(c.get("k:terminal." + worst), bg)})
    add("Terminal", "foreground", "k:terminal.foreground", "k:terminal.background", 7)
    add("Terminal", "ansiWhite (TUI ink)", "k:terminal.ansiWhite", "k:terminal.background", 5)
    add("Terminal", "ansiBrightBlack (dim text)", "k:terminal.ansiBrightBlack", "k:terminal.background", 5)
    add("Terminal", "cursor", "k:terminalCursor.foreground", "k:terminal.background", 3)
    add("Terminal", "selection.fg on selection.bg", "k:terminal.selectionForeground", "k:terminal.selectionBackground", 4.5)
    worst_sel = min(hues + ["ansiBrightBlack"], key=lambda k: ratio(c.get("k:terminal." + k), sel))
    rows.append({"group": "Terminal", "label": f"colors on selection, lowest ({worst_sel}); selection.fg overrides them",
                 "fg": c.get("k:terminal." + worst_sel), "bg": sel, "target": 0,
                 "ratio": ratio(c.get("k:terminal." + worst_sel), sel)})
    return rows


def ansi_blocks(theme: dict, mode: str) -> dict:
    c = Ctx(theme, mode)
    bg = c.get("k:terminal.background")
    return {k: ratio(c.get("k:terminal." + k), bg) for k, *_ in M.ANSI}


def failures(theme: dict) -> list[str]:
    out = []
    for mode in MODES:
        for r in checks(theme, mode):
            if r["ratio"] + 1e-9 < r["target"]:
                out.append(f"{NAME[mode]}: {r['group']}: {r['label']} {r['ratio']:.2f}:1 < {r['target']}:1")
    return out


def contrast_report(theme: dict) -> str:
    L = []
    for mode in MODES:
        L.append(f"[{NAME[mode]}]")
        group = None
        for r in checks(theme, mode):
            if r["group"] != group:
                group = r["group"]
                L.append(f"  {group}")
            flag = "" if r["ratio"] + 1e-9 >= r["target"] else "  <-- below target"
            L.append(f"    {r['label']:<62}{r['ratio']:6.2f}:1  (target {r['target']:g}){flag}")
        L.append("  ANSI as text on terminal.background:")
        for k, v in ansi_blocks(theme, mode).items():
            L.append(f"    {k:<18}{v:6.2f}:1")
        L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# README blocks
# ---------------------------------------------------------------------------
def families(stack: str) -> list[str]:
    return re.findall(r'"([^"]+)"', stack)


def px(value: str) -> float:
    return float(value[:-3]) * 16


def fmt(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


def vscode_stack(stack: str) -> str:
    skip = {"ui-monospace", "system-ui"}
    parts = [p.strip() for p in re.findall(r'"[^"]*"|[^,]+', stack)]
    out = []
    for p in parts:
        bare = p.strip('"')
        if bare in skip:
            continue
        out.append(bare if bare in ("monospace", "sans-serif", "Consolas") else f"'{bare}'")
    return ", ".join(out)


def settings_doc(theme: dict) -> dict:
    t = theme["typography"]
    code = vscode_stack(t["font.code"])
    return {
        "workbench.preferredDarkColorTheme": NAME["slate"],
        "workbench.preferredLightColorTheme": NAME["daylight"],
        "window.autoDetectColorScheme": True,
        "editor.fontFamily": code,
        "editor.fontSize": int(px(t["font.size.code"])),
        "editor.lineHeight": int(round(px(t["font.size.code"]) * float(t["font.line.code"]))),
        "editor.fontLigatures": True,
        "terminal.integrated.fontFamily": code,
        "markdown.preview.fontFamily": vscode_stack(t["font.ui"]),
        "markdown.preview.fontSize": int(px(t["font.size.reading"])),
        "markdown.preview.lineHeight": float(t["font.line.reading"]),
    }


def md_settings(theme: dict) -> str:
    return "```json\n" + dumps(settings_doc(theme)).rstrip("\n") + "\n```"


def md_fonts(theme: dict) -> str:
    t = theme["typography"]
    code, lit = families(t["font.code"]), families(t["font.literal"])
    size = fmt(px(t["font.size.code"]))
    line = fmt(round(px(t["font.size.code"]) * float(t["font.line.code"])))
    return (f"| Use | Family (exact) |\n| :--- | :--- |\n"
            f"| Editor and terminal (default) | `{code[0]}` |\n"
            f"| Terminal or prompt with icons | `{code[1]}` |\n"
            f"| No ligatures (logs, hashes, literal output) | `{lit[0]}` |\n"
            f"| No ligatures, with icons | `{lit[1]}` |\n"
            f"| Markdown preview | `{families(t['font.ui'])[0]}` |\n\n"
            f"Starting size: {size} px with a {line} px line (`font.size.code`, `font.line.code`).")


def role_values(theme: dict, spec: str) -> tuple[str, str]:
    return resolve(theme, "slate", spec), resolve(theme, "daylight", spec)


def md_mapping(theme: dict) -> str:
    rows = ["| Group | Role | Slate | Daylight | VS Code keys |", "| :--- | :--- | :--- | :--- | :--- |"]
    total = 0
    for group, entries in M.WORKBENCH:
        merged: dict[str, list[str]] = {}
        for spec, keys in entries:
            merged.setdefault(spec, []).extend(keys)
        first = True
        for spec, keys in merged.items():
            s, d = role_values(theme, spec)
            total += len(keys)
            rows.append(f"| {group if first else ''} | `{spec}` | `{s}` | `{d}` | "
                        + ", ".join(f"`{k}`" for k in keys) + " |")
            first = False
    rows += ["", f"{total} workbench color keys, plus 16 `terminal.ansi*` keys, per theme."]
    return "\n".join(rows)


def md_ansi(theme: dict) -> str:
    S, D = ansi_blocks(theme, "slate"), ansi_blocks(theme, "daylight")
    c = {m: Ctx(theme, m) for m in MODES}
    rows = ["| # | Key | Flatcap role | Slate | Daylight |", "| ---: | :--- | :--- | :--- | :--- |"]
    for key, idx, rs, rd in M.ANSI:
        role = f"`{rs}`" if rs == rd else f"`{rs}` (Slate) · `{rd}` (Daylight)"
        rows.append(f"| {idx} | `terminal.{key}` | {role} | `{c['slate'].get('k:terminal.' + key)}` · {S[key]:.1f}:1 | "
                    f"`{c['daylight'].get('k:terminal.' + key)}` · {D[key]:.1f}:1 |")
    return "\n".join(rows)


def md_syntax(theme: dict) -> str:
    rows = ["| Element | Role | Scopes | Slate | Daylight |", "| :--- | :--- | :--- | :--- | :--- |"]
    for name, scopes, role, font in M.TOKENS:
        s, d = role_values(theme, role)
        style = f" ({font})" if font else ""
        rows.append(f"| {name}{style} | `{role}` | " + ", ".join(f"`{x}`" for x in scopes) + f" | `{s}` | `{d}` |")
    rows += ["", "Semantic tokens use the same roles:", "", "| Semantic token | Role |", "| :--- | :--- |"]
    for sel, role, font in M.SEMANTIC:
        rows.append(f"| `{sel}` | " + (f"`{role}`" if role else f"({font})") + " |")
    return "\n".join(rows)


def md_contrast(theme: dict) -> str:
    S, D = checks(theme, "slate"), checks(theme, "daylight")
    groups: dict[str, list[tuple[dict, dict]]] = {}
    for a, b in zip(S, D):
        groups.setdefault(a["group"], []).append((a, b))
    rows = ["| Check | Pairs | Lowest Slate | Lowest Daylight | Target | Result |",
            "| :--- | ---: | ---: | ---: | ---: | :--- |"]
    for g, pairs in groups.items():
        targets = sorted({a["target"] for a, _ in pairs})
        s = min(a["ratio"] for a, _ in pairs)
        d = min(b["ratio"] for _, b in pairs)
        ok = all(a["ratio"] + 1e-9 >= a["target"] and b["ratio"] + 1e-9 >= b["target"] for a, b in pairs)
        tgt = "/".join(f"{t:g}" for t in targets) + ":1"
        rows.append(f"| {g} | {len(pairs)} | {s:.2f}:1 | {d:.2f}:1 | {tgt} | {'met' if ok else 'not met'} |")
    return "\n".join(rows)


def md_groups(theme: dict) -> str:
    rows = ["| VS Code area | Flatcap roles | Keys |", "| :--- | :--- | ---: |"]
    total = 0
    for group, entries in M.WORKBENCH:
        roles: list[str] = []
        for spec, _keys in entries:
            role = spec.split("/")[0]
            if role not in ("transparent", "shadow") and role not in roles:
                roles.append(role)
        shown = ", ".join(f"`{r}`" for r in roles[:6]) + (", \u2026" if len(roles) > 6 else "")
        count = sum(len(keys) for _spec, keys in entries)
        area = re.sub(r" \(.*?\)", "", group)
        rows.append(f"| {area} | {shown} | {count} |")
        total += count
    rows += ["", f"{total} workbench color keys, plus 16 `terminal.ansi*` keys, per theme."]
    return "\n".join(rows)


README_BLOCKS = {"settings": md_settings, "fonts": md_fonts, "groups": md_groups, "ansi": md_ansi,
                 "contrast": md_contrast}
DOC_BLOCKS = {"mapping": md_mapping, "syntax": md_syntax}


def render_blocks(path: Path, blocks: dict, theme: dict) -> str:
    text = path.read_text(encoding="utf-8")
    for name, fn in blocks.items():
        pat = re.compile(rf"(<!-- build:{name} -->)\n.*?(<!-- /build:{name} -->)", re.S)
        if not pat.search(text):
            raise SystemExit(f"error: {path.relative_to(ROOT)} is missing the build:{name} markers")
        text = pat.sub(lambda m: m.group(1) + "\n" + fn(theme) + "\n" + m.group(2), text)
    return text


# ---------------------------------------------------------------------------
def validate(theme: dict) -> list[str]:
    errs = []
    for mode in MODES:
        for key, value in workbench_colors(theme, mode).items():
            if not re.match(r"^#[0-9A-F]{6}([0-9A-F]{2})?$", value, re.I):
                errs.append(f"{NAME[mode]}: {key} is not a hex color ({value!r})")
    if [a[1] for a in M.ANSI] != list(range(16)):
        errs.append("ANSI table must cover indexes 0..15 in order")
    return errs


def outputs(theme: dict) -> dict[Path, str]:
    out = {THEMES_DIR / FILE[m]: dumps(theme_file(theme, m)) for m in MODES}
    out[THEMES_DIR / LEGACY_FILE] = dumps(theme_file(theme, "slate", name=LEGACY_LABEL))
    out[PACKAGE] = dumps(package_json(theme))
    out[README] = render_blocks(README, README_BLOCKS, theme)
    out[MAPPING_DOC] = render_blocks(MAPPING_DOC, DOC_BLOCKS, theme)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if generated outputs are stale")
    ap.add_argument("--contrast", action="store_true", help="print the contrast report and exit")
    ap.add_argument("--sync", nargs="?", const=str(UPSTREAM), metavar="PATH",
                    help="copy theme.json from the core checkout (default ../00-Flatcap/src/theme.json)")
    args = ap.parse_args()

    if args.sync:
        src = Path(args.sync)
        if src.is_dir():
            src = src / "src" / "theme.json"
        if not src.is_file():
            print(f"error: {src} not found", file=sys.stderr)
            return 2
        shutil.copyfile(src, THEME)
        print(f"synced {src} -> {THEME.relative_to(ROOT)}")

    theme = load()
    if not str(theme.get("version", "")).startswith("2."):
        print(f"error: expected Flatcap 2.x theme.json, got {theme.get('version')}", file=sys.stderr)
        return 2
    errs = validate(theme)
    if errs:
        print("\n".join("error: " + e for e in errs), file=sys.stderr)
        return 2
    if args.contrast:
        print(contrast_report(theme))
        return 0
    if UPSTREAM.is_file() and UPSTREAM.read_bytes() != THEME.read_bytes():
        print("note: src/theme.json differs from ../00-Flatcap (run --sync to refresh)", file=sys.stderr)

    outs = outputs(theme)
    stale = []
    for path, text in outs.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
    fails = failures(theme)
    if args.check:
        if stale:
            print("stale: " + ", ".join(stale) + " (run python3 scripts/build.py)", file=sys.stderr)
        if fails:
            print("contrast below target:\n  " + "\n  ".join(fails), file=sys.stderr)
        if stale or fails:
            return 1
        print("ok: generated files are up to date and every contrast check meets its target")
    elif fails:
        print("warning: contrast below target (see --contrast):\n  " + "\n  ".join(fails), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
