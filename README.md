# Obsidian Sapphire Theme

> One palette. Multiple editors. A unified development experience.

A comprehensive dark color theme designed for software developers, data engineers, scientists, researchers, and Linux enthusiasts.

Obsidian Sapphire combines deep blue-black backgrounds with sapphire blue, glacier teal, amethyst purple, jade green, and champagne accents. It provides a consistent visual identity across Visual Studio Code, Mousepad, and terminal environments.

## Features

- Carefully coordinated dark color palette.
- Comprehensive syntax highlighting.
- TextMate and semantic token support for Visual Studio Code.
- Universal GtkSourceView 4 color scheme for Mousepad.
- Dedicated Python, Typst, TOML, and Rainbow CSV refinements.
- Integrated terminal and Jupyter Notebook styling.
- Custom JSONC and basic Typst language definitions for Mousepad.
- Reproducible Python-based theme builders.
- No theme-specific background processes or runtime dependencies.

## Supported Editors

| Feature | Visual Studio Code | Mousepad |
|---|---|---|
| Dark color scheme | Yes | Yes |
| Syntax highlighting | TextMate | GtkSourceView 4 |
| Semantic highlighting | Yes, where available | No |
| Language-specific customization | Yes | Yes |
| Custom theme builder | Yes | Yes |
| Integrated terminal styling | Yes | N/A |
| Jupyter Notebook styling | Yes | N/A |

## Color Palette

| Color | HEX | Purpose |
|---|---|---|
| Obsidian | `#151B23` | Editor background |
| Deep Obsidian | `#10161E` | Primary interface surfaces |
| Midnight | `#19212B` | Secondary surfaces |
| Slate | `#354153` | Borders and separators |
| Sapphire | `#64B5F6` | Functions and methods |
| Glacier Teal | `#59C9C2` | Classes and data types |
| Glacier Blue | `#91CCFF` | Properties and keys |
| Amethyst | `#B49AF0` | Keywords and control flow |
| Jade | `#89C9A6` | Strings |
| Mint | `#98FFB3` | Constants and booleans |
| Champagne | `#E7C080` | Numbers and parameters |
| Ruby | `#ED7786` | Errors and invalid syntax |
| Silver | `#D4DEEB` | Variables and normal text |
| Muted Steel | `#8293AA` | Comments |

## Language Support

The theme is designed for broad language compatibility, with particular emphasis on data engineering, scientific computing, academic writing, and software development.

| Category | Languages and Formats |
|---|---|
| Data Engineering | Python, SQL, R, Julia, CSV, TSV |
| Configuration | JSON, JSONC, TOML, YAML, INI, XML |
| Academic Writing | Typst, LaTeX, BibTeX, Markdown |
| Scientific Computing | MATLAB, Octave, Fortran, CUDA |
| Web Development | HTML, CSS, SCSS, JavaScript, TypeScript, JSX, TSX |
| Systems Programming | C, C++, Rust, Go |
| General Programming | Java, Kotlin, C#, Ruby, PHP, Lua |
| Shell and DevOps | Bash, Fish, PowerShell, Dockerfile, Makefile, CMake, Terraform |
| Version Control | Git diff, patches, commit messages |
| Documentation | Markdown, AsciiDoc, reStructuredText, plain text |

Actual language availability and highlighting precision depend on the installed editor grammars and language extensions.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vasif-asadov1/themes-configs.git
cd themes-configs
```

### 2. Visual Studio Code

The current extension version is **1.1.0**.

#### Method A — Install from a VSIX Package

If a packaged VSIX file is available in the GitHub Releases section, download it and install it with:

```bash
code --install-extension obsidian-sapphire-theme-1.1.0.vsix
```

Alternatively:

1. Open Visual Studio Code.
2. Open the Command Palette with `Ctrl + Shift + P`.
3. Select `Extensions: Install from VSIX`.
4. Select the downloaded VSIX package.
5. Open the color theme selector with `Ctrl + K`, followed by `Ctrl + T`.
6. Select **Obsidian Sapphire Theme**.

#### Method B — Build and Install from Source

Requirements:

- Visual Studio Code
- Node.js
- npm

From the repository root:

```bash
cd vscode

npx --yes @vscode/vsce package \
    --no-dependencies \
    --allow-missing-repository \
    --out obsidian-sapphire-theme-1.1.0.vsix

code --install-extension \
    obsidian-sapphire-theme-1.1.0.vsix
