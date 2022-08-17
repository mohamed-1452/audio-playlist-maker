from typing import Callable, List, Tuple, TypeVar
from os.path import normpath, isdir, splitext, split
from moviepy.editor import AudioFileClip
from glob import glob


T = TypeVar('T')


def ask(
    query: str,
    validators: List[Callable[[str], Tuple[bool, str]]] = [],
    transformer: Callable[[str], T] = lambda x: x,
):
    while True:
        answer = input(query)
        passed = True

        for validator in validators:
            valid, message = validator(answer)
            if not valid:
                print(message)
                passed = False
                break

        if not passed:
            continue

        return transformer(answer)


# Validators
def is_numeric(text: str):
    valid = text.isnumeric()
    return (valid, "input must be numeric")


def is_dir(text: str):
    valid = isdir(text)
    return (valid, "input must be a valid directory")


def is_supported_audio_dir(text: str):
    message = "input must be a supported audio directory"
    base_path = text_to_dir_path(text)

    if len(glob(base_path+'*.wav')) + len(glob(base_path+'*.mp3')) > 1:
        return (True, message)
    else:
        sub_dirs = glob(base_path+'*/')
        if len(sub_dirs) > 0:
            for sub_dir_path in sub_dirs:
                if len(glob(sub_dir_path+'*.wav')) + len(glob(sub_dir_path+'*.mp3')) < 2:
                    return (False, message)
            return (True, message)
        else:
            return (False, message)


# Transformers
def text_to_dir_path(text: str):
    return normpath(text) + '/'


def text_to_int(text: str):
    return int(text)


def audio_dir_to_grouped_audio_clips(audio_dir: str):
    groups: List[Tuple[str, List[Tuple[AudioFileClip, str]]]]
    base_path = text_to_dir_path(audio_dir)
    is_single_group = len(
        glob(base_path+'*.wav') + glob(base_path+'*.mp3')) > 1

    if is_single_group:
        groups = [((base_path, []))]
    else:
        sub_paths = glob(base_path+'*/')
        groups = [(sub_path, []) for sub_path in sub_paths]

    for i, group in enumerate(groups):
        path, clips = group
        file_paths = glob(path+'*.wav') + glob(path+'*.mp3')
        for file_path in file_paths:
            clip = AudioFileClip(file_path)
            head, tail = split(file_path)
            title = splitext(tail)[0]
            clips.append((clip, title))
        group_name = split(path[:-1])[1]
        groups[i] = (group_name, clips)

    return groups


def s_to_hhmmss(seconds: int):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02i:%02i:%02i" % (hours, minutes, seconds)
