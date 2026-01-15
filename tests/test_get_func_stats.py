import ast

from src.morthal import collect_func_stats


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
