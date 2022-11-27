import json
import pathlib
import sys

from lib.cmcut import DurationSecUnits, FrameLoudness, ProgramScenes, NominalCMStructure


if __name__ == '__main__':
    frame_per_sec = 8000
    if len(sys.argv) < 3:
        raise ValueError("need both wav file and program property file.")
    wav_path = sys.argv[1]
    default_cm_structures_dict = [{"cm": 60}] * 3 
    default_end_scene_duration_sec = 15
    default_has_monolithic_cm = False
    default_margin_sec = 3.5
    default_duration_threshold = 4000
    duration_sec_units = DurationSecUnits([15, 30])

    program_property = {}
    program_property_json_path = sys.argv[2]
    with open(program_property_json_path, "r") as json_file:
        program_property = json.load(json_file)
    cm_structures_dict = program_property.get("cm_structures", default_cm_structures_dict)
    end_scene_duration_sec = program_property.get("end_scene_duration", default_end_scene_duration_sec)
    has_monolithic_cm = program_property.get("has_monolithic_cm", default_has_monolithic_cm)
    margin_sec = program_property.get("margin_sec", default_margin_sec)
    duration_threshold = program_property.get("duration_threshold", default_duration_threshold)
    additional_duration_units = program_property.get("additional_duration_units", [])
    cm_structures = [
        NominalCMStructure(value, margin_sec) for value in cm_structures_dict
        ]

    for duration in additional_duration_units:
        if not duration in duration_sec_units.durations_sec:
            duration_sec_units = duration_sec_units.append_duration(duration)
#    print (f"#{duration_sec_units.durations_sec}")

    loudness = FrameLoudness.get_loudness_from_wav(wav_path)
#    print (f"DURATION THRESHOLD: {duration_threshold}")
    program_scenes = ProgramScenes.construct_program_scenes(
        loudness, 
        duration_threshold, 
        frame_per_sec, 
        duration_sec_units, 
        cm_structures, 
        end_scene_duration_sec,
        has_monolithic_cm
        )
    video_basename = pathlib.Path(wav_path).stem
    total_duration = 0
    for index, section in enumerate(program_scenes.scene_sections):
        duration = section[1] - section[0]
        print (
            "docker run -v $(pwd):$(pwd) jrottenberg/ffmpeg -stats -i "
            f"$(pwd)/{video_basename}.ts -c copy "
            f"-ss {section[0]} -t {duration} " 
            f"-map 0:v:0? -map 0:a:0? -map 0:a:1? $(pwd)/tmp_{video_basename}.ts"
            )
        print (
            "docker run -v $(pwd):$(pwd) jrottenberg/ffmpeg -stats -i " 
            f"$(pwd)/tmp_{video_basename}.ts -c:v libx264 -map 0:v:0? -map 0:a:0? -map 0:a:1? -f mp4 " 
            f"$(pwd)/{video_basename}_{index}.m4v")
        print (f"rm -f tmp_{video_basename}.ts")
        total_duration += duration
#        print (f"#{section[0], section[1] - section[0]}")
    print (f"#{total_duration}")
