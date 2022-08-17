from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.editor import AudioFileClip, CompositeAudioClip

from helpers import *


def make_playlist(
    audio_clips: list[Tuple[AudioFileClip, str]],
    output_dir: str,
    cross_fade_time: int,
    playlist_name: str
):
    start_audio_at = 0
    timestamps: List[str] = []
    playlist: List[AudioFileClip] = []

    for i, audio_clip in enumerate(audio_clips):
        clip, title = audio_clip
        timestamp = 0
        if start_audio_at == 0:
            clip = audio_fadeout(clip, cross_fade_time)
        else:
            clip = audio_fadein(clip, cross_fade_time)
            clip = clip.set_start(start_audio_at)
            timestamp = round(start_audio_at+cross_fade_time/2)
            if i+1 < len(audio_clips):
                clip = audio_fadeout(clip, cross_fade_time)

        timestamps.append(s_to_hhmmss(timestamp) + ' ' + title.strip())
        playlist.append(clip)
        start_audio_at += clip.duration - cross_fade_time

    playlist_filename = output_dir+playlist_name+'.wav'
    CompositeAudioClip(playlist).write_audiofile(playlist_filename, fps=44100)

    timestamps_filename = output_dir+playlist_name + '.timestamps.txt'
    file = open(timestamps_filename, 'w', encoding='utf-8')
    file.write('\n'.join(timestamps))
    file.close()


def main():
    grouped_audio_clips = ask(
        'input(s) directory: ',
        validators=[is_dir, is_supported_audio_dir],
        transformer=audio_dir_to_grouped_audio_clips,
    )

    output_dir = ask(
        'output directory: ',
        validators=[is_dir],
        transformer=text_to_dir_path,
    )

    cross_fade_time = ask(
        'cross fade time: ',
        validators=[is_numeric],
        transformer=text_to_int,
    )

    for group in grouped_audio_clips:
        playlist_name, clips = group
        make_playlist(clips, output_dir, cross_fade_time, playlist_name)

    return output_dir


if __name__ == "__main__":
    try:
        print('output: ', main())
    except Exception as error:
        print('error: ' + str(error))
