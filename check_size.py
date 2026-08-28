import os, glob

files = sorted(glob.glob('C++学习/**/*.md', recursive=True) + glob.glob('ROS学习/**/*.md', recursive=True))
maxlen = 0
for f in files:
    if os.path.basename(f) == 'README.md':
        continue
    size = os.path.getsize(f)
    maxlen = max(maxlen, size)
    print(f"{os.path.basename(f)}: {size} bytes")
print(f"\nMax file size: {maxlen} bytes")
