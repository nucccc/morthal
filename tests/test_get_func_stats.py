import ast

from src.morthal import collect_func_stats, calc_func_depth


def test_calc_func_depth():
    func_ast = ast.parse('''def func_pass():
    pass
    ''').body[0]
    assert calc_func_depth(func_ast) == 0

    func_ast = ast.parse('''def simple_func():
    if True:
        pass
    ''').body[0]
    assert calc_func_depth(func_ast) == 1

    func_ast = ast.parse('''def simple_func():
    if True:
        pass
    else:
        for j in range(9):
            pass
    ''').body[0]
    assert calc_func_depth(func_ast) == 2

    func_ast = ast.parse('''def simple_func():
    if True:
        pass
    else:
        for j in range(9):
            try:
                pass
            except:
                pass
            else:
                pass
            finally:
                pass
    ''').body[0]
    assert calc_func_depth(func_ast) == 3

    func_ast = ast.parse('''def simple_func():
    if True:
        pass
    else:
        for j in range(9):
            try:
                if True:
                    pass
            except:
                pass
            else:
                pass
            finally:
                pass
    ''').body[0]
    assert calc_func_depth(func_ast) == 4

    func_ast = ast.parse('''def simple_func():
    if True:
        pass
    else:
        for j in range(9):
            try:
                pass
            except:
                if True:
                    pass
            else:
                pass
            finally:
                pass
    ''').body[0]
    assert calc_func_depth(func_ast) == 4

    func_ast = ast.parse('''def simple_func():
    if True:
        pass
    else:
        for j in range(9):
            try:
                pass
            except:
                pass
            else:
                if True:
                    pass
            finally:
                pass
    ''').body[0]
    assert calc_func_depth(func_ast) == 4

    func_ast = ast.parse('''def simple_func():
    if True:
        pass
    else:
        for j in range(9):
            try:
                pass
            except:
                pass
            else:
                pass
            finally:
                if True:
                    pass
    ''').body[0]
    assert calc_func_depth(func_ast) == 4

    func_ast = ast.parse('''def simple_func():
    if True:
        pass
    else:
        for j in range(9):
            try:
                pass
            except:
                pass
            else:
                pass
            finally:
                pass
        else:
            if True:
                if True:
                    if True:
                        pass
    ''').body[0]
    assert calc_func_depth(func_ast) == 5


def test_collect_func_stats():
    f_ast = ast.parse('''def eventually_print_hello_world(i: int, j) -> None:
    if i > 0:
        print('hello')
        if j > 0:
            print(' world')
    ''').body[0]

    f_stats = collect_func_stats(f_ast)

    assert f_stats.name == 'eventually_print_hello_world'
    assert f_stats.max_depth == 2
    assert f_stats.n_codelines == 4
    assert f_stats.n_func_args == 2
    assert f_stats.n_func_args_annotated == 1
    assert f_stats.return_annotated == True


    f_ast = ast.parse('''def do_stuff() -> None:
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
    ''').body[0]

    f_stats = collect_func_stats(f_ast)

    assert f_stats.name == 'do_stuff'
    assert f_stats.max_depth == 6
    assert f_stats.n_codelines == 17
    assert f_stats.n_func_args == 0
    assert f_stats.n_func_args_annotated == 0
    assert f_stats.return_annotated == True