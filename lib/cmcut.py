"""Library to cut CM."""
from __future__ import annotations
import copy
from typing import List, Tuple, Dict, Optional, Union

import get_loudness_from_wav
import numpy as np


class SilentSection:
    """SilentSection
    This class represents property of silent scene.
    Attributes:
        frame_per_sec (float): Factor to convert frame index to sec.
        start_sec (float): Start timing of the scene in sec.
        end_sec (float): End timing of the scene in sec.
    """
    def __init__(
        self, 
        start_frame_index: int, 
        end_frame_index: int, 
        frame_per_sec: float = 8000
        ):
        """Initialize a SilentSection object.
        Args:
            start_frame_index (int): Start timing of the scene in frame_index.
            end_frame_index (int): End timing of the scene in frame_index.
            frame_per_sec (float): Factor to convert frame index to sec.
        """
        if type(start_frame_index) is not int:
            raise TypeError(f"Type of start_frame_index must be int: {type(start_frame_index)}.")
        if start_frame_index < 0:
            raise ValueError(f"start_frame_index must be non-negative: {start_frame_index}.")
        if type(end_frame_index) is not int:
            raise TypeError(f"Type of end_frame_index must be int: {type(end_frame_index)}.")
        if end_frame_index <= 0:
            raise ValueError(f"end_frame_index must be positive: {end_frame_index}.")
        if start_frame_index >= end_frame_index:
            raise ValueError(f"start_frame_index must be less than end_frame_index: {start_frame_index} {end_frame_index}.")
        if frame_per_sec <= 0:
            raise ValueError(f"frame_per_sec must be positive: {frame_per_sec}.")
        self.frame_per_sec = frame_per_sec
        self.start_sec = start_frame_index/frame_per_sec
        self.end_sec = end_frame_index/frame_per_sec

    def __repr__(self):
        return repr([self.start_sec, self.end_sec, self.frame_per_sec])

    def duration_sec(self) -> float:
        """Duration of the section."""
        return self.end_sec - self.start_sec

    def is_cm_divider_candidate(
        self, 
        following_sections: List[SilentSection], 
        duration_sec_units: DurationSecUnits, 
        margin_sec: float
        ) -> bool:
        """Judge if the section is candidate of CM.
        If Duration between the section and the last section 
        is one of the duration units, the section could be a candidate of cm divider.
        Args:
            last_section (SilentSection): A section which is just before the section.
            duration_sec_units (DurationSecUnits): Durations of CM.
            margin_sec (float): Fluctuation of duration to be considered.
        """
        for section in following_sections:
            duration_sec = section.end_sec - self.start_sec
            largest_duration_unit_sec = duration_sec_units.durations_sec[-1] 
            if largest_duration_unit_sec + margin_sec <= duration_sec:
                break
            for duration_sec_unit in duration_sec_units.durations_sec:
#                print (f"#### {self}, {section}, {duration_sec}")
                if duration_sec_unit < duration_sec <= duration_sec_unit + margin_sec:
                    return True
        return False

class FrameLoudness:
    """FrameLoudness
    This class represents timeseries of sound loudness of a TV program.
    Attributes:
        values (List[float]): Timeseries of loudness.
    """
    def __init__(self, loudness_values: List[float]):
        """Initialize a FrameLoudness object.
        Args:
            loudness_array (List[float]): Timeseries of loudness.
        """
        type_error_message = "Loudness_array must be List[float]"
        if type(loudness_values) is not list:
            raise TypeError(
                f"{type_error_message}: {type(loudness_values)}."
                )
        if len(loudness_values) <= 0:
            raise TypeError(
                f"{type_error_message}: length {len(loudness_values)}."
                )
        filtered_values = list(filter(lambda x: type(x) is float, loudness_values))
        if len(filtered_values) != len(loudness_values):
            raise TypeError(type_error_message)
        if len(list(filter(lambda x: x<0, filtered_values))) > 0:
            raise TypeError("Loudness must be positive.")

        self.values = loudness_values

    @classmethod
    def get_loudness_from_wav(cls, wav_path:str) -> FrameLoudness:
        """Get loudness timeseries from wav file.
        Args:
            wav_path (str): A path of wav file.
        """
        loudness_values = get_loudness_from_wav.wav2loudness(wav_path)
        return FrameLoudness(loudness_values)

