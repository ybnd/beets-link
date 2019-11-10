from beets.plugins import BeetsPlugin
from beets import ui
from beets.ui import Subcommand, get_path_formats, input_yn, UserError, print_
from beets.library import Item
from beets.dbcore.query import AndQuery, OrQuery, MatchQuery
from beets.dbcore import types
from beets.util import mkdirall, normpath, syspath
import beets.autotag.hooks as hooks
import os

import os.path
import threading
import argparse
from concurrent import futures
import six

import beets
from beets import util, art
from beets.plugins import BeetsPlugin, log
from beets.ui import Subcommand, get_path_formats, input_yn, UserError, print_
from beets.library import parse_query_string, Item
from beets.util import syspath, displayable_path, cpu_count, bytestring_path

from beetsplug import convert

class LinkPlugin(BeetsPlugin):
    """

    """

    SEPARATORS = {
        'albumartist': ' [/&\\-] |\\, | and | with | feat ',
        'album': ' [/&] | and | with | feat '
    }

    QUERIES = [  # todo: get this from config!
        'albumartist:VA',
        'albumartist:"Various Artists"',
        'albumartist:with',
        'albumartist:feat',
        'album:split',
    ]

    IGNORE = [
        'dontlink:T',
        'albumartist:"Between the Buried and Me"',
        'albumartist:"You Break, You Buy"'
    ]

    LINKPATH = [ # todo: implement %collaborator handling function: repeat for all collaborators ~ https://beets.readthedocs.io/en/stable/dev/plugins.html#add-path-format-functions-and-fields
        'default: $relevant_collaborators/$year - $album/$track $title'
    ]

    album_types = {
        'collaborators': types.STRING, # string to be interpreted as a JSON list by LinkPlugin.collaborator
        'dontlink': types.BOOLEAN,
        'haslinks': types.BOOLEAN,
        'links': types.STRING          # string to be interpreted as a JSON list by LinkPlugin._remove_links
    }

    def __init__(self):
        super(LinkPlugin, self).__init__()

        self.template_fields['relevant_collaborator'] = self._get_collaborators
        self.register_listener('album_imported', self.on_import)
        # https://beets.readthedocs.io/en/v1.3.17/dev/plugins.html#listen-for-events

    def on_import(self, lib, album):
        """ Check for split/compilation 'flags':
                - comp:T?
                    * maybe: separate comp into comp and split, add option for additional fields
                - not all tracks have the same artist?
                - albumartist field contains (configurable) separator(s), e.g. `/`, `&`, `,`, `and`, `with`, `feat`, `vs.`, `et`?
                    https://beets.readthedocs.io/en/v1.3.17/dev/plugins.html#read-configuration-options
                    * separated artists already in library?

                -> prompt user if uncertain
                    https://beets.readthedocs.io/en/v1.3.17/dev/plugins.html#append-prompt-choices

                * also handle case when imported album is NOT a split, but is BY an artist which only had splits previously!
        """
        # https://beets.readthedocs.io/en/v1.3.17/dev/api.html#the-library-class
        # https://beets.readthedocs.io/en/v1.3.17/dev/api.html#album

        print(f"Got here!")
        pass

    def add(self, lib, opts):
        print(f'Should be adding links to library ~ config')

        for album in self._get_candidate_albums(lib):
            self._prompt_user(lib, album)


        pass

    def remove(self, lib, opts):
        print(f'Should be removing links from library')
        pass

    def _get_candidate_albums(self, lib):
        """ For all albums in library, check whether they could be a split (will be slow, probably) """

        negation = ''
        for ignore in self.IGNORE:
            negation = negation + f'^{ignore} '

        albums = []

        for query in [f'{k}::"{v}"' for k,v in self.SEPARATORS.items()] + self.QUERIES:
            for album in lib.albums(query=f"{query} {negation}"):
                if album['path'] not in [a['path'] for a in albums]:
                    albums.append(album)

        return albums

    def _get_all_splits(self, lib):
        pass

    def _infer_if_split(self, lib, album):
        """ Infer whether album is a split based on config """
        pass

    def _prompt_user(self, lib, album):
        """ Prompt user whether it's okay to consider this album a split, and whether the list of collaborators is ok """
        pass

    def _add_links(self, lib, album):
        """ For every collaborator in album, add a link in their respective directories if they meet the conditions set in config """
        pass

    def _remove_links(self, lib, album):
        """ For every collaborator in album, remove link if present """
        pass

    def commands(self):
        return [LinkCommand(self)]


    def _get_collaborators(self, item):
        # todo: split album['albumartist'] by
        # todo: return JSON formatted list
        album = item.get_album()



class LinkCommand(Subcommand):
    name = 'link'
    help = 'add links to split and compilation albums to the contributing artists\' directories'

    def __init__(self, plugin):
        parser = argparse.ArgumentParser()
        parser.add_argument('--add', action='store_const', dest='action', const='add')
        parser.add_argument('--remove', action='store_const', dest='action', const='remove')

        self.parser = parser
        self.plugin = plugin

        super(LinkCommand, self).__init__(self.name, parser, self.help)

    def func(self, lib, opts, _):
        if opts.action == 'add':
            self.plugin.add(lib, opts)
        elif opts.action == 'remove':
            self.plugin.remove(lib, opts)

    def parse_args(self, args):
        return self.parser.parse_args(args), []