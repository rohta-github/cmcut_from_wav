import pytest

from lib.cmcut import SilentSection, DurationSecUnits

class TestSilentSection:
    def test_init(self):
        """Test init."""
        silent_section = SilentSection(0, 10, 2)
        assert silent_section.frame_per_sec == 2
        assert silent_section.start_sec == 0
        assert silent_section.end_sec == 5
        silent_section = SilentSection(0, 16000)
        assert silent_section.frame_per_sec == 8000
        assert silent_section.start_sec == 0
        assert silent_section.end_sec == 2

    def test_init_fail(self):
        """Test init with failure."""
        with pytest.raises(Exception) as e:
            silent_section = SilentSection("hoge", 10)
        assert "Type of start_frame_index must be int:" in str(e.value)
        with pytest.raises(Exception) as e:
            silent_section = SilentSection(-1, 10)
        assert "start_frame_index must be non-negative:" in str(e.value)
        with pytest.raises(Exception) as e:
            silent_section = SilentSection(5, "piyo")
        assert "Type of end_frame_index must be int:" in str(e.value)
        with pytest.raises(Exception) as e:
            silent_section = SilentSection(1, 0)
        assert "end_frame_index must be positive:" in str(e.value)
        with pytest.raises(Exception) as e:
            silent_section = SilentSection(2, 1)
        assert "start_frame_index must be less than end_frame_index:" in str(e.value)
        with pytest.raises(Exception) as e:
            silent_section = SilentSection(0, 10, -1)
        assert "frame_per_sec must be positive:" in str(e.value)

    def test_duration_sec(self):
        """Test duration_sec."""
        silent_section = SilentSection(0, 16000)
        assert silent_section.duration_sec() == 2

    def test_is_cm_divider_candidate(self):
        frame_per_sec = 10
        following_sections = [
            SilentSection(10, 11, frame_per_sec),
            SilentSection(20, 21, frame_per_sec),
        ]
        duration_sec_units = DurationSecUnits([1, 2])
        margin_sec = 0.1
        target_section = SilentSection(0, 1, frame_per_sec)
        assert target_section.is_cm_divider_candidate(following_sections, duration_sec_units, margin_sec)
        duration_sec_units = DurationSecUnits([0.5])
        assert not target_section.is_cm_divider_candidate(following_sections, duration_sec_units, margin_sec)
        duration_sec_units = DurationSecUnits([2])
        assert target_section.is_cm_divider_candidate(following_sections, duration_sec_units, margin_sec)