import unittest

import jc


class EvalTestCase(unittest.TestCase):
    def setUp(self):
        self.e = jc.Evaluator(completer=None)


class ArithmeticTest(EvalTestCase):

    def test_addition(self):
        r = self.e.eval('1 + 2')
        self.assertEqual(r, [3])
        r = self.e.eval('0 + 0')
        self.assertEqual(r, [0])

    def test_subtraction(self):
        r = self.e.eval('2 - 1')
        self.assertEqual(r, [1])
        r = self.e.eval('1 - 2')
        self.assertEqual(r, [-1])

    def test_multiplication(self):
        r = self.e.eval('5 * 4')
        self.assertEqual(r, [20])
        r = self.e.eval('5 * 0')
        self.assertEqual(r, [0])

    def test_division(self):
        r = self.e.eval('10 / 5')
        self.assertEqual(r, [2])
        r = self.e.eval('21 / 5')
        self.assertEqual(r, [4.2])

    def test_floor_division(self):
        r = self.e.eval('10 // 5')
        self.assertEqual(r, [2])
        r = self.e.eval('21 // 5')
        self.assertEqual(r, [4])

    def test_modulo(self):
        r = self.e.eval('5 % 2')
        self.assertEqual(r, [1])
        r = self.e.eval('4 % 2')
        self.assertEqual(r, [0])

    def test_exponent(self):
        r = self.e.eval('2 ** 32')
        self.assertEqual(r, [4294967296])
        r = self.e.eval('2 ** -1')
        self.assertEqual(r, [0.5])

    def test_multiple(self):
        r = self.e.eval('(((2 ** 32) / 1024) * 12) % 52 + 9 - 5')
        self.assertEqual(r, [20])


class AssignmentTest(EvalTestCase):

    def test_assign(self):
        r = self.e.eval('a = 0')
        self.assertEqual(r, [])
        r = self.e.eval('a')
        self.assertEqual(r, [0])
        r = self.e.eval('a_var = 1.5')
        self.assertEqual(r, [])
        r = self.e.eval('a_var')
        self.assertEqual(r, [1.5])
        r = self.e.eval('a_var2 = 2')
        self.assertEqual(r, [])
        r = self.e.eval('a_var2')
        self.assertEqual(r, [2])

    def test_reassign(self):
        r = self.e.eval('a = 0')
        self.assertEqual(r, [])
        r = self.e.eval('a = 1')
        self.assertEqual(r, [])
        r = self.e.eval('a')
        self.assertEqual(r, [1])

    def test_const_assign_err(self):
        with self.assertRaises(jc.NamespaceError):
            r = self.e.eval('pi = 3.14')

    def test_int_assign_err(self):
        with self.assertRaises(jc.NamespaceError):
            r = self.e.eval('_version = 1.1')

    def test_int_space_assign_err(self):
        with self.assertRaises(jc.NamespaceError):
            r = self.e.eval('_dummy = 0')

    def test_ans_assign_err(self):
        with self.assertRaises(jc.NamespaceError):
            r = self.e.eval('ans = 0')

    def test_func_assign_err(self):
        with self.assertRaises(jc.NamespaceError):
            r = self.e.eval('sqrt = 0')

    def test_num_assign_err(self):
        with self.assertRaises(TypeError):
            r = self.e.eval('1 = 0')


class MultiExprTest(EvalTestCase):

    def test_multi_assign(self):
        r = self.e.eval('a = 1; b= 2; c =3; d=4')
        self.assertEqual(r, [])
        r = self.e.eval('a; b; c; d')
        self.assertEqual(r, [1, 2, 3, 4])

    def test_multi_reassign(self):
        r = self.e.eval('a = 1; a = 2; a = 3')
        self.assertEqual(r, [])
        r = self.e.eval('a')
        self.assertEqual(r, [3])

    def test_multi_expr(self):
        r = self.e.eval('x = 2; x ** 8; a = 4; x ** a')
        self.assertEqual(r, [256, 16])


