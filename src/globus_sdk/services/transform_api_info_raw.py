import re
import sys

filename = sys.argv[1]
with open(filename) as fp:
    lines = fp.readlines()

api_call_info_pat = re.compile(r"\s{8}``(GET|PUT|POST|PATCH|DELETE|HEAD)")
end_line_pat = re.compile(r'\s{8}"""(  # noqa: E501)?\n')

updates = []
found_line = None
for i, line in enumerate(lines):
    if api_call_info_pat.match(line):
        found_line = i
    elif end_line_pat.match(line) and found_line is not None:
        updates.append((found_line, i))
        found_line = None


offset = 0
for found_line, move_target in updates:
    old_line = lines[found_line + offset]
    lines = lines[: found_line + offset] + lines[found_line + offset + 2 :]
    offset -= 2

    new_lines = [
        "\n",
        f'{" " * 12}.. tab-item:: API Info\n',
        "\n",
        f'{" " * 8}{old_line}',
    ]
    lines = lines[: move_target + offset] + new_lines + lines[move_target + offset :]
    offset += 4

with open(filename, "w") as fp:
    fp.write("".join(lines))