class NominalCMStructure:
    """NominalCMStructure
    This class represents nominal CM structure, 
    which could consists both actual CM and indistinguishable program scene.
    Attributes:
        composition (dict): Composition of the structure 
            which includes at least a CM and possibly includes a program scene.
            Ex.
            {'cm': 60}
            {'scene': 30, 'cm': 60}
            {'cm': 60, 'scene': 30}
            {'monolithic_cm': 120}
        nominal_duration (Union[int, float]): Sum of durations in the structure.
    """
    def __init__(self, cm_structure: Dict, margin_sec: float):
        """Initialize a NominalCMStructure object.
        Args:
            cm_structure (Dict): Raw nominal CM structure.
        """
        if type(cm_structure) is not dict:
            raise TypeError(
                f"Unexpected type for {self.__class__.__name__}: {type(cm_structure)}."
                )
        if len(cm_structure) > 2:
            raise ValueError(
                f"CM Structure length(must be less than 3) is too long: {len(cm_structure)}"
                )
        elif len(cm_structure) == 1 and "scene" in cm_structure:
            raise ValueError(f"CM Structure must include 'cm' key.")
        elif len(cm_structure) == 0:
            raise ValueError("CM Structure is empty.")
        self.nominal_duration = 0
        for key in cm_structure:
            if key != "cm" and key != "scene" and key != "monolithic_cm":
                raise KeyError(f"Key must be either 'cm' or 'scene': {key}.")
            if type(cm_structure[key]) is not int and type(cm_structure[key]) is not float:
                raise TypeError(
                    f"Type of value must be either integer or float: {type(cm_structure[key])}."
                    )
            elif cm_structure[key] <= 0:
                raise ValueError(f"Value must be positive value: {cm_structure[key]}.")
            self.nominal_duration += cm_structure[key]
        self.composition = cm_structure
        if type(margin_sec) is not int and type(margin_sec) is not float: 
            raise TypeError(f"Type of margin sec must be either integer or float: {type(margin_sec)}.")
        if margin_sec <= 0:
            raise ValueError(f"margin_sec must be positive value: {margin_sec}.")
        self.margin_sec = margin_sec
    def get_actual_cm_section(
        self, 
        last_cm_divider_end_sec: float, 
        next_cm_divider_start_sec: float
        ) -> Tuple[float]:
        """Get actual CM section removing a TV program scene based on the structure.
        Args:
            last_cm_divider_end_sec (float): End timing of last cm divider. 
            next_cm_divider_start_sec (float): Start timing of next cm divider.
        """
        if len(self.composition) == 1:
            return last_cm_divider_end_sec, next_cm_divider_start_sec
        counter = 0
        for key in self.composition:
            if key == "scene":
                if counter == 0:
                    return last_cm_divider_end_sec + self.composition[key], next_cm_divider_start_sec
                else:
                    return last_cm_divider_end_sec, next_cm_divider_start_sec - self.composition[key]
            counter += 1

class DurationSecUnits:
    """DurationSecUnits
    This class represents CM Duration units in sec.
    Attributes:
        durations_sec (List[Union[int, float]]): CM Duration units in sec.
    """
    def __init__(self, durations_sec: List[Union[int, float]]):
        """Initialize a DuratoinSecUnits object.
        Args:
            durations_sec (List[Union[int, float]]): Duration units to distinguish CM.
        """
        self.durations_sec = [15, 30]
        if len(durations_sec) > 0:
            for value in durations_sec:
                if type(value) is not int and type(value) is not float:
                    raise TypeError(
                        f"Element of duration units must be integer or float: {type(value)}."
                        )
                if value <= 0:
                    raise ValueError(f"CM durations must be positive value: {value}.")
                if value not in self.durations_sec:
                    self.durations_sec.append(value)
            self.durations_sec = sorted(self.durations_sec)

    def append_duration(self, duration_sec: Union[int, float]) -> DurationSecUnits:
        """Append a duration to the units.
        Args:
            duration_sec (Union[int, float]): Duration to be appended to the units.
        """
        durations = self.durations_sec
        durations.append(duration_sec)
        durations_sorted = sorted(durations)
        return DurationSecUnits(durations_sorted)

    def remove_duration(self, duration_sec: Union[int, float]) -> DurationSecUnits:
        """Remove a duration from the units.
        Args:
            duration_sec (Union[int, float]): Duration to be removed from the units.
        """
        durations = self.durations_sec
        if duration_sec in durations:
            durations.remove(duration_sec)
        return DurationSecUnits(durations)

