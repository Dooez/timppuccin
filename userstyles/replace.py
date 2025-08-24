import os


def replace_colors(color_map_file, input_json_file, output_json_file):
    """
    Automates hex color code replacement based on a provided map.

    Args:
        color_map_file (str): Path to the file containing the color map.
                              Format: #old_color:#new_color -- comment
        input_json_file (str): Path to the JSON file to be modified.
        output_json_file (str): Path to save the modified JSON content.
    """
    # 1. Build the Replacement Map
    replacement_map = {}
    if not os.path.exists(color_map_file):
        print(f"Error: The color map file '{color_map_file}' was not found.")
        return

    try:
        with open(color_map_file, "r") as f:
            for line in f:
                # Ignore empty lines and lines without a colon
                if not line.strip() or ":" not in line:
                    continue

                # Split the line at the comment marker and get the first part
                line_without_comment = line.split("--")[0].strip()

                # Split the cleaned line into old and new colors
                parts = line_without_comment.split(":")
                if len(parts) == 2:
                    old_color = parts[0].strip()
                    new_color = parts[1].strip()
                    # Ensure both are valid-looking hex codes
                    if old_color.startswith("#") and new_color.startswith("#"):
                        replacement_map[old_color] = new_color

        print(
            f"Successfully built a replacement map with {len(replacement_map)} entries."
        )

    except IOError as e:
        print(f"Error reading the color map file: {e}")
        return

    # Handle the case where the map is empty
    if not replacement_map:
        print("Warning: The replacement map is empty. No colors will be replaced.")
        return

    # 2. Apply Replacements
    if not os.path.exists(input_json_file):
        print(f"Error: The input JSON file '{input_json_file}' was not found.")
        return

    try:
        with open(input_json_file, "r") as f:
            content = f.read()

        # Iterate through the map and replace all occurrences
        for old_color, new_color in replacement_map.items():
            content = content.replace(old_color, new_color)

        print(
            f"Successfully applied color replacements to the content of '{input_json_file}'."
        )

    except IOError as e:
        print(f"Error reading the input JSON file: {e}")
        return

    # 3. Save the Output
    try:
        with open(output_json_file, "w") as f:
            f.write(content)

        print(
            f"The modified content has been successfully saved to '{output_json_file}'."
        )

    except IOError as e:
        print(f"Error writing to the output file: {e}")


if __name__ == "__main__":
    # Define the file paths
    COLOR_MAP_FILE = "color_map.txt"
    INPUT_JSON_FILE = "import.json"
    OUTPUT_JSON_FILE = "import_replaced.json"

    # Run the main function
    replace_colors(COLOR_MAP_FILE, INPUT_JSON_FILE, OUTPUT_JSON_FILE)