```

Reload Visual Studio Code and select **Obsidian Sapphire Theme**.

Verify the installation:

```bash
code --list-extensions --show-versions | grep obsidian-sapphire
```

Expected output:

```text
vasif-asadov.obsidian-sapphire-theme@1.1.0
```

#### Recommended VS Code Settings

The following optional settings complement the theme:

```json
{
    "workbench.colorTheme": "Obsidian Sapphire Theme",
    "editor.fontFamily": "'JetBrains Mono', monospace",
    "editor.fontSize": 14,
    "editor.fontLigatures": true,
    "editor.semanticHighlighting.enabled": true,
    "editor.bracketPairColorization.enabled": true,
    "editor.guides.bracketPairs": "active",
    "editor.guides.indentation": true,
    "editor.minimap.enabled": false,
    "editor.smoothScrolling": false,
    "workbench.list.smoothScrolling": false,
    "workbench.reduceMotion": "on",
    "editor.cursorBlinking": "solid",
    "terminal.integrated.fontFamily": "JetBrainsMono Nerd Font",
    "terminal.integrated.fontSize": 13,
    "terminal.integrated.cursorStyle": "block",
    "terminal.integrated.cursorBlinking": false
}
```

Merge these settings into your existing user configuration. Do not overwrite unrelated settings.

JetBrains Mono and its Nerd Font variant are optional and must be installed separately if desired.

#### Recommended Language Extensions

For enhanced language-specific highlighting and development functionality:

| Language | Extension |
|---|---|
| Python | Python and Pylance |
| Jupyter Notebook | Jupyter |
| Typst | Tinymist |
| LaTeX | LaTeX Workshop |
| TOML | Even Better TOML |
| YAML | YAML by Red Hat |
| CSV / TSV | Rainbow CSV |
| Markdown | Markdown All in One |

These extensions are optional. The color theme does not install or require them automatically.

### 3. Mousepad

The Mousepad theme targets **GtkSourceView 4**.

From the repository root, create the user-level theme directories:

```bash
mkdir -p ~/.local/share/gtksourceview-4/styles
mkdir -p ~/.local/share/gtksourceview-4/language-specs
```

Install the color scheme:

```bash
cp mousepad/styles/obsidian-sapphire.xml \
    ~/.local/share/gtksourceview-4/styles/
```

Install the additional JSONC and Typst language definitions:

```bash
cp mousepad/language-specs/jsonc.lang \
    ~/.local/share/gtksourceview-4/language-specs/

cp mousepad/language-specs/typst.lang \
    ~/.local/share/gtksourceview-4/language-specs/
```

Save your open documents and restart Mousepad.

#### Activate Using the Graphical Interface

1. Open Mousepad.
2. Open Edit → Preferences.
3. Locate the color scheme settings.
4. Select **Obsidian Sapphire Theme**.
5. Open a source code file to verify syntax highlighting.

#### Activate Using the Terminal

```bash
gsettings set \
    org.xfce.mousepad.preferences.view \
    color-scheme \
    'obsidian-sapphire'
```

Verify the active scheme:

```bash
gsettings get \
    org.xfce.mousepad.preferences.view \
    color-scheme
