import atexit
import os
import readline


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
            self.history_file = history_file
            self.history_length = history_len
            self._init_history(self.history_file, self.history_length)

    def _init_history(self, history_file, history_len):
        ''' Initialize the history file. '''
        try:
            readline.read_history_file(history_file)
            readline.set_history_length(history_len)
            retval = True
        except IOError:
            retval = False

        atexit.register(readline.write_history_file, history_file)
        return retval

    def _init_completer(self):
        ''' Initialize a completion provider function. '''
        def completer(text, state):
            results = [i for i in self.content if i.startswith(text)] + [None]
            return results[state]
        return completer

