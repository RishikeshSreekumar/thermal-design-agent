import os
 
 
output_file = "entire_codebase.txt"
 
# Folders to exclude
EXCLUDE_DIRS = {
    "venv",
    ".git",
    "__pycache__",
    ".idea",
    ".vscode",
}
 
# Text file types to include in the flattened snapshot
INCLUDE_EXTENSIONS = {
    ".py",
    ".md",
}
 
 
def generate_tree(
    start_path: str = ".",
) -> str:
    """
    Generate a text-based project tree.
    """
 
    tree_lines = []
 
    for root, dirs, files in os.walk(
        start_path
    ):
        # Remove excluded directories from traversal
        dirs[:] = sorted(
            directory
            for directory in dirs
            if directory not in EXCLUDE_DIRS
        )
 
        level = (
            root.replace(
                start_path,
                "",
            ).count(os.sep)
        )
 
        indent = "│   " * level
 
        folder_name = (
            os.path.basename(root)
            if root != start_path
            else os.path.basename(
                os.path.abspath(start_path)
            )
        )
 
        tree_lines.append(
            f"{indent}📁 {folder_name}/"
        )
 
        sub_indent = "│   " * (
            level + 1
        )
 
        for file in sorted(files):
            if file == output_file:
                continue
 
            tree_lines.append(
                f"{sub_indent}📄 {file}"
            )
 
    return "\n".join(
        tree_lines
    )
 
 
with open(
    output_file,
    "w",
    encoding="utf-8",
) as outfile:
 
    # ==================================================
    # PROJECT TREE
    # ==================================================
 
    outfile.write(
        "=" * 80 + "\n"
    )
 
    outfile.write(
        "PROJECT STRUCTURE\n"
    )
 
    outfile.write(
        "=" * 80 + "\n\n"
    )
 
    outfile.write(
        generate_tree()
    )
 
    outfile.write(
        "\n\n"
    )
 
    # ==================================================
    # FILE CONTENTS
    # ==================================================
 
    outfile.write(
        "=" * 80 + "\n"
    )
 
    outfile.write(
        "FILE CONTENTS\n"
    )
 
    outfile.write(
        "=" * 80 + "\n"
    )
 
    for root, dirs, files in os.walk(
        "."
    ):
        dirs[:] = sorted(
            directory
            for directory in dirs
            if directory not in EXCLUDE_DIRS
        )
 
        for file in sorted(files):
 
            if file == output_file:
                continue
 
            extension = os.path.splitext(
                file
            )[1].lower()
 
            if (
                extension
                not in INCLUDE_EXTENSIONS
            ):
                continue
 
            file_path = os.path.join(
                root,
                file,
            )
 
            outfile.write(
                f"\n\n{'=' * 80}\n"
                f"FILE: {file_path}\n"
                f"{'=' * 80}\n\n"
            )
 
            try:
                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore",
                ) as infile:
                    outfile.write(
                        infile.read()
                    )
 
            except Exception as exc:
                outfile.write(
                    "[ERROR READING FILE: "
                    f"{exc}]\n"
                )
 
 
print(
    f"Codebase exported to: "
    f"{output_file}"
)