```

Expected output:

```text
'obsidian-sapphire'
```

#### Language Detection

Mousepad normally detects the language from the file extension.

If syntax highlighting does not appear, select the appropriate language manually from the document's Filetype menu.

Examples:

| Extension | Language |
|---|---|
| `.py` | Python |
| `.sql` | SQL |
| `.json` | JSON |
| `.jsonc` | JSON with Comments |
| `.md` | Markdown |
| `.typ` | Typst (Basic) |
| `.toml` | TOML |
| `.yaml` | YAML |
| `.tex` | LaTeX |
| `.fish` | Fish |
| `.sh` | Shell |

For VS Code configuration files such as `settings.json`, manually select JSON with Comments if necessary.

The custom Typst grammar provides basic lexical highlighting rather than complete semantic analysis.

## Theme Architecture

### Visual Studio Code

The theme combines three independent coloring mechanisms:

1. Workbench colors for editor interface components.
2. TextMate rules for lexical syntax highlighting.
3. Semantic token rules for language-aware highlighting.

The original development environment contains:

| Metric | Value |
|---|---:|
| Grammar files analyzed | 121 |
| Successfully parsed grammar files | 121 |
| Unique TextMate scopes discovered | 7,243 |
| Workbench color definitions | 223 |

Structural scopes are deliberately left uncolored when assigning a foreground color could interfere with nested syntax.

### Mousepad

The Mousepad theme is generated from installed GtkSourceView 4 language definitions.

| Metric | Value |
|---|---:|
| Visible language definitions | 153 |
| Total language definitions analyzed | 171 |
| Available language style identifiers | 1,634 |
| Generated theme styles | 1,612 |
| Unresolved style identifiers | 37 |
| Style identifier resolution rate | 97.74% |

These statistics describe the original development environment. Counts may differ when rebuilding on another system.

Language coverage statistics do not guarantee perfect highlighting of every syntax construct.

## Building the Themes

Both theme builders use the Python standard library. No additional Python packages are required.

Python 3.9 or newer is recommended.

### Build the VS Code Theme

From the repository root:

```bash
python3 vscode/scripts/build_theme.py
```

The builder:

- Loads the base theme.
- Discovers installed TextMate grammars.
- Extracts syntax scopes.
- Preserves existing syntax and interface colors.
- Adds missing syntax rules.
- Applies language-specific semantic refinements.
- Generates audit reports.
- Validates the resulting JSON.

Generated theme:

```text
vscode/themes/obsidian-sapphire-color-theme.json
```

The default grammar discovery paths target standard Linux installations of Visual Studio Code. Adjust `GRAMMAR_ROOTS` in the builder for other installation paths.

### Build the Mousepad Theme

Install GtkSourceView 4 language definitions using your distribution's package manager if they are not already available.

From the repository root:

```bash
python3 mousepad/scripts/build_theme.py
```

The builder:

- Loads the base GtkSourceView color scheme.
- Reads installed language definitions.
- Includes custom JSONC and Typst grammars.
- Resolves generic and language-specific style mappings.
- Generates additional syntax styles.
- Reports unresolved style identifiers.
- Validates the resulting XML.

Generated theme:

```text
mousepad/styles/obsidian-sapphire.xml
```

Reinstall the generated color scheme using the Mousepad installation instructions.

## Repository Structure

```text
themes-configs/
├── README.md
├── .gitignore
│
├── vscode/
│   ├── package.json
│   ├── .vscodeignore
│   ├── src/
│   │   └── base-theme.json
│   ├── scripts/
│   │   ├── build_theme.py
│   │   └── language_styles.py
│   └── themes/
│       └── obsidian-sapphire-color-theme.json
│
├── mousepad/
│   ├── src/
│   │   └── base-theme.xml
│   ├── scripts/
│   │   └── build_theme.py
│   ├── styles/
│   │   └── obsidian-sapphire.xml
│   └── language-specs/
│       ├── jsonc.lang
│       └── typst.lang
│
├── alacritty/
├── sql_containers/
└── vs_code_themes/
```

The repository also preserves earlier Ubuntu Aubergine themes and related Linux development configurations.

## Customization

The theme is intentionally extensible.

- Modify `vscode/src/base-theme.json` to customize the base VS Code colors.
- Modify `vscode/scripts/language_styles.py` to customize language-specific rules.
- Modify `mousepad/src/base-theme.xml` to customize the Mousepad base scheme.
- Modify the palette in the corresponding Python builder to adjust generated styles.

Rebuild and reinstall the appropriate theme after making changes.

## Performance

Obsidian Sapphire is a static color theme.

It does not require theme-specific background services, continuously running scripts, or additional runtime processes. The Python builders run only when explicitly invoked.

Normal editor resource consumption still depends on file size, installed extensions, syntax complexity, and editor features.

## Troubleshooting

### The VS Code Theme Does Not Appear

- Verify that the extension is installed.
- Reload the VS Code window.
- Open the color theme selector.
- Select Obsidian Sapphire Theme.

### Syntax Colors Look Incorrect in VS Code

- Verify that the correct language mode is selected.
- Enable semantic highlighting where supported.
- Check for conflicting token color customizations.
- Install the relevant language extension if necessary.
- Use `Developer: Inspect Editor Tokens and Scopes` to investigate individual tokens.

### Mousepad Displays Plain Text Without Syntax Colors

- Verify that Obsidian Sapphire Theme is active.
- Select the correct document filetype.
- Confirm that GtkSourceView 4 is being used.
- Restart Mousepad after installing new language definitions.

### JSONC or Typst Is Not Available in Mousepad

Verify that the custom `.lang` files are installed under:

```text
~/.local/share/gtksourceview-4/language-specs/
```

Restart Mousepad after installation.

## Uninstallation

### Visual Studio Code

```bash
code --uninstall-extension vasif-asadov.obsidian-sapphire-theme
```

Select another color theme.

### Mousepad

Select another color scheme before removing the theme:

```bash
gsettings set \
    org.xfce.mousepad.preferences.view \
    color-scheme \
    'oblivion'
```

Remove the installed theme:

```bash
rm -f ~/.local/share/gtksourceview-4/styles/obsidian-sapphire.xml
```

Optionally remove the additional language definitions if they are no longer required:

```bash
rm -f ~/.local/share/gtksourceview-4/language-specs/jsonc.lang
rm -f ~/.local/share/gtksourceview-4/language-specs/typst.lang
```

## Design Philosophy

- Consistency across development tools.
- Comfortable contrast and readable typography.
- Clear differentiation between syntax categories.
- Minimal visual distractions.
- Broad language compatibility.
- Lightweight implementation.
- Reproducible and maintainable configuration.

## Author

**Vasif Asadov**

GitHub: [vasif-asadov1](https://github.com/vasif-asadov1)

## Contributions

Suggestions, bug reports, syntax highlighting improvements, and additional language support are welcome through GitHub Issues and Pull Requests.

---

**Obsidian Sapphire Theme — Designed for focused development.**

