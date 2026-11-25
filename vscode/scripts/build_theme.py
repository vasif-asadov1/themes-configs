
from pathlib import Path
from collections import defaultdict
from copy import deepcopy
import json
import plistlib
import re

# ============================================================
# OBSIDIAN SAPPHIRE THEME
# Visual Studio Code — Universal Theme Builder
# ============================================================

HOME = Path.home()
PROJECT = Path(__file__).resolve().parents[1]

BASE = PROJECT / "src/base-theme.json"
OUTPUT = PROJECT / "themes/obsidian-sapphire-color-theme.json"
REPORTS = PROJECT / "reports"

GRAMMAR_ROOTS = [
    Path("/usr/share/code/resources/app/extensions"),
    Path("/opt/visual-studio-code/resources/app/extensions"),
    HOME / ".vscode/extensions",
]

# ============================================================
# MASTER PALETTE
# ============================================================

P = {
    "background": "#151B23",
    "foreground": "#D4DEEB",
    "surface": "#222D3A",
    "border": "#354153",

    "comment": "#8293AA",
    "keyword": "#B49AF0",
    "function": "#64B5F6",
    "type": "#59C9C2",
    "property": "#91CCFF",
    "string": "#89C9A6",
    "number": "#E7C080",
    "constant": "#98FFB3",
    "operator": "#87E3DC",
    "decorator": "#D0B8FF",
    "error": "#ED7786",

    "heading1": "#64B5F6",
    "heading2": "#59C9C2",
    "heading3": "#B49AF0",
    "heading4": "#E7C080",
    "heading5": "#98FFB3",
    "heading6": "#91CCFF",
}

# ============================================================
# LOAD BASE THEME
# ============================================================

if not BASE.is_file():
    raise SystemExit(f"Base theme not found: {BASE}")

theme = json.loads(BASE.read_text(encoding="utf-8"))

theme["name"] = "Obsidian Sapphire Theme"
theme["type"] = "dark"
theme["semanticHighlighting"] = True

original_rules = deepcopy(theme.get("tokenColors", []))
rules = deepcopy(original_rules)

# ============================================================
# DISCOVER INSTALLED TEXTMATE GRAMMARS
# ============================================================

grammar_files = set()

for root in GRAMMAR_ROOTS:
    if not root.is_dir():
        continue

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        filename = path.name.lower()

        if filename.endswith((
            ".tmlanguage",
            ".tmlanguage.json",
            ".tmlanguage.plist",
        )):
            grammar_files.add(path.resolve())

# ============================================================
# EXTRACT ACTUAL SYNTAX SCOPES
# ============================================================

scopes = set()
scope_sources = defaultdict(set)

parsed_files = []
failed_files = []

scope_pattern = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_.-]*$"
)


def extract_scopes(node, source):

    if isinstance(node, dict):

        for key in ("name", "contentName"):

            value = node.get(key)

            if isinstance(value, str):

                for scope in value.split():

                    if (
                        "." in scope
                        and scope_pattern.fullmatch(scope)
                    ):
                        scopes.add(scope)
                        scope_sources[scope].add(source)

        for value in node.values():
            extract_scopes(value, source)

    elif isinstance(node, list):

        for value in node:
            extract_scopes(value, source)


for path in sorted(grammar_files):

    try:

        if path.name.lower().endswith(".json"):
            grammar = json.loads(
                path.read_text(encoding="utf-8-sig")
            )
        else:
            with path.open("rb") as file:
                grammar = plistlib.load(file)

        # Do not treat the grammar's display name
        # as a syntax token.
        for key in ("patterns", "repository", "injections"):
            extract_scopes(
                grammar.get(key, {}),
                path.name,
            )

        parsed_files.append(str(path))

    except Exception as error:
        failed_files.append({
            "file": str(path),
            "error": str(error),
        })

# ============================================================
# EXISTING THEME SELECTORS
# ============================================================

def get_selectors(token_rules):

    selectors = set()

    for rule in token_rules:

        value = rule.get("scope", [])

        if isinstance(value, str):
            value = [value]

        for item in value:
            for selector in item.split(","):
                selector = selector.strip()

                if selector:
                    selectors.add(selector)

    return selectors


existing = get_selectors(rules)

# Simple prefix matching is intentionally conservative.
# Full TextMate selector evaluation requires a scope stack.

