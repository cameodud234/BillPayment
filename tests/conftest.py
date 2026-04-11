import os
import pytest

TEST_DB_PATH = os.path.abspath("data/test_app.db")
os.environ["DB_PATH"] = TEST_DB_PATH

@pytest.fixture(scope="session", autouse=True)
def test_db():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    from app.db.database import init_db
    init_db()

    yield TEST_DB_PATH

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)