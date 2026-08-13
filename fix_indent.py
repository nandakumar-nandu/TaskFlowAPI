import os
for filename in os.listdir('tests'):
    if not filename.startswith('test_') or not filename.endswith('.py'):
        continue
    filepath = os.path.join('tests', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('\n        \"\"\"', '\n    \"\"\"')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
print('Fixed indentation!')
