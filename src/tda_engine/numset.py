import re
from typing import Self, Optional

int_base16_pattern = r'([\+\-]?0[xX][\dabcdefABCDEF_]+)'
int_base10_pattern = r'([\+\-]?[\d_]+)'
int_base8_pattern = r'([\+\-]?0[oO][01234567_]+)'
int_base2_pattern = r'([\+\-]?0[bB][01_]+)'
# order matters
int_pattern =  '(' + int_base16_pattern + '|' + int_base8_pattern + '|' + int_base2_pattern  + '|' + int_base10_pattern + ')'

pointfloat_pattern = r'([\+\-]?[\d_]*\.[\d_]*)'
exponentfloat_pattern = r'([\+\-]?[\d\.]+[eE][\+\-]?\d+)'
float_pattern = '(' + exponentfloat_pattern + '|' + pointfloat_pattern + ')'

number_pattern = '(' + float_pattern + '|' + int_pattern + ')'
inf_pattern = r'([\+\-]?inf)'
interval_item_pattern = '(' + number_pattern + '|' + inf_pattern + ')'
interval_pattern = r"([\[\(])\s*" + interval_item_pattern + r'\s*,\s*' + interval_item_pattern + r'\s*([\]\)])'
set_item_pattern = '(' + interval_pattern + '|' + number_pattern + ')'
set_full_pattern = '(' + set_item_pattern + r')(\s*,\s*' + set_item_pattern + ')*'
#(-inf, 3], 0xabcd, (1.23, 5.46), (0,1), (2e5, 6.2e8], [12345, inf), (-inf, inf), (0xabcd, 0xffff), 234, 0b1010101, 0o12345, +123497867
class SetOperationError(ArithmeticError):
    pass

# class Singleton(type):
    # _instances = {}
    # def __call__(cls, *args, **kwargs):
        # if cls not in cls._instances:
            # cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        # return cls._instances[cls]

# class Singleton(object):
    # _instance = None
    # def __new__(class_, *args, **kwargs):
        # if not isinstance(class_._instance, class_):
            # class_._instance = object.__new__(class_, *args, **kwargs)
        # return class_._instance

# class EmptySet(metaclass = Singleton):
    # pass

# class Inf(metaclass = Singleton):
    # pass

class _EmptySet():
    _instance = None
    def __new__(cls, *args, **kwargs):
        #singloten class
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

class _Inf():
    _instance = []
    def __new__(cls, *args, **kwargs):
        #dual element
        if len(cls._instance) == 0:
            cls._instance.append(object.__new__(cls, *args, **kwargs))
            cls._instance[0].sign = '+'
            cls._instance.append(object.__new__(cls, *args, **kwargs))
            cls._instance[1].sign = '-'
        return cls._instance[0]

    def __neg__(self)->Self:
        if self is self._instance[0]:
            return self._instance[1]
        else:
            return self._instance[0]

    def __pos__(self):
        return self

    def __lt__(self, other:int|float|Self) -> bool:
        if isinstance(other, _Inf):
            if self.sign == '-' and other.sign == '+':
                return True
        else:
            if self.sign == '-':
                return True
        return False

    def __gt__(self, other:int|float|Self) -> bool:
        if isinstance(other, _Inf):
            if self.sign == '+' and other.sign == '-':
                return True
        else:
            if self.sign == '+':
                return True
        return False

    def __le__(self, other:int|float|Self) -> bool:
        if isinstance(other, _Inf):
            if other.sign == '+' or other.sign == self.sign:
                return True
        else:
            if self.sign == '-':
                return True
        return False

    def __ge__(self, other:int|float|Self) -> bool:
        if isinstance(other, _Inf):
            if other.sign == '-' or other.sign == self.sign:
                return True
        else:
            if self.sign == '+':
                return True
        return False

    def __eq__(self, other:int|float|Self) -> bool:
        if isinstance(other, _Inf):
            if self.sign == other.sign:
                return True
        # return False

    def __ne__(self, other:int|float|Self) -> bool:
        if isinstance(other, _Inf):
            if self.sign == other.sign:
                return False
        return True
    def __str__(self):
        return f'{self.sign}inf'

