from beets.plugins import BeetsPlugin
from beets import ui
from beets.ui import Subcommand, get_path_formats, input_yn, UserError, print_
from beets.library import Item
from beets.dbcore.query import AndQuery, OrQuery, MatchQuery
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

    def __init__(self):
        super(LinkPlugin, self).__init__()

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
        pass

    def remove(self, lib, opts):
        print(f'Should be removing links from library')
        pass

    def _check_all_albums(self, 'lib', 'album'):
        """ For all albums in library, check whether they could be a split (will be slow, probably) """
        pass

    def _get_all_splits(self, lib):
        pass

    def _infer_if_split(self, lib, album):
        """ Infer whether album is a split based on config """
        pass

    def _prompt_user(self):
        """ Prompt user whether it's okay to consider this album a split, and whether the list of collaborators is ok """
        pass

    def _write_collaborators(self, lib, album):
        """ Save list of collaborators to album metadata """
        pass

    def _add_links(self, lib, album):
        """ For every collaborator in album, add a link in their respective directories if they meet the conditions set in config """
        pass

    def _remove_links(self, lib, album):
        """ For every collaborator in album, remove link if present """
        pass

    def commands(self):
        return [LinkCommand(self)]


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