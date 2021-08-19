# normal
import argparse
import os
import re
import sys

# usually are not defaultively installed
import numpy as np
import matplotlib.cm
from matplotlib.colors import to_hex

# project specific
import lyricsgenius
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_args_parser():
    parser = argparse.ArgumentParser('ConkLyr Arguments', add_help=False)
    parser.add_argument('--fs', '--font-size', default=11, type=int)
    parser.add_argument('--l', '--lines', default=25, type=int)

    parser.add_argument('--highlight',
                        nargs='*',
                        type=str,
                        default=['Verse', 'Chorus', 'Instrument', 'Solo', 'Intro', 'Outro'])

    parser.add_argument('--cm', '--color-map',
                        type=str,
                        default='Pastel2')
    return parser


def add_color(src, regex, color):
    matches = set(re.findall(regex, src))
    dst = src
    for match in matches:
        dst = dst.replace(match, '${color ' + color + '}' + match + '${color}')
    return dst


def main(args):
    # disable printing
    sys.stdout = open(os.devnull, 'w')

    show_lines = args.l

    genius = lyricsgenius.Genius(os.environ['GENIUS_TOKEN'])

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ['CLIENT_ID'],
                                                   client_secret=os.environ['CLIENT_SECRET'],
                                                   redirect_uri='http://localhost:8888',
                                                   scope='user-read-playback-state, user-read-currently-playing',
                                                   ))

    font = os.environ['CONKY_FONT']
    # font_size = os.environ['CONKY_FONT_SIZE']

    try:
        curr_song = sp.currently_playing()

        artist = curr_song['item']['artists'][0]['name']
        song = curr_song['item']['name']

        lyrics = genius.search_artist(artist, max_songs=1).song(song).lyrics.replace('EmbedShare URLCopyEmbedCopy', '')
        playback = sp.current_playback()

        prec_played = 1 - (playback['item']['duration_ms'] - playback['progress_ms']) / playback['item']['duration_ms']

        lines = lyrics.split('\n')
        num_lines = len(lines)

        first_line = max(0, int(prec_played * num_lines) - show_lines // 2)
        last_line = min(first_line + show_lines, num_lines)

        lyrics = '\n'.join(lines[first_line: last_line])

        # enable printing
        sys.stdout = sys.__stdout__

        cm = matplotlib.cm.get_cmap(args.cm)
        lin_space = np.linspace(0, 1, len(args.highlight))

        for highlight_target, color_value in zip(args.highlight, lin_space):
            hex_color = str(to_hex(cm(color_value)))
            lyrics = add_color(lyrics, f'.*\s*{highlight_target}.*\s*]', color=hex_color)

        lyrics = '${font ' + font + ':size=' + str(args.fs) + '}' + lyrics + '${font}'

        song_line = '${font ' + font + ':size=13}' + song + '${font}'
        artist_line = '${font ' + font + ':size=' + str(args.fs) + '}' + artist + '${font}'

        lyrics = f'{song_line}\n{artist_line}\n\n{lyrics}'

        print(lyrics)

    except Exception as e:
        # enable printing
        sys.stdout = sys.__stdout__
        print('Error')
        print(e)


if __name__ == '__main__':
    parser = get_args_parser()
    main(parser.parse_args())
