import os, re, glob

def extract_knowledge_and_code(content):
    """提取核心知识点和代码示例部分"""
    lines = content.split('\n')
    result = []
    in_knowledge = False
    in_code = False
    
    for line in lines:
        # 检测核心知识点开始
        if '## 📚 核心知识点' in line:
            in_knowledge = True
            result.append(line)
            continue
        
        # 检测代码示例开始
        if '## 💻 代码示例' in line:
            in_knowledge = False
            in_code = True
            result.append('')
            result.append(line)
            continue
        
        # 检测代码示例结束（下一个 ## 或 ---）
        if in_code and (line.startswith('## ') or line.startswith('---')):
            in_code = False
            break
        
        if in_knowledge or in_code:
            result.append(line)
    
    return '\n'.join(result).strip()

def process_all_files():
    base = os.path.dirname(os.path.abspath(__file__))
    files = []
    for pattern in [os.path.join(base, 'C++学习', '**', '*.md'), os.path.join(base, 'ROS学习', '**', '*.md')]:
        for p in sorted(glob.glob(pattern, recursive=True)):
            if os.path.basename(p) == 'README.md':
                continue
            files.append(p)
    
    for i, path in enumerate(files):
        key = os.path.splitext(os.path.basename(path))[0]
        if '_' in key:
            parts = key.split('_', 1)
            if parts[0].isdigit():
                key = parts[1]
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        extracted = extract_knowledge_and_code(content)
        
        out_path = f'note_clean_{i}.txt'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(extracted)
        
        print(f"{key}: original {len(content)} chars -> extracted {len(extracted)} chars ({len(extracted)/len(content)*100:.0f}%)")

if __name__ == '__main__':
    process_all_files()
