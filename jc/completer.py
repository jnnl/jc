import atexit
import os
import readline
import sys


class Completer(object):
    '''
    Readline completer.

    Provides readline bindings, tab-completion and history for calculations.
    '''

    def __init__(self, content=[], history=True,
                 history_file=os.path.expanduser("~/.jc_history"),
                 history_len=1000):

        self.content = content
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self._init_completer())

        if history:
            try:
                open(history_file, 'a').close()
            except (IOError, OSError):
                sys.stderr.write(
                    'warning: failed to open history file {}, history will not be saved\n'
                    .format(history_file))
            else:
                self._init_history(history_file, history_len)

    def add_content(self, content):
        self.content.append(content)

    def _init_history(self, history_file, history_len):
        ''' Initialize the history file. '''
        readline.read_history_file(history_file)
        readline.set_history_length(history_len)
        atexit.register(readline.write_history_file, history_file)

    def _init_completer(self):
        ''' Initialize a completion provider function. '''
        def completer(text, state):
            results = [i for i in self.content if i.startswith(text)] + [None]
            return results[state]
        return completer

