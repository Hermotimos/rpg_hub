# sandbox.py

def mygen():
    yield 1
    yield 2


# print(next(mygen()))
# print(mygen())

for x in mygen():
    print(x)


mygen2 = (x*x for x in range(1, 10))

for x in mygen2:
    print(x)

print('fff'.split(','))


class ParentCls:
    pass

    def __str__(self):
        return 'LOL'


class Test(ParentCls):
    classattr = 123

    def __init__(self):
        self.attr1 = 1
        self._attr2 = 2
        self.__attr3 = 3


t = Test()
print(dir(t))
print(t.__dict__)
print(t.__eq__(1))
print(t.__str__())

print(t.classattr)
print(Test.classattr)

Test.classattr = 321
print(t.classattr)
print(Test.classattr)

t.classattr = 111
print(t.classattr)
print(Test.classattr)

print(help(t))
print(help(Test))


# -----------

print(repr(t))
print(str(t))

import manage
print(manage.__name__)  # imported module __name__ is set to the modules' name
print(__name__)         # this module's __name__ is always '__main__'


class Employee:
    raise_rate = None

    def __init__(self, salary, firstname=None, lastname=None):
        self.salary = salary
        self.firstname = firstname
        self.lastname = lastname

    @property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"

    @fullname.setter
    def fullname(self, fullname):
        self.firstname, self.lastname = fullname.split(" ")

    @staticmethod
    def greeting():
        return "Dear Mrs/Ms"

    @classmethod
    def upd_raise_rate(cls, growth_factor: float):
        cls.raise_rate += cls.raise_rate * growth_factor

    def raise_salary(self):
        self.salary += self.salary * self.raise_rate


class Developer(Employee):
    raise_rate = 0.15

    @staticmethod
    def greeting():
        return "Hi"


class OfficeClerk(Employee):
    raise_rate = 0.1

    @staticmethod
    def greeting():
        return "Cheers"


emp1 = Developer(10000, "Billy", "Kid")
emp2 = OfficeClerk(8000, "Don", "Draper")
print(help(Developer))



Developer.upd_raise_rate(1)
emp2.upd_raise_rate(1)
emp1.raise_salary()
emp2.raise_salary()
print(emp1.salary)
print(emp2.salary)

print(emp1.fullname)
print(emp2.fullname)

emp3 = OfficeClerk(8000)
print(emp3.firstname, emp3.lastname, emp3.fullname)
emp3.fullname = "Joe Dakota"
print(emp3.firstname, emp3.lastname, emp3.fullname)


class Ninja(Developer, OfficeClerk):
    pass


print(
    """
    In Python, the MRO is from bottom to top and left to right.
    This means that, first, the method is searched in the class of the object.
    If it’s not found, it is searched in the immediate super class.
    In the case of multiple super classes, it is searched left to right, in the order by which was declared by the developer.
    For example:
    def class C(B, A)
    In this case, the MRO would be C -> B -> A.
"""
)
print(help(Ninja))


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


# lambda

func = lambda a, b: f"{a} / {b}"
print(func(1, 2))



#  map
alist1 = ['aa', 'bb', 'cc']
print(list(map(str.upper, alist1)))
print(list(map(str.title, alist1)))
print(list(map(str.capitalize, alist1)))

alist2 = [1.2, 2.5, 3.6]
print(list(map(round, alist2)))


zipped = list(map(lambda a, b: (a, b), alist1, alist2))
print(zipped)


def myzip(a, b):
    return a, b


zipped = list(map(myzip, alist1, alist2))
print(zipped)


# filter

dromes = ("demigod", "rewire", "madam", "freer", "anutforajaroftuna", "kiosk")
print(list(filter(lambda a: a == a[::-1], dromes)))


# reduce

from functools import reduce


def mysum(a, b):
    return a + b


numbers = [3, 4, 6, 9, 34, 12]
print(reduce(mysum, numbers))


def anytrue(a, b) -> bool:
    return bool(a or b)


def alltrue(a, b) -> bool:
    return bool(a and b)


vals = [0, 0, 0, 1, 1, 0]

print(reduce(anytrue, vals))
print(reduce(alltrue, vals))

print(reduce(lambda a, b: bool(a or b), vals))
print(reduce(lambda a, b: bool(a and b), vals))



# closure

def enclosing_func(msg):
    def nested_func():
        return msg + ' nested'
    return nested_func

afunc = enclosing_func('Hello')
print(afunc)
print(afunc())
func1 = enclosing_func('1')
func2 = enclosing_func('2')
func3 = enclosing_func('3')
func4 = enclosing_func('4')

print(func4())


# decorator

def enclosing_func(func):
    def nested_func(arg):
        res = func(arg)
        return res + ' decorated'
    return nested_func


def get_name(name: str):
    return name.title()


print(enclosing_func(get_name)('Bill'))


@enclosing_func
def get_name(name: str):
    return name.title()


print(get_name('Bill'))


#  =============================


def decorator_with_params(addition):
    def inner(func):
        def wrapper(arg):
            res = func(arg)
            return res + addition
        return wrapper

    return inner


def get_name(name: str):
    return name.title()


print(decorator_with_params('add')(get_name)('bill'))


@decorator_with_params('the addition')
def get_name(name: str):
    return name.title()


print(get_name('bill'))


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


#  Context manager

class Manager:

    def __init__(self):
        print('initialized')

    def __enter__(self):
        print('entered')

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('exited')


with Manager() as m:
    print('here')


#  --------------------------


class FileManager:

    def __init__(self, filename, mode='r'):
        self.filename = filename
        if mode == 'w':
            raise Exception('Truncating file on open is not allowed')
        self.mode = mode
        self.file = None
        print('initialized')

    def __enter__(self):
        print('entered')
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        print('exited')


with FileManager('sandbox.py', 'r') as fm:
    print('here')
    print(fm.readline(100), 'inside context manager call')

iterator = iter([1, 2, 3, 4, 5])
print(next(iterator))
print(next(iterator))
print(next(iterator))
print(next(iterator))
print(next(iterator))

print()

generator = (x for x in [1, 2, 3, 4, 5])
print(next(generator))
print(next(generator))
print(next(generator))
print(next(generator))
print(next(generator))

iterator = iter([1, 2, 3, 4, 5])
generator = (x for x in [1, 2, 3, 4, 5])

for v in iterator:
    print(v)

for v in generator:
    print(v)

print()


class MyIterator:

    def __init__(self, iterable):
        self.iter_obj = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iter_obj)


myiterator = MyIterator([1, 2, 3])  # myiterator = iter([1, 2, 3])
for i in myiterator:
    print(i)

print()


class MyGenerator:

    def __init__(self, iterable):
        self.iterable = iterable

    def __iter__(self):
        for x in self.iterable:
            yield x


mygen = MyGenerator([1, 2, 3])  # mygen = (x for x in [1, 2, 3])
print(mygen)

for i in mygen:
    print(i)




#  --------------------------



