import sys

from lib.cmcut import DurationSecUnits, FrameLoudness, ProgramScenes


if __name__ == '__main__':
    frame_per_sec = 8000
    duration_threshold = 5000
    if len(sys.argv) < 2:
        raise ValueError("need wav file.")
    wav_path = sys.argv[1]
    duration_sec_units = DurationSecUnits([15, 30])

    loudness = FrameLoudness.get_loudness_from_wav(wav_path)
    program_scenes = ProgramScenes.construct_program_scenes_without_structure(
        loudness, 
        duration_threshold, 
        frame_per_sec, 
        duration_sec_units, 
        )
    for section in program_scenes.scene_sections:
        print (f"#{section[0], section[1] - section[0]}")

