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


class Formatter:

    @staticmethod
    def color(text: str, highlight: list, cm: matplotlib.colors.Colormap):

        """
        colors each sub-string in highlight according to the colormap - does it in place
        :param text:
        :param highlight:
        :param cm:
        """

        cm = matplotlib.cm.get_cmap(cm)
        lin_space = np.linspace(0, 1, len(highlight))

        for highlight_target, color_value in zip(highlight, lin_space):
            hex_color = str(to_hex(cm(color_value)))
            text = Formatter.color_regex(text, f'.*\s*{highlight_target}.*\s*]', color=hex_color)

        return text

    @staticmethod
    def color_regex(text, regex, color: str = '#ffffff'):
        matches = set(re.findall(regex, text))
        for match in matches:
            text = text.replace(match, '${color ' + color + '}' + match + '${color}')
        return text

    @staticmethod
    def set_font(text: str, font: str = 'Noto Sans', font_size: int = 11, bold=False):
        if bold:
            return '${font ' + font + ':size=' + str(font_size) + ': bold}' + text + '${font}'
        return '${font ' + font + ':size=' + str(font_size) + '}' + text + '${font}'

    @staticmethod
    def slice(text: str, position: float = 0., show_ahead: int = 40, show_behind: int = 20):
        lines = text.split('\n')
        num_lines = len(lines)

        curr_line = int(position * num_lines)

        first_line = max(0, curr_line - show_behind)
        last_line = min(first_line + show_ahead + show_behind, num_lines)

        if last_line - first_line < show_ahead + show_behind:
            first_line = max(0, last_line - show_ahead - show_behind)

        return '\n'.join(lines[first_line: last_line])

    @staticmethod
    def pad(text: str, width: int = 70):
        lines = text.split('\n')
        lines = [line + ' ' * max(0, width - len(line)) for line in lines]
        return '\n'.join(lines)

