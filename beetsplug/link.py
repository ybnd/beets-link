from beets.plugins import BeetsPlugin
from beets import ui
from beets.ui import Subcommand, get_path_formats, input_yn, UserError, print_
from beets.library import Item, Album
from beets.dbcore.query import AndQuery, OrQuery, MatchQuery
from beets.dbcore import types
from beets.util import mkdirall, normpath, syspath
import beets.autotag.hooks as hooks
import os
import re

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

import json

from beetsplug import convert

class LinkPlugin(BeetsPlugin):
    """

    """

    DEFAULT_SEPARATORS = {
        'albumartist': ['/', '&', '\\-', '\\,', ' and ', ' with ', ' feat\\.?'],
    }

    DEFAULT_QUERIES = [  # todo: get this from config!
        'albumartist:VA',
        'albumartist:"Various Artists"',
        'albumartist:with',
        'albumartist:feat',
        'album:split',
    ]

    DEFAULT_IGNORE = [
        'dontlink:T',
        'albumartist:"Between the Buried and Me"',
        'albumartist:"You Break, You Buy"'
    ]

    DEFAULT_FILTER = 'comp:f'

    DEFAULT_MINIMUM = 1

    DEFAULT_LINKPATH = [ # todo: implement %collaborator handling function: repeat for all collaborators ~ https://beets.readthedocs.io/en/stable/dev/plugins.html#add-path-format-functions-and-fields
        'default: %all{$collaborators}/$year - $album/$track $title'
    ]

    album_types = {
        'collaborators': types.STRING, # string to be interpreted as a JSON list
        'dontlink': types.BOOLEAN,
        'links': types.STRING          # string to be interpreted as a JSON list
    }

    def __init__(self):
        super(LinkPlugin, self).__init__()

        # todo: set instance variables for separators, queries, ignore & linkpath ~ config, defaults in LinkPlugin class attirbutes
        self.SEPARATORS = self.DEFAULT_SEPARATORS
        self.QUERIES = self.DEFAULT_QUERIES
        self.IGNORE = self.DEFAULT_IGNORE
        self.LINKPATH = self.DEFAULT_LINKPATH
        self.FILTER = self.DEFAULT_FILTER
        self.MINIMUM = self.DEFAULT_MINIMUM

        self.template_funcs['all'] = self._get_collaborators
        self.register_listener('album_imported', self.on_import)
        # https://beets.readthedocs.io/en/v1.3.17/dev/plugins.html#listen-for-events

    def commands(self):
        return [LinkCommand(self)]

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

        if self._is_candidate(album):
            if self._prompt_user_about_collaborators(lib, album):
                self._add_links(album, self._prompt_user_about_collaborators(lib, album))
        pass

    def add(self, lib, opts):
        print(f'Should be adding links to library ~ config')

        for album in self._get_candidate_albums(lib):
            cont, filtered_collaborators = self._prompt_user_about_collaborators(lib, album)
            if cont: # todo: this is not really clean though...
                self._add_links(album, filtered_collaborators)
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

        for query in [f'{k}::"{"|".join(v)}"' for k,v in self.SEPARATORS.items()] + self.QUERIES:
            for album in lib.albums(query=f"{query} {negation}"):
                if album['path'] not in [a['path'] for a in albums]:
                    albums.append(album)

        return albums

    def _is_candidate(self, album):
        # todo: check if album matches self.SEPARATORS, self.QUERIES and self.IGNORE
        pass

    def _get_all_splits(self, lib):
        # todo: get all albums with a non-empty "links" field
            # Links present -> links:"['path-to-link1', 'path-to-link2']"
            # Links were once present, but have been deleted: "[]"
        pass

    def _prompt_user_about_collaborators(self, lib, album):
        """ Prompt user whether it's okay to consider this album a split, and whether the list of collaborators is ok """

        filtered_collaborators = [
            c for c in self._get_collaborators(album)
            if len(lib.albums(query=f'albumartist:"{c}" ' + self.FILTER)) > self.MINIMUM
        ]

        if filtered_collaborators:
            print(f"Link album {album['albumartist']} - {album['album']} to contributing artists {filtered_collaborators}?")
                # todo: integrate with beets CLI system
                    # todo: add option to edit collaborator list (in JSON form)
                    # todo: add option to 'don't ask again' -> 'for this album' 'for this albumartist' => this sets album['dontlink'] to True
            if True:
                return True, filtered_collaborators

        return False, []




    def _add_links(self, album, collaborators):
        """ For every collaborator in album, add a link in their respective directories if they meet the conditions set in config """
        # todo: write link paths to album['links']
        # todo: make links with beets.util.link
        # todo: links should be relative

        album['collaborators'] = json.dumps(collaborators)



        pass

    def _remove_links(self, lib, album):
        # todo: remove links in album['links'], replace with []
        """ For every collaborator in album, remove link if present """
        pass

    def _get_collaborators(self, item):
        # todo: only return relevant collaborators (i.e. more than x albums, defined in config maybe?)
        # todo: split album['albumartist'] by
        # todo: return JSON formatted list -> write to album['links']

        if type(item) is Item:
            album = item.get_album()
        elif type(item) is Album:
            album = item
        else:
            return []

        return [s.strip() for s in re.split("|".join(self.SEPARATORS['albumartist']), album['albumartist'])]


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
        return self.parser.parse_args(args), [] # todo: why was this empty list needed again?