simple_selectors = {
    selector
    for selector in existing
    if scope_pattern.fullmatch(selector)
}


def already_covered(scope):

    return any(
        scope == selector
        or scope.startswith(selector + ".")
        for selector in simple_selectors
    )

# ============================================================
# SAFE SCOPE CLASSIFICATION
# ============================================================

def classify(scope):

    # Structural containers must not receive
    # arbitrary foreground colors.
    if scope.startswith((
        "meta.",
        "source.",
        "text.",
        "embedded.",
    )):
        return None

    classifications = [
        ("invalid", "error"),
        ("comment", "comment"),

        ("constant.character.escape", "decorator"),
        ("constant.numeric", "number"),
        ("constant.language", "constant"),
        ("constant.other", "constant"),

        ("keyword.operator", "operator"),
        ("keyword", "keyword"),

        ("storage.type", "type"),
        ("storage.modifier", "keyword"),

        ("entity.name.function", "function"),
        ("entity.name.method", "function"),
        ("entity.name.type", "type"),
        ("entity.name.class", "type"),
        ("entity.name.namespace", "type"),
        ("entity.name.tag", "type"),

        ("entity.other.attribute-name", "property"),

        ("support.function", "function"),
        ("support.type", "type"),
        ("support.class", "type"),
        ("support.constant", "constant"),
        ("support.variable", "property"),

        ("variable.parameter", "number"),
        ("variable.other.property", "property"),
        ("variable.language", "constant"),
        ("variable", "foreground"),

        ("string", "string"),

        ("markup.heading", "function"),
        ("markup.bold", "number"),
        ("markup.italic", "keyword"),
        ("markup.inline.raw", "string"),
        ("markup.raw", "string"),
        ("markup.underline.link", "function"),
        ("markup.inserted", "constant"),
        ("markup.deleted", "error"),
        ("markup.changed", "number"),

        ("punctuation.definition.comment", "comment"),
        ("punctuation.definition.string", "string"),
    ]

    for prefix, category in classifications:

        if scope == prefix or scope.startswith(prefix + "."):
            return category

    return None

# ============================================================
# GENERATE MISSING RULES
# ============================================================

generated = defaultdict(list)
unclassified = []
covered = []

for scope in sorted(scopes):

    if already_covered(scope):
        covered.append(scope)
        continue

    category = classify(scope)

    if category is None:
        unclassified.append(scope)
        continue

    generated[category].append(scope)


for category, members in sorted(generated.items()):

    settings = {
        "foreground": P[category],
    }

    if category == "comment":
        settings["fontStyle"] = "italic"

    rules.append({
        "name": f"Universal — {category.title()}",
        "scope": sorted(set(members)),
        "settings": settings,
    })

# ============================================================
# SEMANTIC TOKEN COVERAGE
# ============================================================

semantic = deepcopy(theme.get("semanticTokenColors", {}))

standard_semantics = {
    "namespace": P["type"],
    "type": P["type"],
    "class": P["type"],
    "enum": P["type"],
    "interface": P["type"],
    "struct": P["type"],
    "typeParameter": P["type"],

    "parameter": P["number"],
    "variable": P["foreground"],
    "property": P["property"],
    "enumMember": P["constant"],

    "function": P["function"],
    "method": P["function"],
    "macro": P["decorator"],
    "decorator": P["decorator"],

    "keyword": P["keyword"],
    "modifier": P["keyword"],
    "operator": P["operator"],

    "string": P["string"],
    "number": P["number"],
    "regexp": P["string"],
    "comment": {
        "foreground": P["comment"],
        "italic": True,
    },

    "variable.readonly": P["constant"],
    "property.readonly": P["constant"],
    "*.deprecated": {
        "strikethrough": True,
    },
}

# Preserve existing semantic decisions.
for selector, settings in standard_semantics.items():
    semantic.setdefault(selector, settings)

# ============================================================
# READ EXTENSION SEMANTIC TOKEN DECLARATIONS
# ============================================================

semantic_types = {}
semantic_modifiers = {}
semantic_scope_maps = []

