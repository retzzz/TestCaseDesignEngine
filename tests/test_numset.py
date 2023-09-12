import unittest

from tda_engine.numset import Interval, emptySet, inf, _Inf
from tda_engine.numset import SetOperationError, NumSet, union, intersection

class Test_Interval(unittest.TestCase):

    def test_inf(self):
        self.assertTrue(1234567890 < inf)
        self.assertTrue(-inf < 0)
        self.assertTrue(-1234567890.234 > -inf)
        self.assertTrue(+inf > 0.234)
        self.assertTrue(-inf < +inf)
        self.assertTrue(inf > -inf)
        self.assertFalse(1234567890 >= inf)
        self.assertTrue(inf >= inf)
        self.assertFalse(123 <= -inf)
        self.assertTrue(-inf <= -inf)
        self.assertTrue(+inf == inf)
        self.assertFalse(212.41 == inf)
        self.assertFalse(+inf != inf)
        self.assertIsNot(-inf, inf)
        self.assertIs(+inf, inf)
        userinf = _Inf()
        self.assertIs(userinf, inf)
        self.assertIs(userinf, -(-inf))

    def test_init_int(self):
        #int interval [1,2)
        a = Interval(True, 1, 2, False)
        b = Interval('[', 1, 2, ')')
        c = Interval('[1, 2)')
        d = Interval(1, 2, 'LeftCloseRightOpen')
        e = Interval(1, 2, lower_included = True)
        f = Interval(lower = 1, upper = 2, lower_included = True)

        self.assertEqual(a.lower, 1)
        self.assertTrue(a.lower_included)
        self.assertEqual(a.upper, 2)
        self.assertFalse(a.upper_included)
        self.assertIs(a.type_, int)
        self.assertEqual(a, b)
        self.assertEqual(a, c)
        self.assertEqual(a, d)
        self.assertEqual(a, e)
        self.assertEqual(a, f)

    def test_init_float(self):
        #float interval (1.0, 2.0]
        a = Interval(False, 1.0, 2, True)
        b = Interval('(', 1.0, 2.0, ']')
        c = Interval('(1, 2.0]')
        d = Interval(1.0, 2, 'LeftOpenRightClose')
        e = Interval(1.0, 2.0, upper_included = True)
        f = Interval(lower = 1.0, upper = 2.0, upper_included = True, lower_included = False)
        self.assertEqual(a.lower, 1.0)
        self.assertFalse(a.lower_included)
        self.assertEqual(a.upper, 2.0)
        self.assertTrue(a.upper_included)
        self.assertIs(a.type_, float)
        self.assertEqual(a, b)
        self.assertEqual(a, c)
        self.assertEqual(a, d)
        self.assertEqual(a, e)
        self.assertEqual(a, f)

    def test_init_positive_inf(self):
        # int > 1
        a = Interval(False, 1, inf, False)
        a1 = Interval('(', 1, +inf, ')')
        a2 = Interval('(1, +inf)')
        a3 = Interval(1, inf, 'Open')
        a4 = Interval(1, inf, upper_included = False, lower_included = False)
        a5 = Interval(1, +inf)
        a6 = Interval(1, '+inf')
        a7 = Interval(1, 'inf')
        a8 = Interval(lower = 1, upper = inf, upper_included = False, lower_included = False)
        a9 = Interval(lower = 1, upper = +inf)
        self.assertEqual(a.lower, 1)
        self.assertEqual(a.upper, inf)
        self.assertIs(a.upper, inf)
        self.assertIs(a.type_, int)
        self.assertFalse(a.lower_included)
        self.assertFalse(a.upper_included)
        self.assertEqual(a, a1)
        self.assertEqual(a, a2)
        self.assertEqual(a, a3)
        self.assertEqual(a, a4)
        self.assertEqual(a, a5)
        self.assertEqual(a, a6)
        self.assertEqual(a, a7)
        self.assertEqual(a, a8)
        self.assertEqual(a, a9)

    def test_init_negtive_inf(self):
        # int <= -2e5
        a = Interval(False, -inf, -2e5, True)
        a1 = Interval('(', -inf, -2e5, ']')
        a2 = Interval('(-inf, -2e5]')
        a3 = Interval(-inf, -2e5, 'LeftOpenRightClose')
        a4 = Interval(-inf, -2e5, upper_included = True, lower_included = False)
        a5 = Interval('-inf', -2e5, upper_included = True)
        a6 = Interval(lower = -inf, upper = -2e5, upper_included = True, lower_included = False)
        self.assertEqual(a.lower, -inf)
        self.assertIs(a.lower, -inf)
        self.assertEqual(a.upper, -2e5)
        self.assertIs(a.type_, float)
        self.assertFalse(a.lower_included)
        self.assertTrue(a.upper_included)
        self.assertEqual(a, a1)
        self.assertEqual(a, a2)
        self.assertEqual(a, a3)
        self.assertEqual(a, a4)
        self.assertEqual(a, a5)
        self.assertEqual(a, a6)

    def test_singloten(self):
        # singloten set
        a = Interval(True, 1, 1, True)
        a1 = Interval('[', 1, 1, ']')
        a2 = Interval('[1,1]')
        a3 = Interval(1, 1, 'Close')
        a4 = Interval(1, 1, upper_included = True, lower_included = True)
        a5 = Interval("1")
        a5 = Interval(1)
        self.assertEqual(a.lower, 1)
        self.assertEqual(a.upper, 1)
        self.assertIs(a.type_, int)
        self.assertTrue(a.lower_included)
        self.assertTrue(a.upper_included)

    def test_exception(self):
        #exception
        #left > right
        self.assertRaises(AssertionError, Interval, 2, 1)
        self.assertRaises(AssertionError, Interval, '(2.0, 1.9)')
        self.assertRaises(AssertionError, Interval, '(inf, 1]')
        #left == right but not close
        self.assertRaises(AssertionError, Interval, True, 1, 1, ')')
        self.assertRaises(AssertionError, Interval, '(1,1]')
        self.assertRaises(AssertionError, Interval, '[1.0,1.0)')
        self.assertRaises(AssertionError, Interval, '(2e3,2e3)')
        #left == inf but not close
        # self.assertRaises(AssertionError, Interval, '[-inf,1)')
        # self.assertRaises(AssertionError, Interval, '(', 0, +inf, ']')
        self.assertRaises(SetOperationError, Interval, '(abc,0]')
        self.assertRaises(SetOperationError, Interval, 'abc,0')
        with self.assertRaises(AssertionError):
            Interval('[-5, 0)').intersection(Interval('[0, 5)'))

    def test_other_literals(self):
        a = Interval('[0xabcd, 0xffff]')
        self.assertEqual(a.lower, 0xabcd)
        self.assertEqual(a.upper, 0xffff)
        self.assertIs(a.type_, int)
        a = Interval('[0b10101, 0o777]')
        self.assertEqual(a.lower, 0b10101)
        self.assertEqual(a.upper, 0o777)
        self.assertIs(a.type_, int)
        a = Interval('[-0b10_101, +0o7_7_7]')
        self.assertEqual(a.lower, -0b10101)
        self.assertEqual(a.upper, +0o777)
        self.assertIs(a.type_, int)
        a = Interval('[-1., +.1]')
        self.assertEqual(a.lower, -1.0)
        self.assertEqual(a.upper, +0.1)
        self.assertIs(a.type_, float)
        a = Interval('[-2e-5, +3.0e+3]')
        self.assertEqual(a.lower, -2e-5)
        self.assertEqual(a.upper, 3000.0)
        self.assertIs(a.type_, float)

    def test_in(self):
        self.assertTrue(0 in Interval('[-1, 1]'))
        self.assertTrue(0.5 in Interval('[-1, 1]'))
        self.assertTrue(-1 in Interval('[-1, 1]'))
        self.assertTrue(1 in Interval('[-1, 1]'))
        self.assertTrue(1.1 in Interval('(-1.1, 1.1]'))
        self.assertTrue(-1e10 in Interval('(-inf, 1.1]'))
        self.assertTrue(-inf in Interval('(-inf, inf)'))
        self.assertTrue(+inf in Interval('(-inf, inf)'))

        self.assertFalse(-1.1 in Interval('(-1.1, 1.1]'))
        self.assertFalse(1.1 in Interval('(-1.1, 1.1)'))
        self.assertFalse(inf in Interval('(-1.1, 1.1]'))
        self.assertFalse(-inf in Interval('(-1.1, 1.1]'))
        self.assertFalse(1.100001 in Interval('(-1.1, 1.1]'))

        self.assertTrue(Interval('[-1, 1]') in Interval('(-1.1, 1.1]'))
        self.assertTrue(Interval('[-1, 1.1]') in Interval('(-1.1, 1.1]'))
        self.assertFalse(Interval('[-1.1, 1.1]') in Interval('(-1.1, 1.1]'))
        self.assertFalse(Interval('[-1, 1.1001]') in Interval('(-1.1, 1.1]'))

    def test_overlap(self):
        self.assertTrue(Interval('[-1, 1]').overlap(Interval('(-1.1, 1.1]')))
        self.assertTrue(Interval('[1.1, 2]').overlap(Interval('(-1.1, 1.1]')))
        self.assertFalse(Interval('[-2, -1.1]').overlap(Interval('(-1.1, 1.1]')))
        self.assertFalse(Interval('[-2, -1.1]').overlap(Interval('(-1.1, 1.1]')))

        self.assertFalse(Interval('[-2.1, -1.1]').overlap(Interval('(-1.1, inf)')))
        self.assertTrue(Interval('[-2.1, -1.1]').overlap(Interval('(-inf, 1.1]')))

    def test_union(self):
        self.assertEqual(Interval('[-5, 0]').union(Interval('(-1, 5)')), Interval('[-5,5)'))
        self.assertEqual(Interval('(-inf, 0]').union(Interval('(-1, inf)')), Interval('(-inf,inf)'))
        self.assertEqual(Interval('(-1.0, 0]').union(Interval('(0, inf)')), Interval('(-1.0,inf)'))
        with self.assertRaises(AssertionError):
            Interval('(-1.0, 0)').union(Interval('(0, inf)'))

    def test_intersection(self):
        self.assertEqual(Interval('[-5, 0]').intersection(Interval('(-1, 5)')), Interval('(-1,0]'))
        self.assertEqual(Interval('(-inf, 0]').intersection(Interval('(-1, inf)')), Interval('(-1,0]'))
        self.assertEqual(Interval('[-5, 0]').intersection(Interval('[0, 5)')), Interval('[0,0]'))

    def test_compare(self):
        self.assertLess(Interval('[-5, 0]'), Interval('(-1,-0.5]'))
        self.assertLess(Interval('[-5, 0]'), Interval('(-5,0]'))
        self.assertLess(Interval('(-inf, 0]'), Interval('(-1000,0]'))
        self.assertGreater(Interval('[-5, 0]'), Interval('(-1,-0.5]'))
        self.assertGreater(Interval('[-5, 0]'), Interval('(-1,0.0)'))
        self.assertGreater(Interval('[-5, inf)'), '(-1,1000)')
        self.assertEqual(Interval('(1,inf)'), '(1, inf)')

    def test_str(self):
        self.assertEqual(str(Interval('[-5.0, 0]')), '[-5.0, 0.0]')
        self.assertEqual(str(Interval('[-0xa, 0]')), '[-10, 0]')
        self.assertEqual(str(Interval('(-inf, 0]')), '(-inf, 0]')
        self.assertEqual(str(Interval('(-inf, inf)')), '(-inf, +inf)')

