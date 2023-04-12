import re
import sys

filename = sys.argv[1]
with open(filename) as fp:
    lines = fp.readlines()

decorator_pat = re.compile(r'\s{4}\@utils\.doc_api_method\("([^"]+)", "([^"]+)"\)')
end_line_pat = re.compile(r'\s{8}"""(  # noqa: E501)?\n')

updates = []
found_line_data = None
found_docstring_start = False
for i, line in enumerate(lines):
    if m := decorator_pat.match(line):
        found_line_data = i, m.group(1), m.group(2)
        found_docstring_start = False
    elif end_line_pat.match(line) and found_line_data is not None:
        if not found_docstring_start:
            found_docstring_start = True
        else:
            updates.append(
                (found_line_data[0], i, found_line_data[1], found_line_data[2])
            )
            found_line_data = None


offset = 0
for found_line, move_target, link_name, link_ref in updates:
    lines = lines[: found_line + offset] + lines[found_line + offset + 1 :]
    offset -= 1

    new_lines = [
        "\n",
        f'{" " * 16}.. extdoclink:: {link_name}\n',
        f'{" " * 20}:ref: {link_ref}\n',
    ]
    lines = lines[: move_target + offset] + new_lines + lines[move_target + offset :]
    offset += 3

with open(filename, "w") as fp:
    fp.write("".join(lines))
