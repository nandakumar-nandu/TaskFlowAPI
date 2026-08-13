import os
import re

for filename in os.listdir('tests'):
    if not filename.startswith('test_') or not filename.endswith('.py'):
        continue
    filepath = os.path.join('tests', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to match docstrings in async def test_ functions
    pattern = re.compile(r'(async def test_[a-zA-Z0-9_]+\(.*?\):\s*)\"\"\"(.*?)\"\"\"', re.DOTALL)
    
    def replacer(match):
        func_def = match.group(1)
        doc_content = match.group(2)
        
        # Try to extract the scenario or the first meaningful sentence
        lines = [line.strip() for line in doc_content.split('\n') if line.strip()]
        new_doc = ''
        if lines:
            first_line = lines[0]
            first_line = re.sub(r'^🧪 Scenario:\s*', '', first_line)
            first_line = re.sub(r'^🧪 Test\s*', '', first_line)
            first_line = re.sub(r'^🧪\s*', '', first_line)
            # Ensure it ends with a period if not
            if not first_line.endswith('.'):
                first_line += '.'
            # Fix capitalization
            first_line = first_line[0].upper() + first_line[1:]
            new_doc = f'    """{first_line}"""'
        else:
            new_doc = '    """Test scenario."""'
            
        return f'{func_def}{new_doc}'
        
    new_content = pattern.sub(replacer, content)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
print('Done!')
