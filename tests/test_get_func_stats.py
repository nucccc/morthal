import ast

from src.morthal import collect_func_stats, calc_func_depth


def test_calc_func_depth():
    func_ast = ast.parse('''def func_pass(i: int, j) -> None:
    pass
    ''').body[0]

    assert calc_func_depth(func_ast) == 0

    func_ast = ast.parse('''def simple_func(i: int, j) -> None:
    if True:
        pass
    ''').body[0]

    assert calc_func_depth(func_ast) == 1


def test_collect_func_stats():
    f_mod = ast.parse('''def eventually_print_hello_world(i: int, j) -> None:
    if i > 0:
        print('hello')
        if j > 0:
            print(' world')
''')
    
    f_ast = f_mod.body[0]

    f_stats = collect_func_stats(f_ast)

    assert f_stats.name == 'eventually_print_hello_world'
    assert f_stats.max_depth == 2
    assert f_stats.n_codelines == 4
    assert f_stats.n_func_args == 2
    assert f_stats.n_func_args_annotated == 1
    assert f_stats.return_annotated == True


    f_mod = ast.parse('''def do_stuff() -> None:
    try:
        print('hello')
    except ValueError:
        if True:
            if not False:
                for i in range(10):
                    try:
                        print(i)
                    except TypeError:
                        if True:
                            pass
    else:
        if 1 > 0:
            print(' world')
    finally:
        if not False:
            print('boh')
''')
    
    f_ast = f_mod.body[0]

    f_stats = collect_func_stats(f_ast)

    assert f_stats.name == 'do_stuff'
    assert f_stats.max_depth == 6
    assert f_stats.n_codelines == 17
    assert f_stats.n_func_args == 0
    assert f_stats.n_func_args_annotated == 0
    assert f_stats.return_annotated == True