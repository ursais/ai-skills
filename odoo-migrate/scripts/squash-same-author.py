#!/usr/bin/env python3
"""Git rebase sequence editor: fixup consecutive commits from the same author."""
import subprocess
import sys

todo_path = sys.argv[1]
with open(todo_path) as f:
    lines = f.readlines()

out = []
prev_author = None
for line in lines:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        out.append(line)
        continue
    parts = stripped.split()
    if parts[0] not in ("pick", "fixup", "squash", "reword", "edit", "drop"):
        out.append(line)
        continue
    sha = parts[1]
    author = subprocess.check_output(
        ["git", "log", "-1", "--format=%ae", sha], text=True
    ).strip()
    if prev_author == author:
        out.append(f"fixup {sha}\n")
    else:
        out.append(f"pick {sha}\n")
        prev_author = author

with open(todo_path, "w") as f:
    f.writelines(out)
