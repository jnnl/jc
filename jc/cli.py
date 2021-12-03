from __future__ import print_function

import os
import sys
import traceback

import jc

if sys.version_info < (3, 0, 0):
    exec('input = raw_input')

debug = os.environ.get('JC_DEBUG', False) == '1'

def handle_error(error, exit_on_error=True):
    print('ERROR: %s' % error, file=sys.stderr)
    if debug:
        traceback.print_exc()
    if exit_on_error:
        sys.exit(1)

def single_calc(e):
    # single calculation mode
    try:
        results = e.eval(''.join(sys.argv[1:]))
        for result in results:
            print(result)
    except Exception as error:
        handle_error(error)

def interactive_calc(e):
    # interactive mode
    while True:
        try:
            expr = input('> ')
            while expr.rstrip().endswith('\\'):
                expr = ''.join(expr.rsplit('\\')[:1]).rstrip()
                expr += input('>> ')
            results = e.eval(expr)
            for result in results:
                print(result)
        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit()
        except Exception as error:
            handle_error(error, exit_on_error=False)

def piped_calc(e):
    # piped mode
    try:
        expr = ';'.join(sys.stdin.readlines())
        results = e.eval(expr)
        for result in results:
            print(result)
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)
    except Exception as error:
        handle_error(error)

def main():
    e = jc.Evaluator()

    if len(sys.argv) > 1:
        single_calc(e)
    elif sys.stdin.isatty():
        interactive_calc(e)
    else:
        piped_calc(e)


if __name__ == '__main__':
    main()
