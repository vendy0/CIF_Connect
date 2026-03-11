def spaces_to_tabs(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        stripped = line.lstrip(" ")
        leading_spaces = len(line) - len(stripped)

        tabs = "\t" * (leading_spaces // 4)
        remaining_spaces = " " * (leading_spaces % 4)

        new_lines.append(tabs + remaining_spaces + stripped)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

# utilisation
spaces_to_tabs("src/chat_view.py")
