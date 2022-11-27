import pathlib
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
    print (f"#{total_duration}")

