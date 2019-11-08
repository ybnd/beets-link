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

    def commands(self):
        return [SplitsCommand(self)]


class SplitsCommand(Subcommand):
    name = 'splits'
    help = "add links to split and compilation albums to the contributing artists' directories"

    def __init__(self, plugin):
        super(SplitsCommand, self).__init__(self.name, self.help)