class ProgramScenes:
    """ProgramScenes
    This class defines TV program scenes using both start and end timing.
    Attributes:
        scene_sections (List[Tuple[float]]): List of start and end timing.
    """
    starting_range_sec = 5
    end_margin_sec = 1

    def __init__(self, scene_sections: List[Tuple[float]]):
        self.scene_sections = scene_sections
    
    @classmethod
    def construct_program_scenes(
        cls, 
        loudness: FrameLoudness, 
        duration_frame_threshold: int, 
        frame_per_sec: float, 
        duration_sec_units: DurationSecUnits, 
        cm_structures: List[NominalCMStructure], 
        last_scene_duration: int,
        has_monolithic_cm: bool
        ) -> ProgramScenes:
        """Construct TV program scenes based on both its loudness timeseries and program property.
        The property consists of structures of CMs and duration of last scene.
        Args:
            loudness (FrameLoudness): Loudness timeseries of a TV program.
            duration_frame_threshold (int): Duration threshold in frame number to distinguish silent section.
            frame_per_sec (float): Factor to convert frame index to sec.
            duration_sec_units (DurationSecUnits): CM Duration units in sec.
            cm_structures (List[NominalCMStructure]): List of nominal CM structure, 
                which could consists both actual CM and indistinguishable program scene.
            last_scene_duration (int): Duration of last scene in the program.
        """
        silent_sections = cls.extract_silent_sections(loudness, duration_frame_threshold, frame_per_sec)
#        print (f"SILENT_SECTIONS: {silent_sections}")
        cm_sections = cls.construct_cm_sections(
            silent_sections, 
            duration_sec_units, 
            cm_structures, 
            has_monolithic_cm
            )
        first_start_sec_canditate = silent_sections[0].start_sec
        last_end_sec_canditate = silent_sections[-1].end_sec
        return ProgramScenes(
            cls.generate_scenes(
                first_start_sec_canditate, 
                last_end_sec_canditate,
                cm_sections, 
                last_scene_duration,
                )
                )

    @classmethod
    def construct_program_scenes_without_structure(
        cls, 
        loudness: FrameLoudness, 
        duration_frame_threshold: int, 
        frame_per_sec: float, 
        duration_sec_units: DurationSecUnits, 
        ) -> ProgramScenes:
        """Construct TV program scenes based on its loudness.
        Countinuous series made of multi CM is searched and then is cut.
        Args:
            loudness (FrameLoudness): Loudness timeseries of a TV program.
            duration_frame_threshold (int): Duration threshold in frame number to distinguish silent section.
            frame_per_sec (float): Factor to convert frame index to sec.
            duration_sec_units (DurationSecUnits): CM Duration units in sec.
        """
        silent_sections = cls.extract_silent_sections(loudness, duration_frame_threshold, frame_per_sec)
        cm_sections = cls.search_cm_sections(silent_sections, duration_sec_units)
        first_start_sec_canditate = silent_sections[0].start_sec
        last_end_sec_canditate = silent_sections[-1].end_sec
        return ProgramScenes(
            cls.generate_scenes(
                first_start_sec_canditate, 
                last_end_sec_canditate,
                cm_sections, 
                last_scene_duration=0,
                )
                )

    @staticmethod
    def extract_silent_sections(
        loudness: FrameLoudness, duration_frame_threshold: int, frame_per_sec: int
        ) -> List[SilentSection]:
        """Extract silent sections based on its loudness.
        Args:
            loudness (FrameLoudness): Loudness timeseries of a TV program.
            duration_frame_threshold (int): Duration threshold in frame number to distinguish silent section.
            frame_per_sec (float): Factor to convert frame index to sec.
        """
        silent_sections = []
        silent_duration = 0
        last_loudness = -1
        for frame_index, loudness in enumerate(loudness.values):
            if loudness == 0:
                if last_loudness != 0:
                    start_frame_index = frame_index
                silent_duration += 1
            elif loudness != 0:
                if silent_duration > 0:
                    if silent_duration > duration_frame_threshold:
                        end_frame_index = frame_index
                        silent_sections.append(SilentSection(start_frame_index, end_frame_index, frame_per_sec))
                silent_duration = 0
            last_loudness = loudness
        return silent_sections

    @staticmethod
    def construct_cm_sections(
        silent_sections: List[SilentSection], 
        duration_sec_units: DurationSecUnits, 
        cm_structures: List[NominalCMStructure],
        has_monolithic_cm: bool
        ) -> List[Tuple[int]]:
        """Construct CM sections based on both silent sections and program property.
        The property consists of structures of CMs and duration of last scene.
        Args:
            silent_sections (List[SilentSection]): Silent sections which could divide program scenes and CMs
            duration_sec_units (DurationSecUnits): CM Duration units in sec.
            cm_structures (List[NominalCMStructure]): List of nominal CM structure, 
                which could consists both actual CM and indistinguishable program scene.
        """
        if len(cm_structures) == 0:
            return []
        cm_num_threshold = 1
        if has_monolithic_cm:
            cm_num_threshold = 0

        cm_divider_candidates = []
        cm_sections = []
        structure_reference = 0
        target_cm_structure = cm_structures[structure_reference]
        margin_sec = target_cm_structure.margin_sec
        nominal_cm_duration = target_cm_structure.nominal_duration

        for index, section in enumerate(silent_sections):
