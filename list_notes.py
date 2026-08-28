import os, json, glob

base = os.getcwd()
files = []

for pattern in ['C++学习/**/*.md', 'ROS学习/**/*.md']:
    for p in sorted(glob.glob(os.path.join(base, pattern), recursive=True)):
        if os.path.basename(p) == 'README.md':
            continue
        rel = os.path.relpath(p, base)
        files.append(rel)

for f in files:
    print(f)
print(f"\nTotal: {len(files)} files")
