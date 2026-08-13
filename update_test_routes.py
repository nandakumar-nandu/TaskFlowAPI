import os
import re

for filename in os.listdir('tests'):
    if not filename.startswith('test_') or not filename.endswith('.py'):
        continue
    filepath = os.path.join('tests', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace URLs in client requests
    for prefix in ['/auth', '/users', '/tasks', '/categories']:
        # Replace occurrences like client.post("/auth...") or client.get("/auth...")
        content = re.sub(rf'([\'"]){prefix}', rf'\1/api/v1{prefix}', content)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
print('Replaced paths in tests!')
