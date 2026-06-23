"""
Quick script to count and list all exercises from chapter files
"""
import re
from pathlib import Path

chapters_dir = Path("source/chapters")
exercise_pattern = re.compile(r'\\begin\{exercise\}')

total_exercises = 0
for ch_file in sorted(chapters_dir.glob("ch*.tex")):
    with open(ch_file, 'r', encoding='utf-8') as f:
        content = f.read()

    count = len(exercise_pattern.findall(content))
    ch_num = re.search(r'ch(\d+)', ch_file.name).group(1)
    print(f"Chapter {ch_num}: {count} exercises")
    total_exercises += count

print(f"\nTotal: {total_exercises} exercises")
