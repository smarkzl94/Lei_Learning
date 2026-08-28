import os, glob

base = os.path.dirname(os.path.abspath(__file__))
files = []
for pattern in [os.path.join(base, 'C++学习', '**', '*.md'), os.path.join(base, 'ROS学习', '**', '*.md')]:
    for p in sorted(glob.glob(pattern, recursive=True)):
        if os.path.basename(p) == 'README.md':
            continue
        files.append(p)

# Process batch 2: files 1-5 (indices 1-5)
batch = files[1:6]  # 运算符与表达式, 控制流程, 函数, 指针与引用, 数组与字符串
for i, path in enumerate(batch):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    out_path = f'note_{i+1}.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Written to {out_path}")
