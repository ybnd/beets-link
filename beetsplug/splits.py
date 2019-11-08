from beets.plugins import BeetsPlugin
from beets import ui
from beets.ui import Subcommand, get_path_formats, input_yn, UserError, print_
from beets.library import Item
from beets.dbcore.query import AndQuery, OrQuery, MatchQuery
from beets.util import mkdirall, normpath, syspath
import beets.autotag.hooks as hooks
import os

class SplitsPlugin(BeetsPlugin):
    def __init__(self):
        super(SplitsPlugin).__init__()

        self.config.add({

        })

        self.register_listener('album_imported', self.infer_split)

    def infer_split(self, lib, album):
        """ Check for split/compilation 'flags':
                - comp:T?
                    * maybe: separate comp into comp and split, add option for additional fields
                - not all tracks have the same artist?
                - albumartist field contains (configurable) separator(s), e.g. `/`, `&`, `,`, `and`, `with`, `feat`?
                    * separated artists already in library?

                -> prompt user if uncertain

                * also handle case when imported album is NOT a split, but is BY an artist which only had splits previously!
        """
        pass

    def _link_split(self):
        """ Add symlinks to split to all relevant albumartist directories; create if not already present
        """
        pass

    def commands(self):
        return [SplitsCommand(self)]


class SplitsCommand(Subcommand):
    name = 'splits'
    help = "add links to split and compilation albums to the contributing artists' directories"

    def __init__(self, plugin):
        super(SplitsCommand, self).__init__(self.name, self.help)