class Test_NumSet(unittest.TestCase):
    def test_init(self):
        self.assertEqual(NumSet(r'(1,4), [5,8], [2,7)'), '(1, 8]')
        self.assertEqual(NumSet(r'(-inf, -1), (1,4), [5,8], [2,7)'), '(-inf, -1), (1, 8]')
        self.assertEqual(NumSet([Interval(1,4), Interval('[4,8]'), Interval(False, 8, 100, True)]), '(1, 100]')
        self.assertEqual(NumSet(r'(1,4), (-inf,8], [2,20]'), '(-inf, 20]')
        self.assertRaises(AssertionError, NumSet, 'abc')
        self.assertRaises(AssertionError, NumSet, '2,inf]')

    def test_union(self):
        a = NumSet('[1,4)')
        b = a.union('[3,5], [10,20]')
        self.assertEqual(a, NumSet('[1,5],[10,20]'))
        self.assertIs(a, b)
        self.assertEqual(union('(-inf, -100]', '(1,4), (3,6)', Interval(-200, -50)), '(-inf, -50), (1,6)')

    def test_intersection(self):
        a = NumSet('[1,4)')
        b = a.intersection('[3,5], [10,20]')
        self.assertEqual(a, NumSet('[3,4)'))
        self.assertIs(a, b)
        a = intersection('(-inf, -100]', '(1,4), (3,6)', Interval(-200, -50))
        self.assertEqual(a, NumSet())
        a = intersection('(-inf, -100]', Interval(-200, -50))
        self.assertEqual(a, NumSet('(-200, -100]'))

if __name__ == '__main__':
    unittest.main()

