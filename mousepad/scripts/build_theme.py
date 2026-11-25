
from pathlib import Path
from copy import deepcopy
import xml.etree.ElementTree as ET
import re

# ============================================================
# OBSIDIAN SAPPHIRE THEME — UNIVERSAL EDITION
# ============================================================

HOME = Path.home()

GTK_DATA = HOME / ".local/share/gtksourceview-4"
PROJECT_DIR = Path(__file__).resolve().parents[1]
STYLE_DIR = PROJECT_DIR / "styles"

LANGUAGE_DIRS = [
    Path("/usr/share/gtksourceview-4/language-specs"),
    PROJECT_DIR / "language-specs",
]

BASE_THEME = PROJECT_DIR / "src/base-theme.xml"
OUTPUT = STYLE_DIR / "obsidian-sapphire.xml"

# ============================================================
# MASTER PALETTE
# ============================================================

PALETTE = {
    "background": "#151B23",
    "surface":    "#222D3A",
    "foreground": "#D4DEEB",
    "comment":    "#8293AA",
    "keyword":    "#B49AF0",
    "function":   "#64B5F6",
    "type":       "#59C9C2",
    "string":     "#89C9A6",
    "number":     "#E7C080",
    "constant":   "#98FFB3",
    "property":   "#91CCFF",
    "operator":   "#59C9C2",
    "error":      "#ED7786",
    "selection":  "#2C4057",
    "border":     "#354153",
    "muted":      "#52657D",
}

# ============================================================
# LOAD WORKING V2 THEME
# ============================================================

if not BASE_THEME.is_file():
    raise SystemExit(f"Base theme not found: {BASE_THEME}")

root = ET.parse(BASE_THEME).getroot()

root.set("id", "obsidian-sapphire")
root.attrib.pop("name", None)
root.attrib.pop("_name", None)
root.set("_name", "Obsidian Sapphire Theme")

description = root.find("description")

if description is None:
    description = ET.SubElement(root, "description")

description.text = (
    "Universal Obsidian Sapphire theme for GtkSourceView 4"
)

styles = {
    style.get("name"): style
    for style in root.findall("style")
}

# ============================================================
# STYLE UTILITIES
# ============================================================

def add_style(name, category, **options):
    if name in styles:
        return

    attributes = {
        "name": name,
        "foreground": PALETTE[category],
        **options,
    }

    element = ET.SubElement(root, "style", attributes)
    styles[name] = element


def copy_style(name, source):
    if name in styles or source not in styles:
        return False

    element = deepcopy(styles[source])
    element.set("name", name)

    root.append(element)
    styles[name] = element

    return True


# ============================================================
# COMPLETE GENERIC STYLE COVERAGE
# ============================================================

GENERIC = {
    "comment": "comment",
    "shebang": "comment",
    "doc-comment": "comment",
    "doc-comment-element": "property",
    "constant": "constant",
    "character": "string",
    "string": "string",
    "special-char": "number",
    "number": "number",
    "floating-point": "number",
    "decimal": "number",
    "base-n-integer": "number",
    "complex": "number",
    "special-constant": "constant",
    "boolean": "constant",
    "identifier": "foreground",
    "function": "function",
    "builtin": "function",
    "statement": "keyword",
    "operator": "operator",
    "keyword": "keyword",
    "type": "type",
    "emphasis": "keyword",
    "strong-emphasis": "number",
    "inline-code": "string",
    "insertion": "constant",
    "deletion": "error",
    "link-text": "function",
    "link-symbol": "type",
    "link-destination": "property",
    "heading": "function",
    "thematic-break": "muted",
    "preformatted-section": "string",
    "list-marker": "constant",
    "preprocessor": "keyword",
    "error": "error",
    "warning": "number",
    "reserved": "keyword",
    "note": "number",
    "net-address": "function",
    "underlined": "function",
}

for style_id, category in GENERIC.items():
    options = {}

    if style_id in {
        "comment", "doc-comment", "emphasis"
    }:
        options["italic"] = "true"

    if style_id in {
        "heading", "strong-emphasis", "note"
    }:
        options["bold"] = "true"

    if style_id in {
        "link-text", "net-address", "underlined", "insertion"
    }:
        options["underline"] = "single"

    if style_id == "deletion":
        options["strikethrough"] = "true"

    add_style(f"def:{style_id}", category, **options)

