# normal
import argparse
import os
import sys

# src
from src.formatter import Formatter

# project specific
import lyricsgenius
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_args_parser():
    parser = argparse.ArgumentParser('ConkLyr Arguments', add_help=False)

    parser.add_argument('--fs', '--font-size', default=11, type=int)
    parser.add_argument('--tfs', '--title-font-size', default=13, type=int)

    parser.add_argument('--sa', '--show-ahead',
                        help='how many lines to show ahead of the estimated current line (to show all lines enter a '
                             'large number both in --sa and in --sb)',
                        default=20,
                        type=int)

    parser.add_argument('--sb', '--show-behind',
                        help='how many lines to show behind of the estimated current line (to show all lines enter a '
                             'large number both in --sa and in --sb)',
                        default=10,
                        type=int)

    parser.add_argument('--highlight-list',
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

        song_length = playback['item']['duration_ms']
        current_pos = playback['progress_ms']

        percent_played = current_pos / song_length

        lyrics = Formatter.slice(text=lyrics, position=percent_played, show_ahead=args.sa, show_behind=args.sb)
        lyrics = Formatter.color(text=lyrics, highlight=args.highlight_list, cm=args.cm)

        song   = Formatter.set_font(song, font_size=args.tfs, bold=True)
        artist = Formatter.set_font(artist, font_size=args.fs)
        lyrics = Formatter.set_font(lyrics, font_size=args.fs)

        # enable printing
        sys.stdout = sys.__stdout__

        lyrics = f'{song}\n{artist}\n\n{lyrics}'
        print(lyrics)

    except Exception as e:
        # enable printing
        sys.stdout = sys.__stdout__
        print('There was error')
        print(e)


if __name__ == '__main__':
    parser = get_args_parser()
    main(parser.parse_args())
