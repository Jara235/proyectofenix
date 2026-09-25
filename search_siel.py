import os, re

for root, dirs, files in os.walk('.'):
    # skip .git and virtualenvs
    if '.git' in root or '__pycache__' in root or 'node_modules' in root:
        continue
    for file in files:
        if file.endswith(('.py', '.sql', '.json', '.html', '.js', '.txt', '.md', '.docx', '.xlsx')):
            filepath = os.path.join(root, file)
            try:
                if file.endswith(('.py', '.sql', '.json', '.html', '.js', '.txt', '.md')):
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if re.search(r'\bsiel\b', content, re.IGNORECASE):
                            print(f"Match in {filepath}")
            except Exception as e:
                pass
