import os
import re

replacements = {
    r'raise HTTPException\(\s*status_code=status.HTTP_404_NOT_FOUND,\s*detail="Task not found"\s*\)': 'raise TaskNotFoundError()',
    r'raise HTTPException\(\s*status_code=status.HTTP_403_FORBIDDEN,\s*detail="You do not have permission to access this task"\s*\)': 'raise TaskForbiddenError()',
    r'raise HTTPException\(\s*status_code=status.HTTP_404_NOT_FOUND,\s*detail="Category not found"\s*\)': 'raise CategoryNotFoundError()',
    r'raise HTTPException\(\s*status_code=status.HTTP_403_FORBIDDEN,\s*detail="You do not have permission to access this category"\s*\)': 'raise CategoryForbiddenError()',
    r'raise HTTPException\(\s*status_code=status.HTTP_404_NOT_FOUND,\s*detail="Comment not found"\s*\)': 'raise CommentNotFoundError()',
    r'raise HTTPException\(\s*status_code=status.HTTP_403_FORBIDDEN,\s*detail="You do not have permission to edit this comment"\s*\)': 'raise CommentForbiddenError()',
    r'raise HTTPException\(\s*status_code=status.HTTP_403_FORBIDDEN,\s*detail="You do not have permission to delete this comment"\s*\)': 'raise CommentForbiddenError(detail="You do not have permission to delete this comment")',
    r'raise HTTPException\(\s*status_code=status.HTTP_401_UNAUTHORIZED,\s*detail="Invalid email or password"\s*\)': 'raise InvalidCredentialsError()',
    r'raise HTTPException\(\s*status_code=status.HTTP_409_CONFLICT,\s*detail="Email is already registered"\s*\)': 'raise DuplicateEmailError()',
}

files_to_update = [
    'app/services/task_service.py',
    'app/services/category_service.py',
    'app/services/comment_service.py',
    'app/routes/tasks.py',
    'app/routes/categories.py',
    'app/routes/auth.py',
    'app/routes/users.py'
]

for filepath in files_to_update:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add imports if we are doing replacements
    original_content = content
    for pattern, repl in replacements.items():
        content = re.sub(pattern, repl, content)
        
    if content != original_content:
        # Add import at the top (under from fastapi import ...)
        import_str = "from app.core.exceptions import TaskNotFoundError, TaskForbiddenError, CategoryNotFoundError, CategoryForbiddenError, CommentNotFoundError, CommentForbiddenError, InvalidCredentialsError, DuplicateEmailError\n"
        if "from fastapi import" in content:
            content = content.replace("from fastapi import HTTPException", "from fastapi import status") # just in case
            content = content.replace("from fastapi import status, HTTPException", "from fastapi import status")
            content = re.sub(r'(from fastapi import.*?\n)', r'\1' + import_str, content, count=1)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
print('Done updating exceptions!')
