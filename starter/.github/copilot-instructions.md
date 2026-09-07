# Copilot Instructions – Sudoku Refactor Project

## Style & Structure
- Use modern Python (Flask) best practices, PEP8 formatting
- Organize code into logical modules (e.g., sudoku_logic.py, routes.py, static/js, templates/)
- Use clear, descriptive variable/function names
- Add comments/docstrings for non-obvious logic

## Error Handling
- Handle invalid input gracefully, no crashes
- Validate all Sudoku moves server-side

## Frontend
- Use plain CSS
- Layout must work in light + dark mode, mobile + desktop
- 3x3 squares must alternate colors clearly

## Testing
- Every new feature should have a matching test where practical
- Don't break existing passing tests when adding new features

## Working Style
- Suggest one logical change at a time, not massive rewrites
- Explain any suggestion that uses an unfamiliar library/pattern