for level in range(7):
    add_style(
        f"def:heading{level}",
        "function",
        bold="true",
    )

# ============================================================
# READ ALL INSTALLED LANGUAGE DEFINITIONS
# ============================================================

definitions = {}
languages = set()

for directory in LANGUAGE_DIRS:
    if not directory.is_dir():
        continue

    for path in sorted(directory.glob("*.lang")):
        try:
            language = ET.parse(path).getroot()
        except ET.ParseError as error:
            print(f"Skipped {path.name}: {error}")
            continue

        language_id = language.get("id")

        if not language_id:
            continue

        languages.add(language_id)

        for style in language.findall("./styles/style"):
            style_id = style.get("id")

            if not style_id:
                continue

            full_id = f"{language_id}:{style_id}"

            target = style.get("map-to")

            if target and ":" not in target:
                target = f"{language_id}:{target}"

            definitions[full_id] = {
                "id": style_id,
                "target": target,
            }

# ============================================================
# FALLBACK CLASSIFICATION
# Used only when no mapped style exists.
# ============================================================

RULES = [
    (r"comment|docstring|shebang", "comment"),
    (r"error|invalid", "error"),
    (r"warning|todo|fixme", "number"),
    (r"heading|header|title", "function"),
    (r"decorator|annotation", "number"),
    (r"boolean|constant|null|literal", "constant"),
    (r"string|character|quote", "string"),
    (r"number|integer|float|decimal|numeric", "number"),
    (r"function|method|builtin|command", "function"),
    (r"class|type|namespace|interface|struct", "type"),
    (r"property|attribute|key|field", "property"),
    (r"keyword|statement|control|directive", "keyword"),
    (r"operator|punctuation|delimiter", "operator"),
    (r"link|url", "function"),
    (r"tag|element|selector", "type"),
    (r"parameter|argument", "number"),
    (r"variable|identifier", "foreground"),
]


def classify(style_id):
    for pattern, category in RULES:
        if re.search(pattern, style_id, re.IGNORECASE):
            return category

    return None


# ============================================================
# RESOLVE STYLE MAPPINGS
# ============================================================

def resolve(name, visited=None):
    if name in styles:
        return True

    if name not in definitions:
        return False

    visited = set() if visited is None else visited

    if name in visited:
        return False

    visited.add(name)

    definition = definitions[name]
    target = definition["target"]

    if target and resolve(target, visited):
        return copy_style(name, target)

    category = classify(definition["id"])

    if category:
        options = {}

        if category == "comment":
            options["italic"] = "true"

        if re.search(r"heading|header", definition["id"]):
            options["bold"] = "true"

        add_style(name, category, **options)

        return True

    return False


original_count = len(styles)

unresolved = []

for name in sorted(definitions):
    if not resolve(name):
        unresolved.append(name)

# ============================================================
# WRITE FINAL UNIVERSAL THEME
# ============================================================

STYLE_DIR.mkdir(parents=True, exist_ok=True)

ET.indent(root, space="    ")

ET.ElementTree(root).write(
    OUTPUT,
    encoding="UTF-8",
    xml_declaration=True,
)

# Verify generated XML is readable.
ET.parse(OUTPUT)

# ============================================================
# BUILD REPORT
# ============================================================

print()
print("=" * 60)
print("OBSIDIAN SAPPHIRE THEME")
print("=" * 60)
print(f"Language definitions : {len(languages)}")
print(f"Available style IDs  : {len(definitions)}")
print(f"Original styles      : {original_count}")
print(f"New styles           : {len(styles) - original_count}")
print(f"Total theme styles   : {len(styles)}")
print(f"Unresolved styles    : {len(unresolved)}")
print(f"Output               : {OUTPUT}")
print("XML validation       : PASSED")
print("=" * 60)

if unresolved:
    report = PROJECT_DIR / "unresolved.txt"

    report.write_text(
        "\n".join(unresolved) + "\n",
        encoding="utf-8",
    )

    print(f"Unresolved report    : {report}")

print("\nBuild completed successfully.")