#            print (section)
            tmp_duration_sec_units = copy.deepcopy(duration_sec_units)
            if "monolithic_cm" in target_cm_structure.composition:
                tmp_duration_sec_units = duration_sec_units.append_duration(target_cm_structure.composition["monolithic_cm"])
            if section.is_cm_divider_candidate(silent_sections[index+1:], tmp_duration_sec_units, margin_sec):
#                print (f"CANDIDATE: {section}")
                cm_divider_candidates.append(section)
            candidates_could_be_cm = len(cm_divider_candidates) > cm_num_threshold
            if len(target_cm_structure.composition) and "monolithic_cm" in target_cm_structure.composition:
                candidates_could_be_cm = len(cm_divider_candidates) == 1
            if candidates_could_be_cm:
#                print (section, cm_divider_candidates)
                combined_duration_sec = section.end_sec - cm_divider_candidates[0].start_sec
#                print (f"COMB_DURA_SEC: {combined_duration_sec}")
                if combined_duration_sec <= nominal_cm_duration:
                    continue
                if nominal_cm_duration < combined_duration_sec < nominal_cm_duration + margin_sec:
                    actual_cm_section = target_cm_structure.get_actual_cm_section(
                        cm_divider_candidates[0].end_sec, section.start_sec
                        )
                    cm_sections.append(actual_cm_section)
                    structure_reference += 1
                    if structure_reference < len(cm_structures):
                        target_cm_structure = cm_structures[structure_reference]
                        nominal_cm_duration = target_cm_structure.nominal_duration
                    else:
                        break
                cm_divider_candidates = [cm_divider_candidates[-1]]
        return cm_sections


    @classmethod
    def search_cm_sections(
        cls, 
        silent_sections: List[SilentSection], 
        duration_sec_units: DurationSecUnits
        ):
        """Search CM sections based on silent sections.
        Countinuous series made of multi CM is searched.
        Args:
            silent_sections (List[SilentSection]): Silent sections which could divide program scenes and CMs
            duration_sec_units (DurationSecUnits): CM Duration units in sec.
        """
        margin_sec = 1
        cm_divider_candidates = []
        cm_sections = []
        continuity = False
        for index, section in enumerate(silent_sections):
            if section.is_cm_divider_candidate(silent_sections[index+1:], duration_sec_units, margin_sec):
                cm_divider_candidates.append(section)
                continuity = True
            else:
                if continuity and len(cm_divider_candidates) >= 2:
                    cm_sections.append((cm_divider_candidates[0].end_sec, cm_divider_candidates[-1].start_sec))
                    cm_divider_candidates = []
                    continuity = False
        if len(cm_divider_candidates) >= 2:
            cm_sections.append((cm_divider_candidates[0].end_sec, cm_divider_candidates[-1].start_sec))
        return cm_sections

    @classmethod
    def generate_scenes(
        cls,
        first_start_sec_candidate: float,
        last_end_sec_candidate: float,
        cm_sections: List[Tuple[float]], 
        last_scene_duration: int
        ):
        """Generate sections based on CM sections.
        Args:
            first_start_sec_candidate (float): Start timing of first silent scene in a TV program.
            last_end_sec_candidate (float): End timing of last silent scene in the program.
            cm_sections (List[Tuple[float]]): List of start-end timings of CMs. 
            last_scene_duration (int): The duration of last scene in the program.
        """
        scenes = []
        start_sec = 0
        if first_start_sec_candidate < cls.starting_range_sec:
            start_sec = first_start_sec_candidate
        for section in cm_sections:
            scenes.append((start_sec, section[0]))
            start_sec = section[1]
        if last_scene_duration != 0:
            scenes.append((start_sec, start_sec + last_scene_duration + cls.end_margin_sec))
        else:
            scenes.append((start_sec, last_end_sec_candidate))
        return scenes