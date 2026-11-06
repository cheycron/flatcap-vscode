# Flatcap for Visual Studio Code

![Version](https://img.shields.io/badge/version-2.0.0-blueviolet) ![VS Code](https://img.shields.io/badge/VS%20Code-%5E1.85-blue) ![License](https://img.shields.io/badge/license-MIT-blue) [![Marketplace](https://img.shields.io/badge/Marketplace-Flatcap-007acc?logo=visual-studio-code)](https://marketplace.visualstudio.com/items?itemName=cheycron.flatcap-theme)

<p align="center">
  <img src="https://raw.githubusercontent.com/cheycron/flatcap-vscode/main/images/screenshot-slate.png" alt="Flatcap Slate in VS Code: explorer with Git status, a TypeScript file with syntax highlighting, and the status bar" width="100%">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/cheycron/flatcap-vscode/main/images/screenshot-daylight.png" alt="Flatcap Daylight in VS Code: the same workspace in the light theme" width="100%">
</p>

<p align="center"><sub>Flatcap Slate (dark) above, Flatcap Daylight (light) below.</sub></p>

**Flatcap for Visual Studio Code** brings the Flatcap visual system to the editor: matte graphite surfaces, one mineral-blue accent, and syntax colors that stay in the background until they are needed.

> The interface organizes. Content takes the foreground. Color informs.

It ships two themes, tuned separately: **Flatcap Slate** (dark) and **Flatcap Daylight** (light).

## Quiet precision

[Flatcap](https://github.com/cheycron/flatcap-theme) is a semantic visual system for focused work. Colors are named for **what they do**, not for how they look, and the two themes share roles rather than identical values: Daylight is not an inverted Slate.

- **Hierarchy before decoration.** Surfaces separate by tone and hairline borders. Menus, hovers and suggestions are the only floating layer.
- **Useful color.** Mineral blue marks keywords, links, focus and the current item; red appears only for errors and deletions. Properties, namespaces and CSS values stay neutral, and symbol icons are colored by kind, not by rainbow.
- **Explicit interaction.** Focus rings, input outlines, buttons and the active tab indicator stay clearly visible in both themes.
- **Calm by default.** Bracket pairs cycle through the text roles and the accent; the current line is a quiet tint, not a border.

## Install

1. Open the Extensions view (`Ctrl+Shift+X`), search for `Flatcap` and install.
2. Run **Preferences: Color Theme** and pick **Flatcap Slate** or **Flatcap Daylight**.

## Upgrading from v1

The v1 theme ID `Flatcap` is kept as **Flatcap (v1 name, now Slate)**, so an existing `"workbench.colorTheme": "Flatcap"` keeps working and now renders Slate. The v1 palette (Nord-derived) is gone; colors are resolved by role from the Flatcap 2.0 core. Switch to the new names when convenient.

## Recommended settings

The themes do not change your settings. To follow the operating system's light/dark mode and use the Flatcap type scale, add this to `settings.json`:

<!-- build:settings -->
```json
{
  "workbench.preferredDarkColorTheme": "Flatcap Slate",
  "workbench.preferredLightColorTheme": "Flatcap Daylight",
  "window.autoDetectColorScheme": true,
  "editor.fontFamily": "'Cascadia Code', 'Cascadia Code NF', 'CaskaydiaCove Nerd Font Mono', Consolas, monospace",
  "editor.fontSize": 15,
  "editor.lineHeight": 24,
  "editor.fontLigatures": true,
  "terminal.integrated.fontFamily": "'Cascadia Code', 'Cascadia Code NF', 'CaskaydiaCove Nerd Font Mono', Consolas, monospace",
  "markdown.preview.fontFamily": "'IBM Plex Sans', 'Segoe UI', sans-serif",
  "markdown.preview.fontSize": 16,
  "markdown.preview.lineHeight": 1.625
}
```
<!-- /build:settings -->

## Fonts

Fonts are not bundled; install them on the machine where VS Code runs. Without them VS Code falls back to the next family in the list, and colors are unaffected.

<!-- build:fonts -->
| Use | Family (exact) |
| :--- | :--- |
| Editor and terminal (default) | `Cascadia Code` |
| Terminal or prompt with icons | `Cascadia Code NF` |
| No ligatures (logs, hashes, literal output) | `Cascadia Mono` |
| No ligatures, with icons | `Cascadia Mono NF` |
| Markdown preview | `IBM Plex Sans` |

Starting size: 15 px with a 24 px line (`font.size.code`, `font.line.code`).
<!-- /build:fonts -->

## How colors are chosen

Every value comes from the Flatcap 2.0 core and is resolved by semantic role, never by palette position. The themes also set TextMate scopes and semantic tokens. By area:

<!-- build:groups -->
| VS Code area | Flatcap roles | Keys |
| :--- | :--- | ---: |
| Base: text, links, focus, selection | `text.primary`, `text.secondary`, `text.disabled`, `danger.fg`, `focus.ring`, `accent.fg`, … | 23 |
| Editor surface and gutter | `bg.canvas`, `text.primary`, `text.muted`, `text.secondary`, `bg.hover`, `accent.fg`, … | 46 |
| Selection, occurrences, find, brackets | `selection.bg`, `selection.fg`, `accent.fg`, `focus.ring`, `text.primary`, `text.secondary`, … | 51 |
| Diagnostics, validation, banners | `danger.fg`, `warning.fg`, `info.fg`, `text.secondary`, `danger.bg`, `warning.bg`, … | 41 |
| Diff, merge and git | `success.bg`, `success.fg`, `danger.bg`, `danger.fg`, `warning.fg`, `info.fg`, … | 44 |
| Lists and trees | `bg.selected`, `text.primary`, `accent.fg`, `bg.hover`, `border.subtle` | 15 |
| Controls: buttons, inputs, checkboxes, dropdowns, badges, progress, scrollbars | `accent.fill`, `accent.on`, `accent.hover`, `bg.raised`, `text.primary`, `bg.hover`, … | 59 |
| Workbench chrome: title bar, activity bar, sidebar, tabs, panel, status bar | `bg.surface`, `bg.canvas`, `text.primary`, `text.secondary`, `text.muted`, `accent.fg`, … | 121 |
| Floating widgets: hover, suggest, find, menus, quick input, notifications, peek | `bg.raised`, `bg.surface`, `text.primary`, `text.secondary`, `border.subtle`, `border.control`, … | 57 |
| Terminal | `text.primary`, `bg.canvas`, `selection.bg`, `selection.fg`, `accent.fg`, `text.muted`, … | 14 |
| Debug, testing, notebooks, charts, source control graph | `danger.fg`, `danger.bg`, `success.fg`, `warning.fg`, `info.fg`, `text.muted`, … | 62 |
| Minimap and overview ruler | `selection.bg`, `accent.fg`, `bg.selected`, `border.control` | 9 |
| Symbol icons | `syntax.function`, `syntax.type`, `syntax.keyword`, `syntax.string`, `syntax.number`, `text.primary`, … | 32 |

574 workbench color keys, plus 16 `terminal.ansi*` keys, per theme.
<!-- /build:groups -->

The complete tables (every key with its role and the Slate and Daylight values, plus all syntax scopes and semantic tokens) are in the [full mapping](https://github.com/cheycron/flatcap-vscode/blob/main/docs/mapping.md).

### Terminal ANSI colors

Each ANSI color is a Flatcap role. The ratio is the color as text on the terminal background.

<!-- build:ansi -->
| # | Key | Flatcap role | Slate | Daylight |
| ---: | :--- | :--- | :--- | :--- |
| 0 | `terminal.ansiBlack` | `border.subtle` (Slate) · `text.primary` (Daylight) | `#3D4652` · 1.8:1 | `#28313B` · 12.1:1 |
| 1 | `terminal.ansiRed` | `danger.fg` | `#E2A0A5` · 7.9:1 | `#A43F4A` · 5.7:1 |
| 2 | `terminal.ansiGreen` | `success.fg` | `#9FC3AD` · 8.8:1 | `#32664D` · 6.1:1 |
| 3 | `terminal.ansiYellow` | `warning.fg` | `#D8BC87` · 9.2:1 | `#765319` · 6.4:1 |
| 4 | `terminal.ansiBlue` | `accent.fg` | `#9BBFDF` · 8.8:1 | `#285D85` · 6.4:1 |
| 5 | `terminal.ansiMagenta` | `syntax.number` | `#B6AED5` · 8.1:1 | `#68598C` · 5.7:1 |
| 6 | `terminal.ansiCyan` | `syntax.function` | `#ABC9CB` · 9.6:1 | `#306770` · 5.8:1 |
| 7 | `terminal.ansiWhite` | `text.secondary` | `#AEB8C4` · 8.4:1 | `#465463` · 7.1:1 |
| 8 | `terminal.ansiBrightBlack` | `text.muted` | `#A7B3C2` · 8.0:1 | `#536273` · 5.7:1 |
| 9 | `terminal.ansiBrightRed` | `danger.fg` | `#E2A0A5` · 7.9:1 | `#A43F4A` · 5.7:1 |
| 10 | `terminal.ansiBrightGreen` | `success.fg` | `#9FC3AD` · 8.8:1 | `#32664D` · 6.1:1 |
| 11 | `terminal.ansiBrightYellow` | `warning.fg` | `#D8BC87` · 9.2:1 | `#765319` · 6.4:1 |
| 12 | `terminal.ansiBrightBlue` | `accent.hover` | `#ACCCE7` · 10.1:1 | `#214F73` · 7.9:1 |
| 13 | `terminal.ansiBrightMagenta` | `syntax.number` | `#B6AED5` · 8.1:1 | `#68598C` · 5.7:1 |
| 14 | `terminal.ansiBrightCyan` | `syntax.function` | `#ABC9CB` · 9.6:1 | `#306770` · 5.8:1 |
| 15 | `terminal.ansiBrightWhite` | `text.primary` (Slate) · `bg.raised` (Daylight) | `#D5DBE3` · 12.2:1 | `#FFFFFF` · 1.1:1 |
<!-- /build:ansi -->

## Accessibility

Contrast is computed from the theme values by `scripts/build.py` (WCAG 2.x), and the build fails if any pair misses its target. Targets are 7:1 for editor and sidebar text, 5:1 for secondary text, syntax, links and diagnostics, 4.5:1 for text on filled actions and overlays, and 3:1 for controls and focus.

<!-- build:contrast -->
| Check | Pairs | Lowest Slate | Lowest Daylight | Target | Result |
| :--- | ---: | ---: | ---: | ---: | :--- |
| Editor | 1 | 12.15:1 | 12.06:1 | 7:1 | met |
| Syntax on canvas | 7 | 7.96:1 | 5.66:1 | 5:1 | met |
| Text over editor overlays (lowest of text + 6 syntax roles) | 13 | 3.69:1 | 4.43:1 | 0/4.5/5:1 | met |
| Selection pair | 1 | 5.64:1 | 9.45:1 | 4.5:1 | met |
| Gutter and hints | 6 | 5.74:1 | 5.71:1 | 5/7:1 | met |
| Diagnostics | 11 | 5.17:1 | 5.02:1 | 4.5/5:1 | met |
| Feedback pairs | 3 | 5.75:1 | 5.09:1 | 4.5:1 | met |
| Workbench text | 30 | 5.75:1 | 5.68:1 | 4.5/5/7:1 | met |
| Filled actions (accent.on) | 7 | 8.27:1 | 6.77:1 | 4.5:1 | met |
| Functional boundaries | 18 | 1.39:1 | 1.19:1 | 1/3:1 | met |
| Terminal | 7 | 3.67:1 | 4.43:1 | 0/3/4.5/5/7:1 | met |
<!-- /build:contrast -->

Known limits:

- **`terminal.ansiBrightWhite` in Daylight is `bg.raised` (`#FFFFFF`) on purpose.** It is meant for text on colored blocks, so as text on the terminal background it is 1.1:1. In Slate, `terminal.ansiBlack` is `border.subtle` (1.8:1): a surface tone, not text ink.
- **Syntax colors over a text selection** would fall to 3.69:1 (Slate) and 4.43:1 (Daylight) in the worst case. The themes set `editor.selectionForeground` and `terminal.selectionForeground` to `selection.fg` (5.64:1 and 9.45:1), so selected text is drawn in that one color. The same applies to ANSI colors in the terminal.
- **Decorative surfaces are not held to 3:1.** Hairline borders and selected-row fills separate by tone only (the selected row against the sidebar is 1.39:1 in Slate and 1.19:1 in Daylight). Controls, outlines and focus rings are held to 3:1.
- **Computed, not sampled.** Ratios come from the theme values, not from measuring every rendered widget. Colors that other extensions set for their own views are outside the theme's control.

## Compatibility

- **VS Code ^1.85** (`engines.vscode`). Versions between 1.85 and 1.145 were not tested one by one.
- Tested on **code-server 4.145 (VS Code 1.145)** and on desktop VS Code, where the author checked the packaged VSIX.
- Semantic highlighting is enabled by the themes. Language extensions that provide semantic tokens use the semantic colors; the rest use the TextMate scopes.

## How it is built

`themes/*.json`, the `package.json` theme entries and the generated README and `docs/mapping.md` blocks are produced by a script; do not edit them by hand.

- `src/theme.json` is a copy of the Flatcap 2.0 core.
- `scripts/mapping.py` maps roles to VS Code keys, scopes and tokens (roles only, no hex).
- `scripts/build.py` resolves the roles, runs the contrast gate and writes the files. It needs Python 3.10+ and nothing else.

```sh
python3 scripts/build.py            # regenerate themes, package.json fields and docs
python3 scripts/build.py --check    # fail if generated files are stale or contrast misses its target
python3 scripts/build.py --sync     # copy theme.json from ../00-Flatcap, then rebuild
python3 scripts/build.py --contrast # print the full contrast report
```

Colors come from [Flatcap](https://github.com/cheycron/flatcap-theme), the core of the system.

## License

MIT. Fonts are not bundled and carry their own licenses. The cap drawing in the extension icon derives from third-party artwork (Vexels, [terms](https://vexels.com/terms-and-conditions/)) and is not relicensed by MIT.

## Support

If Flatcap makes your workspace calmer, you can support its development.

<p align="center">
  <a href="https://www.buymeacoffee.com/cheycron">
    <img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me a Coffee">
  </a>
</p>
