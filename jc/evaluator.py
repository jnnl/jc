#!/usr/bin/env python

'''
jc.py

A simple arithmetic calculator in the vein of bc.
Usage: jc.py [expression[; ...]]

TODO:
    - support arbitrary output base
    - support floats in non-decimal bases
    - support complex numbers
'''

from __future__ import print_function

import ast
import math
import operator
import re
import sys

from . import completer


class NamespaceError(Exception):
    pass


class Evaluator(object):
    '''
    Expression evaluator.
    Constructs ASTs from expressions and evaluates them.

    Supports standard arithmetic and binary calculations,
    variable assignments, basic functions, constants and base conversions.
    '''

    def __init__(self, base=10, completer=completer.Completer):
        self.ans = None

        self.operators = {
            ast.Add:      {'op': operator.add,      'symbol': '+'},
            ast.Sub:      {'op': operator.sub,      'symbol': '-'},
            ast.Mult:     {'op': operator.mul,      'symbol': '*'},
            ast.Div:      {'op': operator.truediv,  'symbol': '/'},
            ast.FloorDiv: {'op': operator.floordiv, 'symbol': '//'},
            ast.Mod:      {'op': operator.mod,      'symbol': '%'},
            ast.Pow:      {'op': operator.pow,      'symbol': '**'},
            ast.BitAnd:   {'op': operator.iand,     'symbol': '&'},
            ast.BitOr:    {'op': operator.ior,      'symbol': '|'},
            ast.BitXor:   {'op': operator.ixor,     'symbol': '^'},
            ast.LShift:   {'op': operator.lshift,   'symbol': '>>'},
            ast.RShift:   {'op': operator.rshift,   'symbol': '<<'},
            ast.UAdd:     {'op': operator.pos,      'symbol': '+'},
            ast.USub:     {'op': operator.neg,      'symbol': '-'},
        }

        self.symbols = [op['symbol'] for op in self.operators.values()]

        self.internal_variables = {
            '_base': base,
            '_version': '0.9'
        }

        self.variables = {}

        self.constants = {
            'e':   {'value': math.e,
                    'help': 'e: Euler\'s number / Napier\'s constant'},
            'pi':  {'value': math.pi,
                    'help': 'pi: 0.5 tau'},
            'phi': {'value': (1 + math.sqrt(5)) / 2,
                    'help': 'phi: the golden ratio'},
            'tau': {'value': math.pi * 2,
                    'help': 'tau: 2 pi'},
        }

        self.functions = {
            'A':     {'value': lambda m, n: n + 1 if m == 0 else \
                     (self.functions['A']['value'](m - 1, 1) if m > 0 and n == 0 else \
                     self.functions['A']['value'](m - 1, self.functions['A']['value'](m, n - 1))),
                     'help': 'A(x, y): Ackermann function'},
            'abs':   {'value': abs,
                      'help': 'abs(x): absolute value of x'},
            'acos':  {'value': math.acos,
                      'help': 'acos(x): inverse trigonometric cosine of x (in radians)'},
            'acosh': {'value': math.acosh,
                      'help': 'acosh(x): inverse hyperbolic cosine of x (in radians)'},
            'asin':  {'value': math.asin,
                      'help': 'asin(x): inverse trigonometric sine of x (in radians)'},
            'asinh': {'value': math.asinh,
                      'help': 'asinh(x): inverse hyperbolic sine of x (in radians)'},
            'atan':  {'value': math.atan,
                      'help': 'atan(x): inverse trigonometric tangent of x (in radians)'},
            'atanh': {'value': math.atanh,
                      'help': 'atanh(x): inverse hyperbolic tangent of x (in radians)'},
            'base': {'value': lambda x=None: self._set_base(x),
                      'help': 'base(x): set output base to x (2, 8, 10 or 16 allowed)'},
            'cbrt':  {'value': lambda x: x ** (1. / 3),
                      'help': 'cbrt(x): cube root of x'},
            'ceil':  {'value': math.ceil,
                      'help': 'ceil(x): ceiling function of x'},
            'cos':   {'value': math.cos,
                      'help': 'cos(x): cosine of x (in radians)'},
            'deg':   {'value': math.degrees,
                      'help': 'deg(x): convert x from radians to degrees'},
            'erf':   {'value': math.erf,
                      'help': 'erf(x): error function of x'},
            'exp':   {'value': math.exp,
                      'help': 'exp(x): calculate e ** x'},
            'fact':  {'value': math.factorial,
                      'help': 'fact(x): factorial of x'},
            'fmod':  {'value': math.fmod,
                      'help': 'fmod(x, y): calculate floating point modulo of x % y'},
            'floor': {'value': math.floor,
                      'help': 'floor(x): floor function of x'},
            'gamma': {'value': math.gamma,
                      'help': 'gamma(x): gamma function of x'},
            'help':  {'value': lambda x: self._help(x),
                      'help': 'help(x): print help on x'},
            'hyp':   {'value': math.hypot,
                      'help': 'hyp(x): hypotenuse of x'},
            'ln':    {'value': lambda x: math.log(x, math.e),
                      'help': 'ln(x): natural logarithm of x'},
            'log':   {'value': math.log,
                      'help': 'log(x[, base]): logarithm of x to base (default: 2)'},
            'log2':  {'value': lambda x: math.log(x, 2),
                      'help': 'log2(x): base 2 logarithm of x'},
            'log10': {'value': math.log10,
                      'help': 'log10(x): base 10 logarithm of x'},
            'nrt':   {'value': lambda n, x: x ** (1. / n),
                      'help': 'nrt(x): nth root of x'},
            'rad':   {'value': math.radians,
                      'help': 'rad(x): convert x from degrees to radians'},
            'round': {'value': round,
                      'help': 'round(x[, n]): round x to n decimal places (default: 0)'},
            'sin':   {'value': math.sin,
                      'help': 'sin(x): sine of x'},
            'sqrt':  {'value': math.sqrt,
                      'help': 'sqrt(x): square root of x'},
            'tan':   {'value': math.tan,
                      'help': 'tan(x): tangent of x'},
        }

        self.completer = completer(
            list([k + '(' for k in self.functions.keys()]) +
            list(self.constants.keys()) +
            list(self.variables.keys()) +
            ['ans']
        )

    def _help(self, args):
        ''' Print help for given topics. '''
        if not len(args):
            get_help = lambda x: '\n'.join(c['help'] for c in x.values())
            print('jc version %s' % self.internal_variables['_version'])
            print('\nAvailable constants:')
            print(get_help(self.constants))
            print('\nAvailable functions:')
            print(get_help(self.functions))

        for arg in args:
            msg = self.constants.get(arg.id, self.functions.get(arg.id, {})).get('help')
            if msg:
                print(msg)
            else:
                raise ValueError('unknown help topic \'%s\'' % arg.id)

    def _set_base(self, base):
        if base is None:
            print(self.internal_variables['_base'])
            return
        if base not in (2, 8, 10, 16):
            raise ValueError('unsupported base \'%s\' (allowed: 2, 8, 10, 16)' % base)
        self.internal_variables['_base'] = base

    def _get_op(self, operator):
        try:
            found_op = self.operators[type(operator.op)]['op']
        except KeyError:
            raise SyntaxError('unknown operator \'%s\'' % operator.op)
        return found_op

    def _eval_unary_op(self, operator):
        ''' Evaluate unary operator (e.g. -1) '''
        op = self._get_op(operator)
        value = op(self._eval_op(operator.operand))
        return value

    def _eval_binary_op(self, operator):
        ''' Evaluate binary operator (e.g. 5 + 5). '''
        op = self._get_op(operator)
        value = op(self._eval_op(operator.left), self._eval_op(operator.right))
        return value

    def _eval_name(self, operator):
        ''' Evaluate name expansion / assignment (e.g. a = 10). '''
        if operator.id in self.constants:
            return self.constants[operator.id]['value']
        elif operator.id in self.internal_variables:
            return self.internal_variables[operator.id]
        elif operator.id in self.variables:
            return self.variables[operator.id]
        elif operator.id == 'ans':
            return self.ans
        elif operator.id in self.functions:
            raise TypeError('cannot evaluate function label \'%s\'' % operator.id)
        else:
            raise NameError('variable \'%s\' is not defined' % operator.id)

    def _eval_func(self, operator):
        ''' Evaluate function call (e.g. sqrt(16)). '''
        if operator.func.id in self.functions:
            func = self.functions[operator.func.id]['value']
            if operator.func.id == 'help':
                return func(operator.args)
            value = func(*(self._eval_op(arg) for arg in operator.args))
            return value
        else:
            raise NameError('function \'%s\' is not defined' % operator.func.id)

    def _eval_op(self, op):
        ''' Evaluate expression operator. '''
        if isinstance(op, ast.Num):
            val = op.n
        elif isinstance(op, ast.UnaryOp):
            val = self._eval_unary_op(op)
        elif isinstance(op, ast.BinOp):
            val = self._eval_binary_op(op)
        elif isinstance(op, ast.Name):
            val = self._eval_name(op)
        elif isinstance(op, ast.Call):
            val = self._eval_func(op)
        else:
            raise SyntaxError('unknown operator \'%s\'' % op)

        return val

    def _validate_var(self, var):
        ''' Validate a variable assignment. '''
        if var in self.constants:
            raise NamespaceError('cannot assign to constant \'%s\'' % var)
        elif var in self.internal_variables:
            raise NamespaceError('cannot assign to internal variable \'%s\'' % var)
        elif var in self.functions:
            raise NamespaceError('cannot override existing function \'%s\'' % var)
        elif var.startswith('_'):
            raise NamespaceError('cannot assign to internal variable space (starting with _)')
        elif var == 'ans':
            raise NamespaceError('cannot assign to reserved variable \'ans\'')
        elif var.isdigit():
            raise TypeError('cannot assign variable to a numeric literal')
        elif re.match(r'\w+', var):
            return True
        else:
            raise NameError('invalid variable name \'%s\', only alphanumerics and underscores are supported' % var)

    def _assign_var(self, var_name, expr_value):
        ''' Assign a value to a variable. '''
        self._validate_var(var_name)
        tree = ast.parse(expr_value, mode='eval')
        value = self._eval_op(tree.body)
        self.variables[var_name] = value
        self.completer.content.append(var_name)

        return value

    def _convert_out(self, result):
        ''' Convert output result to defined base. '''
        base = self.internal_variables['_base']
        if base == 2:
            return int(bin(int(result))[2:])
        elif base == 8:
            if sys.version_info >= (3, 0, 0):
                return int(oct(int(result))[2:])
            else:
                if result == 0: return int(oct(int(result)))
                else: return int(oct(int(result))[1:])
        elif base == 10:
            if result - int(result) == 0:
                return int(result)
            else:
                return result
        elif base == 16:
            return hex(result)[2:]
        else:
            raise ValueError('unsupported base value \'%s\'' % base)

    def _eval_expr(self, expr):
        ''' Evaluate a single expression. '''
        if self.ans is not None and len(expr) and expr[0] in self.symbols:
            expr = 'ans' + expr

        tree = ast.parse(expr, mode='eval')
        result = self._eval_op(tree.body)

        if result is not None:
            self.ans = result
            result = self._convert_out(result)

        return result

    def evaluate(self, expr, results=None):
        ''' Build and evaluate the AST for an expression, return the result(s). '''
        if results is None:
            results = []

        expr = expr.strip()

        multi_expr = ';' in expr
        if multi_expr:
            exprs = expr.split(';')
            expr = exprs[0]
            rest = ';'.join(exprs[1:])

        if not len(expr):
            return results
        elif expr.startswith('#'):
            return results

        var_assign = re.search(r'(?P<var>^\w+\s*)\=(?P<val>\s*(.*?)$)', expr)
        if var_assign:
            var_assign = var_assign.groupdict()
            var_name = var_assign['var'].strip()
            var_value = var_assign['val'].strip()
            self._assign_var(var_name, var_value)
        else:
            result = self._eval_expr(expr)
            if result is not None:
                results.append(result)

        if multi_expr:
            self.evaluate(rest, results)

        return results
