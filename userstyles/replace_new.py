import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_INPUT_JSON = "import.json"
DEFAULT_OUTPUT_JSON = "import_replaced.json"
DEFAULT_PALETTE_FILE = "my_palette.txt"

PALETTE_DEFAULTS_RE = re.compile(
    r"(?m)^(?P<indent>[ \t]*)#lib\.palette\(\);\n(?P=indent)#lib\.defaults\(\);"
)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Insert the contents of the palette file after #lib.palette(); "
            "and before #lib.defaults(); in sourceCode entries."
        )
    )
    parser.add_argument("input_json", nargs="?", default=DEFAULT_INPUT_JSON)
    parser.add_argument("output_json", nargs="?", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--palette", default=DEFAULT_PALETTE_FILE)
    return parser.parse_args()


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"Error: '{path}' was not found.")
    except OSError as exc:
        raise SystemExit(f"Error reading '{path}': {exc}")


def load_json(path):
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Error parsing '{path}' as JSON: {exc}")


def format_palette(palette, indent):
    lines = palette.rstrip("\n").splitlines()
    return "\n".join(f"{indent}{line}" if line else "" for line in lines)


def insert_palette(source_code, palette):
    def replace_match(match):
        indent = match.group("indent")
        indented_palette = format_palette(palette, indent)
        return (
            f"{indent}#lib.palette();\n"
            f"{indented_palette}\n"
            f"{indent}#lib.defaults();"
        )

    return PALETTE_DEFAULTS_RE.subn(replace_match, source_code)


def replace_source_code_values(value, palette):
    replacements = 0

    if isinstance(value, dict):
        for key, nested_value in value.items():
            if key == "sourceCode" and isinstance(nested_value, str):
                value[key], count = insert_palette(nested_value, palette)
                replacements += count
            else:
                replacements += replace_source_code_values(nested_value, palette)
    elif isinstance(value, list):
        for item in value:
            replacements += replace_source_code_values(item, palette)

    return replacements


def write_json(path, data):
    try:
        content = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Error writing '{path}': {exc}")


def main():
    args = parse_args()
    input_path = Path(args.input_json)
    output_path = Path(args.output_json)
    palette_path = Path(args.palette)

    palette = read_text(palette_path)
    if not palette.strip():
        raise SystemExit(f"Error: '{palette_path}' is empty.")

    data = load_json(input_path)
    replacements = replace_source_code_values(data, palette)

    if replacements == 0:
        print(
            "Warning: no '#lib.palette();' followed by '#lib.defaults();' "
            "blocks were found.",
            file=sys.stderr,
        )

    write_json(output_path, data)
    print(f"Wrote '{output_path}' with {replacements} palette insertion(s).")


if __name__ == "__main__":
    main()
