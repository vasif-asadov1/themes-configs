
# ============================================================
# OBSIDIAN SAPPHIRE THEME
# Language-specific syntax and semantic refinements
# ============================================================

def apply_language_styles(rules, semantic, palette):

    p = palette

    # ========================================================
    # PYTHON — PYLANCE
    # ========================================================

    semantic.update({
        "selfParameter:python": p["decorator"],
        "clsParameter:python": p["decorator"],
        "magicFunction:python": p["function"],
        "builtinConstant:python": p["constant"],

        "parameter.keywordArgument:python": p["number"],
        "string.escapeCharacter:python": p["decorator"],

        "function.decorator:python": p["decorator"],
        "class.decorator:python": p["decorator"],

        "variable.callable:python": p["function"],
        "property.callable:python": p["function"],

        "*.typeHint:python": p["type"],

        "*.typeHintComment:python": {
            "foreground": p["comment"],
            "italic": True,
        },

        "*.invalid:python": p["error"],

        "colon:python": p["operator"],
        "semicolon:python": p["foreground"],
        "arrow:python": p["operator"],
    })

    # ========================================================
    # TYPST — TINYMIST
    # ========================================================

    semantic.update({
        "bool:typst": p["constant"],
        "punct:typst": p["operator"],
        "escape:typst": p["decorator"],

        "link:typst": {
            "foreground": p["function"],
            "underline": True,
        },

        "raw:typst": p["string"],
        "label:typst": p["decorator"],
        "ref:typst": p["property"],

        "heading:typst": {
            "foreground": p["function"],
            "bold": True,
        },

        "marker:typst": p["constant"],

        "term:typst": {
            "foreground": p["number"],
            "bold": True,
        },

        "delim:typst": p["operator"],
        "delim.math:typst": p["decorator"],
        "operator.math:typst": p["operator"],
        "pol:typst": p["property"],
        "error:typst": p["error"],
        "text:typst": p["foreground"],

        "*.math:typst": p["type"],

        "*.strong:typst": {
            "bold": True,
        },

        "*.emph:typst": {
            "italic": True,
        },

        "*.strong.emph:typst": {
            "bold": True,
            "italic": True,
        },
    })

    # ========================================================
    # TOML — EVEN BETTER TOML
    # ========================================================

    semantic.update({
        "tomlArrayKey": p["property"],
        "tomlTableKey": p["property"],
    })

    # ========================================================
    # LANGUAGE-SPECIFIC TEXTMATE RULES
    # ========================================================

    def add_rule(name, scopes, color, font_style=None):

        settings = {
            "foreground": color,
        }

        if font_style is not None:
            settings["fontStyle"] = font_style

        rules.append({
            "name": name,
            "scope": scopes,
            "settings": settings,
        })

    # Python
    add_rule(
        "Python — Magic Methods",
        ["support.function.magic.python"],
        p["function"],
    )

    add_rule(
        "Python — Keyword Arguments",
        ["variable.parameter.function-call.python"],
        p["number"],
    )

    add_rule(
        "Python — Self and Class Parameters",
        [
            "variable.parameter.function.language.special.self.python",
            "variable.parameter.function.language.special.cls.python",
        ],
        p["decorator"],
    )

    # Typst
    add_rule(
        "Typst — Headings",
        ["markup.heading.typst"],
        p["function"],
        "bold",
    )

    add_rule(
        "Typst — Mathematics",
        ["markup.math.typst"],
        p["type"],
    )

    add_rule(
        "Typst — Mathematical Operators",
        ["keyword.operator.math.typst"],
        p["operator"],
    )

    add_rule(
        "Typst — Mathematics Delimiters",
        ["punctuation.definition.math.typst"],
        p["decorator"],
    )

    add_rule(
        "Typst — Labels",
        ["entity.name.label.typst"],
        p["decorator"],
    )

    add_rule(
        "Typst — References",
        ["markup.other.reference.typst"],
        p["property"],
    )

    add_rule(
        "Typst — Raw Text",
        ["markup.other.raw.typst"],
        p["string"],
    )

    add_rule(
        "Typst — Strong Emphasis",
        ["markup.bold.typst"],
        p["number"],
        "bold",
    )

    add_rule(
        "Typst — Italic Emphasis",
        ["markup.italic.typst"],
        p["keyword"],
        "italic",
    )

    add_rule(
        "Typst — Hyperlinks",
        ["markup.underline.link.typst"],
        p["function"],
        "underline",
    )

    add_rule(
        "Typst — List Markers",
        ["punctuation.definition.list.begin.typst"],
        p["constant"],
    )

    # TOML
    add_rule(
        "TOML — Properties",
        ["support.type.property-name.toml"],
        p["property"],
    )

    add_rule(
        "TOML — Array and Table Keys",
        [
            "support.type.property-name.array.toml",
            "support.type.property-name.table.toml",
        ],
        p["property"],
    )

    # ========================================================
    # RAINBOW CSV — TEN DISTINCT COLUMN COLORS
    # ========================================================

    rainbow = [
        ("rainbow1", "#D4DEEB"),
        ("keyword.rainbow2", "#B49AF0"),
        ("entity.name.function.rainbow3", "#64B5F6"),
        ("comment.rainbow4", "#59C9C2"),
        ("string.rainbow5", "#89C9A6"),
        ("variable.parameter.rainbow6", "#E7C080"),
        ("constant.numeric.rainbow7", "#ED7786"),
        ("entity.name.type.rainbow8", "#98FFB3"),
        ("markup.bold.rainbow9", "#D0B8FF"),
        ("invalid.rainbow10", "#91CCFF"),
    ]

    for index, (scope, color) in enumerate(rainbow, 1):

        add_rule(
            f"Rainbow CSV — Column {index}",
            [scope],
            color,
            "",
        )

        semantic[f"rainbow{index}:dynamic csv"] = {
            "foreground": color,
            "bold": False,
            "italic": False,
            "underline": False,
        }
