import pytest

from lib.cmcut import SilentSection

class TestSilentSection:
    def test_init(self):
        """Test init."""
        silent_section = SilentSection(0, 10, 2)
        assert silent_section.frame_per_sec == 2
        assert silent_section.start_sec == 0
        assert silent_section.end_sec == 5
    def test_init_fail(self):
        """Test init with failure."""
        with pytest.raises(Exception) as e:
            silent_section = SilentSection(0, 10, -1)
        assert "frame_per_sec must be positive:" in str(e.value)
    def test_center_sec(self):
        silent_section = SilentSection(0, 10, 2)
        assert silent_section.center_sec() == 5./2

