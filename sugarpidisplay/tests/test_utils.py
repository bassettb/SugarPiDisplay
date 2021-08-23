from ..utils import get_stale_minutes

def test_get_stale_minutes():
    assert get_stale_minutes() == 20
