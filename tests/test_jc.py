import unittest

import jc


class ArithmeticTest(unittest.TestCase):

    def setUp(self):
        self.e = jc.Evaluator()

    def test_addition(self):
        r = self.e.evaluate('1 + 2')
        self.assertEqual(r, [3])
        r = self.e.evaluate('0 + 0')
        self.assertEqual(r, [0])

    def test_subtraction(self):
        r = self.e.evaluate('2 - 1')
        self.assertEqual(r, [1])
        r = self.e.evaluate('1 - 2')
        self.assertEqual(r, [-1])

    def test_multiplication(self):
        r = self.e.evaluate('5 * 4')
        self.assertEqual(r, [20])
        r = self.e.evaluate('5 * 0')
        self.assertEqual(r, [0])

    def test_division(self):
        r = self.e.evaluate('10 / 5')
        self.assertEqual(r, [2])
        r = self.e.evaluate('21 / 5')
        self.assertEqual(r, [4.2])

    def test_floor_division(self):
        r = self.e.evaluate('10 // 5')
        self.assertEqual(r, [2])
        r = self.e.evaluate('21 // 5')
        self.assertEqual(r, [4])

    def test_modulo(self):
        r = self.e.evaluate('5 % 2')
        self.assertEqual(r, [1])
        r = self.e.evaluate('4 % 2')
        self.assertEqual(r, [0])

    def test_exponent(self):
        r = self.e.evaluate('2 ** 32')
        self.assertEqual(r, [4294967296])
        r = self.e.evaluate('2 ** -1')
        self.assertEqual(r, [0.5])

    def test_multiple(self):
        r = self.e.evaluate('(((2 ** 32) / 1024) * 12) % 52 + 9 - 5')
        self.assertEqual(r, [20])


class AssignmentTest(unittest.TestCase):

    def setUp(self):
        self.e = jc.Evaluator()

    def test_assign(self):
        r = self.e.evaluate('a = 0')
        self.assertEqual(r, [])
        r = self.e.evaluate('a')
        self.assertEqual(r, [0])

    def test_reassign(self):
        r = self.e.evaluate('a = 0')
        self.assertEqual(r, [])
        r = self.e.evaluate('a = 1')
        self.assertEqual(r, [])
        r = self.e.evaluate('a')
        self.assertEqual(r, [1])


class MultiExprTest(unittest.TestCase):

    def setUp(self):
        self.e = jc.Evaluator()

    def test_multi_assign(self):
        r = self.e.evaluate('a = 1; b= 2; c =3; d=4')
        self.assertEqual(r, [])
        r = self.e.evaluate('a; b; c; d')
        self.assertEqual(r, [1, 2, 3, 4])

    def test_multi_reassign(self):
        r = self.e.evaluate('a = 1; a = 2; a = 3')
        self.assertEqual(r, [])
        r = self.e.evaluate('a')
        self.assertEqual(r, [3])

    def test_multi_expr(self):
        r = self.e.evaluate('x = 2; x ** 8; a = 4; x ** a')
        self.assertEqual(r, [256, 16])


class FunctionTest(unittest.TestCase):

    def setUp(self):
        self.e = jc.Evaluator()

    def test_sqrt(self):
        r = self.e.evaluate('sqrt(16)')
        self.assertEqual(r, [4])

        r = self.e.evaluate('sqrt(0)')
        self.assertEqual(r, [0])

        # complex numbers are currently not supported
        with self.assertRaises(ValueError):
            r = self.e.evaluate('sqrt(-1)')

    def test_cbrt(self):
        r = self.e.evaluate('cbrt(27)')
        self.assertEqual(r, [3])

        r = self.e.evaluate('cbrt(100)')
        self.assertAlmostEqual(r[0], 4.6415888)

        # complex numbers are currently not supported
        with self.assertRaises((TypeError, ValueError)):
            r = self.e.evaluate('cbrt(-1)')

    def test_nrt(self):
        r = self.e.evaluate('nrt(5, 32)')
        self.assertEqual(r, [2])

        r = self.e.evaluate('nrt(8, 5)')
        self.assertAlmostEqual(r[0], 1.2228445)

    def test_abs(self):
        r = self.e.evaluate('abs(5.95)')
        self.assertEqual(r, [5.95])

        r = self.e.evaluate('abs(0)')
        self.assertEqual(r, [0])

        r = self.e.evaluate('abs(-1.1)')
        self.assertEqual(r, [1.1])

    def test_round(self):
        r = self.e.evaluate('round(5.5)')
        self.assertEqual(r, [6])

        r = self.e.evaluate('round(0)')
        self.assertEqual(r, [0])

        r = self.e.evaluate('round(1.49)')
        self.assertEqual(r, [1])

        r = self.e.evaluate('round(9.501)')
        self.assertEqual(r, [10])

    def test_ln(self):
        r = self.e.evaluate('ln(1)')
        self.assertEqual(r, [0])

        r = self.e.evaluate('ln(2)')
        self.assertAlmostEqual(r[0], 0.6931472)

        r = self.e.evaluate('ln(e)')
        self.assertEqual(r, [1])

        with self.assertRaises(ValueError):
            r = self.e.evaluate('ln(0)')


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.e = jc.Evaluator()

    def test_input_base(self):
        r = self.e.evaluate('0b1111')
        self.assertEqual(r, [15])

        r = self.e.evaluate('0o123')
        self.assertEqual(r, [83])

        r = self.e.evaluate('0x10')
        self.assertEqual(r, [16])

    def test_output_base(self):
        r = self.e.evaluate('base(2); 10')
        self.assertEqual(r, [1010])

        r = self.e.evaluate('base(8); 10')
        self.assertEqual(r, [12])

        r = self.e.evaluate('base(10); 10')
        self.assertEqual(r, [10])

        r = self.e.evaluate('base(16); 10')
        self.assertEqual(r, ['a'])

    def test_multi_base(self):
        r = self.e.evaluate('base(2); 10; base(8); 10; base(10); 10; base(16); 10')
        self.assertEqual(r, [1010, 12, 10, 'a'])

        r = self.e.evaluate('base(2); 0; base(8); 0; base(10); 0; base(16); 0')
        self.assertEqual(r, [0, 0, 0, '0'])

        r = self.e.evaluate('base(2); 10; base(10); base(2); 15')
        self.assertEqual(r, [1010, 1111])


class MiscellaneousTest(unittest.TestCase):
    def setUp(self):
        self.e = jc.Evaluator()

    def test_ans(self):
        r = self.e.evaluate('ans')
        self.assertEqual(r, [])

        r = self.e.evaluate('100; ans')
        self.assertEqual(r, [100, 100])

        r = self.e.evaluate('ans; ans/100; (ans*20)/(ans*10); ans-ans')
        self.assertEqual(r, [100, 1, 2, 0])

        r = self.e.evaluate('ans; ans + 10.51; round(ans)')
        self.assertEqual(r, [0, 10.51, 11])

    def test_implicit_ans(self):
        r = self.e.evaluate('1; / 2')
        self.assertEqual(r, [1, 0.5])

        r = self.e.evaluate('* 10 + 50')
        self.assertEqual(r, [55])

        r = self.e.evaluate('/ 100; * 5 + 0.25')
        self.assertEqual(r, [0.55, 3])


if __name__ == '__main__':
    unittest.main()