class FunctionTest(EvalTestCase):

    def test_sqrt(self):
        r = self.e.eval('sqrt(16)')
        self.assertEqual(r, [4])

        r = self.e.eval('sqrt(0)')
        self.assertEqual(r, [0])

        # complex numbers are currently not supported
        with self.assertRaises(ValueError):
            r = self.e.eval('sqrt(-1)')

    def test_cbrt(self):
        r = self.e.eval('cbrt(27)')
        self.assertEqual(r, [3])

        r = self.e.eval('cbrt(100)')
        self.assertAlmostEqual(r[0], 4.6415888)

        # complex numbers are currently not supported
        with self.assertRaises((TypeError, ValueError)):
            r = self.e.eval('cbrt(-1)')

    def test_nrt(self):
        r = self.e.eval('nrt(5, 32)')
        self.assertEqual(r, [2])

        r = self.e.eval('nrt(8, 5)')
        self.assertAlmostEqual(r[0], 1.2228445)

    def test_abs(self):
        r = self.e.eval('abs(5.95)')
        self.assertEqual(r, [5.95])

        r = self.e.eval('abs(0)')
        self.assertEqual(r, [0])

        r = self.e.eval('abs(-1.1)')
        self.assertEqual(r, [1.1])

    def test_round(self):
        r = self.e.eval('round(5.5)')
        self.assertEqual(r, [6])

        r = self.e.eval('round(0)')
        self.assertEqual(r, [0])

        r = self.e.eval('round(1.49)')
        self.assertEqual(r, [1])

        r = self.e.eval('round(9.501)')
        self.assertEqual(r, [10])

    def test_ln(self):
        r = self.e.eval('ln(1)')
        self.assertEqual(r, [0])

        r = self.e.eval('ln(2)')
        self.assertAlmostEqual(r[0], 0.6931472)

        r = self.e.eval('ln(e)')
        self.assertEqual(r, [1])

        with self.assertRaises(ValueError):
            r = self.e.eval('ln(0)')


class BaseTest(EvalTestCase):

    def test_input_base(self):
        r = self.e.eval('0b1111')
        self.assertEqual(r, [15])

        r = self.e.eval('0o123')
        self.assertEqual(r, [83])

        r = self.e.eval('0x10')
        self.assertEqual(r, [16])

    def test_output_base(self):
        r = self.e.eval('base(2); 10')
        self.assertEqual(r, [1010])

        r = self.e.eval('base(8); 10')
        self.assertEqual(r, [12])

        r = self.e.eval('base(10); 10')
        self.assertEqual(r, [10])

        r = self.e.eval('base(16); 10')
        self.assertEqual(r, ['a'])

    def test_multi_base(self):
        r = self.e.eval('base(2); 10; base(8); 10; base(10); 10; base(16); 10')
        self.assertEqual(r, [1010, 12, 10, 'a'])

        r = self.e.eval('base(2); 0; base(8); 0; base(10); 0; base(16); 0')
        self.assertEqual(r, [0, 0, 0, '0'])

        r = self.e.eval('base(2); 10; base(10); base(2); 15')
        self.assertEqual(r, [1010, 1111])


class AnsTest(EvalTestCase):

    def test_ans(self):
        r = self.e.eval('ans')
        self.assertEqual(r, [])

        r = self.e.eval('100; ans')
        self.assertEqual(r, [100, 100])

        r = self.e.eval('ans; ans/100; (ans*20)/(ans*10); ans-ans')
        self.assertEqual(r, [100, 1, 2, 0])

        r = self.e.eval('ans; ans + 10.51; round(ans)')
        self.assertEqual(r, [0, 10.51, 11])

    def test_implicit_ans(self):
        r = self.e.eval('1; / 2')
        self.assertEqual(r, [1, 0.5])

        r = self.e.eval('* 10 + 50')
        self.assertEqual(r, [55])

        r = self.e.eval('/ 100; * 5 + 0.25')
        self.assertEqual(r, [0.55, 3])


class BitwiseTest(EvalTestCase):

    def test_and(self):
        r = self.e.eval('0b1011 & 0b1101')
        self.assertEqual(r, [9])
        r = self.e.eval('11 & 12')
        self.assertEqual(r, [8])

    def test_or(self):
        r = self.e.eval('0b1011 | 0b1101')
        self.assertEqual(r, [15])
        r = self.e.eval('3 | 8')
        self.assertEqual(r, [11])

    def test_xor(self):
        r = self.e.eval('0b1011 ^ 0b1101')
        self.assertEqual(r, [6])
        r = self.e.eval('3 ^ 8')
        self.assertEqual(r, [11])

    def test_inv(self):
        r = self.e.eval('~ 0b1011')
        self.assertEqual(r, [-12])
        r = self.e.eval('2 + ~-3')
        self.assertEqual(r, [4])

    def test_lshift(self):
        r = self.e.eval('1 << 10')
        self.assertEqual(r, [1024])
        r = self.e.eval('3 << 8')
        self.assertEqual(r, [768])

    def test_rshift(self):
        r = self.e.eval('2 >> 1')
        self.assertEqual(r, [1])
        r = self.e.eval('1024 >> 4')
        self.assertEqual(r, [64])
        r = self.e.eval('8 >> 8')
        self.assertEqual(r, [0])


if __name__ == '__main__':
    unittest.main()