for root in GRAMMAR_ROOTS:

    if not root.is_dir():
        continue

    for path in root.glob("*/package.json"):

        try:
            manifest = json.loads(
                path.read_text(encoding="utf-8-sig")
            )
        except Exception:
            continue

        contributes = manifest.get("contributes", {})

        for token in contributes.get("semanticTokenTypes", []):

            token_id = token.get("id")

            if token_id:
                semantic_types[token_id] = token

        for modifier in contributes.get(
            "semanticTokenModifiers", []
        ):

            modifier_id = modifier.get("id")

            if modifier_id:
                semantic_modifiers[modifier_id] = modifier

        semantic_scope_maps.extend(
            contributes.get("semanticTokenScopes", [])
        )

# Resolve custom types using declared inheritance.
for _ in range(len(semantic_types) + 1):

    changed = False

    for token_id, definition in semantic_types.items():

        if token_id in semantic:
            continue

        parent = definition.get("superType")

        if parent in semantic:
            semantic[token_id] = deepcopy(semantic[parent])
            changed = True

    if not changed:
        break

# ============================================================
# WRITE GENERATED THEME
# ============================================================

from language_styles import apply_language_styles

apply_language_styles(rules, semantic, P)

theme["tokenColors"] = rules
theme["semanticTokenColors"] = semantic

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

OUTPUT.write_text(
    json.dumps(theme, indent=4, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

# Validate output JSON.
validated = json.loads(
    OUTPUT.read_text(encoding="utf-8")
)

# Ensure that workbench colors remain unchanged.
base_theme = json.loads(BASE.read_text(encoding="utf-8"))

assert validated.get("colors") == base_theme.get("colors")

# Ensure that original TextMate rules remain intact.
assert validated["tokenColors"][:len(original_rules)] == original_rules

# ============================================================
# GENERATE AUDIT REPORTS
# ============================================================

(REPORTS / "all-scopes.txt").write_text(
    "\n".join(sorted(scopes)) + "\n",
    encoding="utf-8",
)

(REPORTS / "unclassified-scopes.txt").write_text(
    "\n".join(
        scope + "\t" + ", ".join(sorted(scope_sources[scope]))
        for scope in unclassified
    ) + "\n",
    encoding="utf-8",
)

(REPORTS / "semantic-tokens.json").write_text(
    json.dumps({
        "types": semantic_types,
        "modifiers": semantic_modifiers,
        "scopeMappings": semantic_scope_maps,
    }, indent=4, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

summary = {
    "grammarFilesFound": len(grammar_files),
    "grammarFilesParsed": len(parsed_files),
    "grammarFilesFailed": failed_files,
    "uniqueScopes": len(scopes),
    "existingPrefixCoverage": len(covered),
    "newExplicitScopes": sum(
        len(items) for items in generated.values()
    ),
    "unclassifiedScopes": len(unclassified),
    "originalTextMateRules": len(original_rules),
    "finalTextMateRules": len(rules),
    "semanticRules": len(semantic),
    "customSemanticTypes": len(semantic_types),
    "workbenchColors": len(theme.get("colors", {})),
}

(REPORTS / "build-report.json").write_text(
    json.dumps(summary, indent=4) + "\n",
    encoding="utf-8",
)

# ============================================================
# BUILD SUMMARY
# ============================================================

print()
print("=" * 64)
print("OBSIDIAN SAPPHIRE THEME — VISUAL STUDIO CODE")
print("=" * 64)

print(f"Grammar files found      : {len(grammar_files)}")
print(f"Grammar files parsed     : {len(parsed_files)}")
print(f"Grammar files failed     : {len(failed_files)}")
print(f"Unique TextMate scopes   : {len(scopes)}")
print(f"Existing prefix coverage : {len(covered)}")
print(f"New explicit scopes      : {summary['newExplicitScopes']}")
print(f"Unclassified scopes      : {len(unclassified)}")
print(f"Original TextMate rules  : {len(original_rules)}")
print(f"Final TextMate rules     : {len(rules)}")
print(f"Semantic token rules     : {len(semantic)}")
print(f"Custom semantic types    : {len(semantic_types)}")
print(f"Workbench colors         : {summary['workbenchColors']}")
print("JSON validation          : PASSED")
print("Workbench preservation   : PASSED")
print("Original rule retention  : PASSED")
print("=" * 64)
print(f"Theme  : {OUTPUT}")
print(f"Reports: {REPORTS}")
print("=" * 64)
