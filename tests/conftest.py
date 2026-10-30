# pytest configuration

import pytest
from panther.config import config

@pytest.fixture(scope="session")
def temp_db(tmp_path_factory):
    """Create a temporary SQLite DB for the duration of the test session."""
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    # Ensure the config points to the temporary DB for the tests
    original = config.db_path
    config.db_path = db_path
    yield db_path
    # Restore original path after tests
    config.db_path = original
