import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.config import Config  # noqa: E402
from bot.storage import Storage  # noqa: E402


@pytest.fixture
def cfg(tmp_path):
    c = Config()
    c.data_dir = tmp_path
    return c


@pytest.fixture
def storage(tmp_path):
    s = Storage(tmp_path / "test.db")
    yield s
    s.close()
