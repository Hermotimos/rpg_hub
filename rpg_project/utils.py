from django.db import connection, reset_queries
import time
import functools


def create_sorting_name(obj):
    name = str(obj).lower()
    name = name.replace('a', 'aa')
    name = name.replace('ą', 'aą')
    name = name.replace('c', 'cc')
    name = name.replace('ć', 'cć')
    name = name.replace('e', 'ee')
    name = name.replace('ę', 'eę')
    name = name.replace('l', 'll')
    name = name.replace('ł', 'lł')
    name = name.replace('n', 'nn')
    name = name.replace('ń', 'nń')
    name = name.replace('o', 'oo')
    name = name.replace('ó', 'oó')
    name = name.replace('s', 'ss')
    name = name.replace('ś', 'sś')
    name = name.replace('z', 'zz')
    name = name.replace('ż', 'zż')
    name = name.replace('ź', 'zź')
    return name


# def create_sorting_name(obj):
#     name = str(obj)
#     name = name.replace('Ą', 'Azz')
#     name = name.replace('ą', 'azz')
#     name = name.replace('Ć', 'Czz')
#     name = name.replace('ć', 'czz')
#     name = name.replace('Ę', 'Ezz')
#     name = name.replace('ę', 'ezz')
#     name = name.replace('Ł', 'Lzz')
#     name = name.replace('ł', 'lzz')
#     name = name.replace('Ó', 'Ozz')
#     name = name.replace('ó', 'ozz')
#     name = name.replace('Ń', 'Nzz')
#     name = name.replace('ń', 'nzz')
#     name = name.replace('Ś', 'Szz')
#     name = name.replace('ś', 'szz')
#     name = name.replace('Ż', 'Zzz')
#     name = name.replace('ż', 'zzz')
#     name = name.replace('Ź', 'Zzz')
#     name = name.replace('ź', 'zzz')
#     return name


def query_debugger(func):
    """
    Source of query_debugger: https://medium.com/@goutomroy/django-select-related-and-prefetch-related-f23043fd635d
    """
    @functools.wraps(func)
    def inner_func(*args, **kwargs):

        reset_queries()
        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result

    return inner_func
