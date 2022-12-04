import pytest

from lib.cmcut import ProgramScenes

@pytest.fixture
def generate_scenes_inputs():
    first_start_sec_candidate_1 = 3
    last_end_sec_candidate_1 = 20
    cm_sections_1 = [(5, 10), (12, 15)]
    last_scene_duration_1 = 5
    expected_output_1 = [(3, 5), (10, 12), (15, 21)]

    first_start_sec_candidate_2 = 7
    last_end_sec_candidate_2 = 25
    cm_sections_2 = [(9, 12), (15, 20)]
    last_scene_duration_2 = 0
    expected_output_2 = [(0, 9), (12, 15), (20, 25)]

    first_start_sec_candidate_3 = 6
    last_end_sec_candidate_3 = 30
    cm_sections_3 = [(8, 12), (16, 22)]
    last_scene_duration_3 = 7
    expected_output_3 = [(0, 8), (12, 16), (22, 30)]

    return [
        (
            first_start_sec_candidate_1, 
            last_end_sec_candidate_1, 
            cm_sections_1, 
            last_scene_duration_1, 
            expected_output_1
        ),        
        (
            first_start_sec_candidate_2, 
            last_end_sec_candidate_2, 
            cm_sections_2, 
            last_scene_duration_2, 
            expected_output_2
        ),        
        (
            first_start_sec_candidate_3, 
            last_end_sec_candidate_3, 
            cm_sections_3, 
            last_scene_duration_3, 
            expected_output_3
        ),    
    ]

class TestProgramScenes:
    def test_generate_scenes(self, generate_scenes_inputs):
        for input in generate_scenes_inputs:
            first_start_sec_candidate = input[0]
            last_end_sec_candidate = input[1]
            cm_sections = input[2]
            last_scene_duration = input[3]
            expected_output = input[4]
            assert ProgramScenes.generate_scenes(first_start_sec_candidate, last_end_sec_candidate, cm_sections, last_scene_duration) == expected_output