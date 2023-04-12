import sys

filename = sys.argv[1]
with open(filename) as fp:
    lines = fp.readlines()

updates = []
last_example_start = None
for i, line in enumerate(lines):
    if line == f"{' ' * 8}**Examples**\n":
        last_example_start = i
    if line == f'{" " * 8}"""\n' and last_example_start is not None:
        updates.append((last_example_start, i))
        last_example_start = None

offset = 0
for start, end in updates:
    old_lines = lines[start + offset : end + offset]
    new_lines = [
        f'{" " * 8}.. tab-set::\n',
        "\n",
        f'{" " * 12}.. tab-item:: Example Usage\n',
        "\n",
    ] + [((" " * 8) + o if o != "\n" else o) for o in old_lines[2:]]
    lines = lines[: start + offset] + new_lines + lines[end + offset :]
    offset += len(new_lines) - len(old_lines)

with open(filename, "w") as fp:
    fp.write("".join(lines))
