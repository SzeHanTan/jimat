"""
CRUD operations (Create, Read, Update, Delete).

This is the data access layer - all database queries go here.
Routes should NOT directly query the database; they call these functions instead.

Why this pattern:
- Single responsibility: CRUD functions only handle database logic
- Reusability: Multiple routes can use the same CRUD function
- Testability: Easy to mock CRUD functions in tests
- Maintainability: Change database logic in one place
"""
