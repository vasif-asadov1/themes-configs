
# Themes & Configurations

A personal collection of custom Visual Studio Code themes and development environment configurations.

Maintained by [vasif-asadov1](https://github.com/vasif-asadov1).

---

## 🎨 VS Code Themes

### Ubuntu Aubergine Advanced

A custom dark theme inspired by Ubuntu's classic aubergine terminal colors, featuring a deep reddish-purple background, warm orange accents, and comprehensive syntax highlighting.

Designed for software development, data engineering, data science, and technical documentation.

### Color Palette

| Element | Hex Color |
|---------|-----------|
| Editor Background | `#300A24` |
| Ubuntu Purple | `#772953` |
| Ubuntu Orange | `#E95420` |
| Editor Foreground | `#EEEEEC` |
| Functions | `#FCAF3E` |
| Keywords | `#FF7A59` |
| Strings | `#A8D870` |
| Types and Classes | `#8BBCE0` |
| Numbers | `#E07B9F` |
| Comments | `#8F7387` |
| Properties | `#D9B3D4` |
| Parameters | `#F0C8A0` |
| Decorators | `#AD7FA8` |

### Features

- Classic Ubuntu aubergine interface
- Advanced semantic syntax highlighting
- Custom editor, sidebar, tabs, and activity bar
- Integrated terminal color customization
- Git decorations and diff highlighting
- Error, warning, and diagnostic highlighting
- Bracket pair colorization
- Jupyter Notebook interface styling
- Markdown and technical documentation styling
- Enhanced syntax highlighting for programming languages

### Supported Languages and Formats

The theme includes syntax highlighting rules for:

**Programming Languages**
- Python
- R
- JavaScript
- TypeScript
- Bash and shell scripting

**Data Engineering**
- SQL
- JSON and JSONC
- YAML
- TOML
- CSV (with appropriate extensions)

**Documentation**
- Markdown
- LaTeX
- BibTeX
- Typst
- Plain text

**Web Development**
- HTML
- CSS
- XML

**Development and Configuration**
- Dockerfile
- Makefile
- INI
- Environment files

**Notebooks**
- Jupyter Notebooks (`.ipynb`)
- Python notebook cells
- Markdown notebook cells

Language-specific syntax highlighting depends on the language grammars and extensions installed in VS Code. Plain text receives the theme's editor colors without syntax highlighting.

---

## 📁 Repository Structure

    themes-configs/
    ├── README.md
    ├── .gitignore
    └── vs_code_themes/
        └── ubuntu-aubergine/
            ├── package.json
            ├── README.md
            └── themes/
                └── ubuntu-aubergine-color-theme.json

Additional themes and configurations may be added in future updates.

---

## 🚀 Installation

### 1. Clone the Repository

Using SSH:

    git clone git@github.com:vasif-asadov1/themes-configs.git

Or using HTTPS:

    git clone https://github.com/vasif-asadov1/themes-configs.git

### 2. Navigate to the Repository

    cd themes-configs

### 3. Install Ubuntu Aubergine Advanced

Copy the extension directory into the VS Code extensions folder:

    cp -r vs_code_themes/ubuntu-aubergine \
        ~/.vscode/extensions/vasif.ubuntu-aubergine-2.0.0

### 4. Activate the Theme

1. Open Visual Studio Code.
2. Press `Ctrl+Shift+P`.
3. Run `Developer: Reload Window`.
4. Press `Ctrl+K`, followed by `Ctrl+T`.
5. Select `Ubuntu Aubergine Advanced`.

The displayed theme name depends on the extension's `package.json` configuration.

---

## 🛠️ Customization

The theme's main configuration file is:

    vs_code_themes/ubuntu-aubergine/themes/ubuntu-aubergine-color-theme.json

The JSON file contains three primary sections:

- `colors`: Visual Studio Code interface colors.
- `tokenColors`: TextMate syntax highlighting rules.
- `semanticTokenColors`: Semantic highlighting for language-aware tokens.

To edit the theme locally, open the repository in VS Code:

    code ~/Projects/themes-configs

After modifying the theme, copy the updated files into the installed extension directory and reload VS Code.

---

## 🐧 Development Environment

The themes are developed and tested primarily on:

- Linux Mint XFCE
- Bash shell
- Visual Studio Code
- Git and GitHub

The themes use VS Code's cross-platform color theme system and are not restricted to Linux.

---

## 📌 Project Goals

- Maintain a consistent Ubuntu-inspired development environment.
- Provide comprehensive syntax highlighting across different languages.
- Improve readability during long programming sessions.
- Support data engineering and scientific computing workflows.
- Maintain portable, version-controlled configurations.
- Continuously refine visual consistency and accessibility.

---

## 👤 Author

**vasif-asadov1**

GitHub: https://github.com/vasif-asadov1

Repository: https://github.com/vasif-asadov1/themes-configs

---

## 📄 License

No license has been selected for this repository.

All rights are reserved unless a license is explicitly added.

Third-party extensions and themes retain their respective licenses and copyrights.
