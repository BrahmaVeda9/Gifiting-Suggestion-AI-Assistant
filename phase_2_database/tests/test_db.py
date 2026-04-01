import pytest
from unittest.mock import patch

# Mocking the Supabase client so we can test logic independently of external service availability
@patch("database.get_supabase")
def test_mock_create_user(mock_get_supabase):
    # Setup mock
    mock_db = mock_get_supabase.return_value
    mock_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": "123", "email": "test@example.com"}]
    
    # Run Function
    from crud import create_user
    user = create_user("test@example.com")
    
    # Assert
    assert user["email"] == "test@example.com"