emptySet = _EmptySet()
inf = _Inf()

class Interval:
    def __init__(self, *args, **kwargs):
        # examples: (-inf, 3], (1.23, 5.46), (0,1), (2e5, 6.2e8], [12345, inf), (-inf, inf)
        assert len(args) <= 4
        lower = None
        upper = None
        lower_included = False
        upper_included = False
        if len(args) == 0:
            # example
            assert 2 <= len(kwargs) <= 4
            assert 'lower' in kwargs
            assert 'upper' in kwargs
            lower = kwargs['lower']
            upper = kwargs['upper']
            lower_included = kwargs['lower_included'] if 'lower_included' in kwargs else False
            upper_included = kwargs['upper_included'] if 'upper_included' in kwargs else False
        elif len(args) == 1:
            if isinstance(args[0], str):
                s = args[0].strip().lower()
                # interval_pattern = re.compile(r"([\[\(])\s*([0-9\.\+\-abcdefox]+|[\+\-]?inf)\s*,\s*([0-9\.\+\-abcdefox]+|[\+\-]?inf)\s*([\]\)])")
                if m := re.fullmatch(interval_pattern, s):
                    lower_included = m.group(1)
                    lower = m.group(2)
                    upper = m.group(13)
                    upper_included = m.group(24)
                else:
                    lower = upper = s
                    lower_included = upper_included = True
            else:
                lower = upper = args[0]
                lower_included = upper_included = True

        elif len(args) == 2:
            # default: open set
            assert len(kwargs) <= 2
            lower = args[0]
            upper = args[1]
            lower_included = kwargs['lower_included'] if 'lower_included' in kwargs else False
            upper_included = kwargs['upper_included'] if 'upper_included' in kwargs else False
        elif len(args) == 3:
            # example: (1, 2, 'close'), (2.3, 4.6, 'open'), (-inf, 1000, 'leftopenrightclose'), (123, 435, 'leftcloserightopen')
            lower = args[0]
            upper = args[1]
            assert isinstance(args[2], str)
            style = args[2].lower()
            if style.lower() == 'open':
                lower_included = False
                upper_included = False
            elif style == 'close':
                lower_included = True
                upper_included = True
            elif style == 'leftopenrightclose':
                lower_included = False
                upper_included = True
            elif style == 'leftcloserightopen':
                lower_included = True
                upper_included = False
        elif len(args) == 4:
            lower_included = args[0]
            lower = args[1]
            upper = args[2]
            upper_included = args[3]

        if isinstance(lower_included, str):
            lower_included = lower_included.strip()
            assert (lower_included == '[' or lower_included == '(')
            lower_included = (lower_included == '[')
        assert isinstance(lower_included, bool)
        if isinstance(upper_included, str):
            upper_included = upper_included.strip()
            assert upper_included == ']' or upper_included == ')'
            upper_included = (upper_included == ']')
        assert isinstance(upper_included, bool)

        def str2num(s):
            assert isinstance(s, str)
            s = s.lower()
            num = None
            # if re.fullmatch(r'([\d\+\-]+)|([\+\-]?0x[\d\+\-abcdef]+)|([\+\-]?0b[01\+\-]+)|([\+\-]?0o[\d\+\-]+)', s):
            if re.fullmatch(int_base10_pattern, s):
                num = int(s)
            elif re.fullmatch(int_base16_pattern, s):
                num = int(s, base=16)
            elif re.fullmatch(int_base8_pattern, s):
                num = int(s, base=8)
            elif re.fullmatch(int_base2_pattern, s):
                num = int(s, base=2)
            elif re.fullmatch(float_pattern, s):
                num = float(s)
            elif re.fullmatch(inf_pattern, s):
                if s == '-inf':
                    num = -inf
                else:
                    num = inf
            else:
                raise SetOperationError(f'{s} is not a number or a interval.')
            return num
        if isinstance(lower, str):
            lower = str2num(lower)
        if isinstance(upper, str):
            upper = str2num(upper)

        assert lower is not None
        assert not isinstance(lower, str)
        assert upper is not None
        assert not isinstance(upper, str)
        assert lower <= upper
        if lower == upper and not isinstance(lower, _Inf):
            assert lower_included
            assert upper_included
        if isinstance(lower, _Inf):
            lower_included = False
            # assert not lower_included, 'inf and -inf cannot be included in a interval'
        if isinstance(upper, _Inf):
            upper_included = False
            # assert not upper_included, 'inf and -inf cannot be included in a interval'
        if isinstance(lower, float) or isinstance(upper, float):
            self.type_ = float
            if type(lower) is int:
                lower = float(lower)
            if type(upper) is int:
                upper = float(upper)
        else:
            self.type_ = int
        self.lower = lower
        self.upper = upper
        self.lower_included = lower_included
        self.upper_included = upper_included

    def __eq__(self, other: str|Self):
        if isinstance(other, str):
            other = Interval(other)
        return self.lower == other.lower and self.upper == other.upper \
                and self.lower_included == other.lower_included \
                and self.upper_included == other.upper_included \
                and self.type_ == other.type_

    def __contains__(self, other:int|float|Self|_Inf) -> bool:
        if type(other) is int or type(other) is float:
            if (self.lower < other < self.upper) \
                    or (self.lower_included and self.lower == other) \
                    or (self.upper_included and self.upper == other):
                        return True
        elif isinstance(other, _Inf):
            if other == self.lower or other == self.upper:
                return True
        else:
            #other is a interval
            if ((other.lower in self) or (not self.lower_included
                                          and not other.lower_included
                                          and self.lower == self.lower)) \
                    and ((other.upper in self) or (not self.upper_included
                                          and not other.upper_included
                                          and self.upper == self.upper)):
                return True
        return False

    def overlap(self, other:Self) -> bool:
        if (other.lower > self.upper) \
                or (other.lower == self.upper
                    and not (other.lower_included and self.upper_included)) \
                or (other.upper < self.lower) \
                or (other.upper == self.lower
                    and not (other.upper_included and self.lower_included)):
            return False
        else:
            return True

    def __lt__(self, other:str|Self) -> bool:
        'if any element in self is less than all elements of other, return True'
        if isinstance(other, str):
            other = Interval(other)
        return (self.lower < other.lower) \
                or (self.lower == other.lower
                    and self.lower_included
                    and not other.lower_included)

    def __gt__(self, other:str|Self) -> bool:
        'if any element in self is greater than all elements of other, return True'
        if isinstance(other, str):
            other = Interval(other)
        return (self.upper > other.upper) \
                or (self.upper == other.upper
                    and self.upper_included
                    and not other.upper_included)

    def mergable(self, other:Self) -> bool:
        if self.overlap(other):
            return True
        if (self.lower == other.upper \
                    and (self.lower_included \
                        or other.upper_included)) \
                or (other.lower == self.upper \
                    and (other.lower_included \
                        or self.upper_included)):
            return True
        return False
    def union(self, other:Self) -> Self:
        # only allowed when union of two intervals can produce one interval object
        assert(self.mergable(other))
        if self.lower < other.lower:
            lower = self.lower
            lower_included = self.lower_included
        elif self.lower > other.lower:
            lower = other.lower
            lower_included = other.lower_included
        else:
            # ==
            if self.lower_included or other.lower_included:
                lower = self.lower
                lower_included = True
            else:
                lower = self.lower
                lower_included = False
        if self.upper > other.upper:
            upper = self.upper
            upper_included = self.upper_included
        elif self.upper < other.upper:
            upper = other.upper
            upper_included = other.upper_included
        else:
            if self.upper_included or other.upper_included:
                upper = self.upper
                upper_included = True
            else:
                upper = self.upper
                upper_included = False
        return Interval(lower_included, lower, upper, upper_included)

    def intersection(self, other:Self) -> Self:
        assert self.overlap(other)
        if self.lower > other.lower:
            lower = self.lower
            lower_included = self.lower_included
        elif self.lower < other.lower:
            lower = other.lower
            lower_included = other.lower_included
        else:
            if self.lower_included and other.lower_included:
                lower = self.lower
                lower_included = True
            else:
                lower = self.lower
                lower_included = False
        if self.upper < other.upper:
            upper = self.upper
            upper_included = self.upper_included
        elif self.upper > other.upper:
            upper = other.upper
            upper_included = other.upper_included
        else:
            if self.upper_included and other.upper_included:
                upper = self.upper
                upper_included = True
            else:
                upper = self.upper
                upper_included = False
        return Interval(lower_included, lower, upper, upper_included)
    def __str__(self):
        left = '[' if self.lower_included else '('
        right = ']' if self.upper_included else ')'
        return f'{left}{self.lower}, {self.upper}{right}'

    def __repr__(self):
        return '<Interval: {}>'.format(str(self))

