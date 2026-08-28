import os, json, glob

def read_file_raw(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

base = os.path.dirname(os.path.abspath(__file__))
files = []
for pattern in [os.path.join(base, 'C++学习', '**', '*.md'), os.path.join(base, 'ROS学习', '**', '*.md')]:
    for p in sorted(glob.glob(pattern, recursive=True)):
        if os.path.basename(p) == 'README.md':
            continue
        files.append(p)

data = {}
for path in files:
    key = os.path.splitext(os.path.basename(path))[0]
    if '_' in key:
        parts = key.split('_', 1)
        if parts[0].isdigit():
            key = parts[1]
    content = read_file_raw(path)
    data[key] = content

with open('notes_content.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Saved {len(data)} notes to notes_content.json")
