# normal
import argparse
import os
import re
import sys

# usually are not defaultively installed
import numpy as np
import matplotlib.cm
from matplotlib.colors import to_hex

# src
from src.formatter import Formatter

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
                        default=['Verse', 'Chorus', 'Instrument', 'Solo', 'Bridge', 'Intro', 'Outro'])

    parser.add_argument('--cm', '--color-map',
                        type=str,
                        default='Pastel2')

    parser.add_argument('--rm',
                        nargs='*',
                        type=str,
                        default=['Remaster', '-'])
    return parser


def main(args):
    # disable printing
    sys.stdout = open(os.devnull, 'w')

    genius = lyricsgenius.Genius(os.environ['GENIUS_TOKEN'])

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ['CLIENT_ID'],
                                                   client_secret=os.environ['CLIENT_SECRET'],
                                                   redirect_uri='http://localhost:8888',
                                                   scope='user-read-playback-state, user-read-currently-playing',
                                                   ))

    try:
        curr_song = sp.currently_playing()

        song = curr_song['item']['name']

        for substr in args.rm:
            song = song.replace(substr, '')
        song = song.strip()

        artist = curr_song['item']['artists'][0]['name']

        lyrics = genius.search_artist(artist, max_songs=1).song(song).lyrics.replace('EmbedShare URLCopyEmbedCopy', '')

        song, artist, lyrics = Formatter.pad(song), Formatter.pad(artist), Formatter.pad(lyrics)
        playback = sp.current_playback()

        percent_played = 1 - (playback['item']['duration_ms'] - playback['progress_ms']) / playback['item']['duration_ms']

        lyrics = Formatter.slice(text=lyrics, position=percent_played, show_ahead=20, show_behind=10)
        lyrics = Formatter.color(text=lyrics, highlight=args.highlight, cm=args.cm)

        song, artist, lyrics = Formatter.set_font(song, font_size=13, bold=True), Formatter.set_font(artist), Formatter.set_font(lyrics)

        # enable printing
        sys.stdout = sys.__stdout__


        lyrics = f'{song}\n{artist}\n\n{lyrics}'

        print(lyrics)

    except Exception as e:
        # enable printing
        sys.stdout = sys.__stdout__
        print('Error')
        print(e)


if __name__ == '__main__':
    parser = get_args_parser()
    main(parser.parse_args())