class NumSet:
    '''
    a set of disjoint intervals
    '''
    def __init__(self, s: Optional[str|Interval|list[Interval]|Self] = None):
        self._intervals = []
        if isinstance(s, str) and len(s) > 0 :
            for item in self._parse(s):
                self.append(item.group())
        elif isinstance(s, Interval):
            self.append(s)
        elif isinstance(s, list):
            for a in s:
                self.append(a)
        elif isinstance(s, NumSet):
            self._intervals = [a for a in s._intervals]

        # if isinstance(s, str) and  not ('=' in s or '<' in s or '>' in s):
            # example: [ 1,4),[-2, 5.5 ] ,234, (12, inf], 12, [3e2, 4e2],12.5,5e2
            # s = s.lower()
            # full_pattern = re.compile(r"([\[\(]\s*([\d\.\+\-abcdefox]+|[\+\-]?inf)\s*,\s*([\d\.\+\-abcdefox]+|[\+\-]?inf)\s*[\]\)])|([\.\d\+\-abcdefox]+)")
            # items = re.finditer(set_item_pattern, s, re.MULTILINE)
            # for item in items:
                # self._intervals.append(Interval(items))
    def _parse(self, s:str):
        s = s.lower()
        assert re.fullmatch(set_full_pattern, s) is not None, f'"{s}" is not a legal format of number set.'
        return re.finditer(set_item_pattern, s)

    def append(self, s: str|Interval):
        if isinstance(s, str):
            s = Interval(s)
        merged = False
        merged_indexes = []
        for i, a in enumerate(self._intervals):
            if s.mergable(a):
                s = s.union(a)
                merged = True
                merged_indexes.append(i)
            elif not merged and s < a:
                self._intervals.insert(i, s)
                return
        if merged:
            self._intervals = [a for i, a in enumerate(self._intervals) if i not in merged_indexes]
            self._intervals.insert(merged_indexes[0], s)
        else:
            self._intervals.append(s)

    def __eq__(self, other:str|Self):
        if isinstance(other, str):
            other = NumSet(other)
        return other._intervals == self._intervals

    def __len__(self):
        return len(self._intervals)

    def __getitem__(self, i):
        return self._intervals[i]

    def union(self, other: str|Interval|Self):
        if not isinstance(other, NumSet):
            other = NumSet(other)
        for a in other:
            self.append(a)
        return self

    def intersection(self, other: str|Interval|Self):
        if not isinstance(other, NumSet):
            other = NumSet(other)
        new_intervals = []
        for a in other:
            for b in self:
                if a.overlap(b):
                    new_intervals.append(b.intersection(a))
        self._intervals = new_intervals
        return self

    def __str__(self):
        s = ''
        first = True
        for a in self:
            if first:
                first = False
            else:
                s += ', '
            s += str(a)
        if s == '':
            s = 'emptySet'
        return s

    def __repr__(self):
        return '<NumSet: {}>'.format(str(self))

    def __bool__(self):
        return bool(self._intervals)

def union(*args : str|Interval|NumSet) -> NumSet:
    res = NumSet()
    for s in args:
        if not isinstance(s, NumSet):
            s = NumSet(s)
        res.union(s)
    return res

def intersection(*args : str|Interval|NumSet) -> NumSet:
    res = NumSet('(-inf, inf)')
    for s in args:
        if not isinstance(s, NumSet):
            s = NumSet(s)
        res.intersection(s)
    return res

