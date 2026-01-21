import ast

from morthal.utils.ast import identify_tab_offset, parentify

def verify_parents(ast_node: ast.AST, parent: ast.AST | None = None):
    if parent is not None:
        assert ast_node.parent is parent
    for child in ast.iter_child_nodes(ast_node):
        verify_parents(ast_node=child, parent=ast_node)

def test_parentify_base():
    ast_mod = ast.parse('''a = 0
def a_func():
    if True:
        return None''')
    
    parentify(ast_mod)

    verify_parents(ast_node=ast_mod)


def test_parentify_elden_focus():
    ast_mod = ast.parse('''
def a_func():
                        
    def b_func():
        if True:
            async def c_func():
                pass
                        
    if True:
        return None
                        
class a_class:
                        
    def d_func():                        
        def e_func():
            pass
        pass
                        
    def f_func():
        pass''')
    
    parentify(ast_mod)

    verify_parents(ast_node=ast_mod)

    a_func = ast_mod.body[0]
    b_func = a_func.body[0]
    b_if = b_func.body[0]
    c_func = b_if.body[0]
    c_pass = c_func.body[0]

    a_if = a_func.body[1]
    a_return = a_if.body[0]

    a_class = ast_mod.body[0]
    d_func = a_class.body[0]
    e_func = d_func.body[0]
    f_func = a_class.body[1]

    assert ast_mod.parent is None
    assert ast_mod.elden is None
    assert ast_mod.depth == 0

    assert a_func.parent is ast_mod
    assert a_func.elden is ast_mod
    assert a_func.depth == 0

    assert b_func.parent is a_func
    assert b_func.elden is a_func
    assert b_func.depth == 1

    assert c_func.parent is b_if
    assert c_func.elden is b_func
    assert c_func.depth == 3

    assert c_pass.parent is c_func
    assert c_pass.elden is c_func
    assert c_pass.depth == 4

    assert a_if.parent is a_func
    assert a_if.elden is a_func
    assert a_if.depth == 1

    assert a_return.parent is a_if
    assert a_return.elden is a_func
    assert a_return.depth == 2

    assert a_class.parent is ast_mod
    assert a_class.elden is ast_mod
    assert a_class.depth == 0

    assert d_func.parent is a_class
    assert d_func.elden is a_class
    assert d_func.depth == 1

    assert e_func.parent is d_func
    assert e_func.elden is d_func
    assert e_func.depth == 2

    assert f_func.parent is a_class
    assert f_func.elden is a_class
    assert f_func.depth == 1


def test_parentify_depth_focus():
    ast_mod = ast.parse('''
def do_stuff() -> None:
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
            print('boh')''')
    
    parentify(ast_node=ast_mod)

    fdef: ast.FunctionDef = ast_mod.body[0]
    assert fdef.depth == 0

    tr: ast.Try = fdef.body[0]
    assert tr.depth == 1

    trpr = tr.body[0]
    assert trpr.parent is tr
    assert trpr.elden is fdef
    assert trpr.depth == 2

    ex1: ast.ExceptHandler = tr.handlers[0]
    assert ex1.depth == 1
    
    ex1_if = ex1.body[0]
    assert ex1_if.parent is ex1
    assert ex1_if.elden is fdef
    assert ex1_if.depth == 2

    ex1_if_if = ex1_if.body[0]
    assert ex1_if_if.parent is ex1_if
    assert ex1_if_if.elden is fdef
    assert ex1_if_if.depth == 3

    ex1_if_if_for = ex1_if_if.body[0]
    assert ex1_if_if_for.parent is ex1_if_if
    assert ex1_if_if_for.elden is fdef
    assert ex1_if_if_for.depth == 4

    ex1_if_if_for_tr = ex1_if_if_for.body[0]
    assert ex1_if_if_for_tr.parent is ex1_if_if_for
    assert ex1_if_if_for_tr.elden is fdef
    assert ex1_if_if_for_tr.depth == 5

    ex1_if_if_for_tr_pr = ex1_if_if_for_tr.body[0]
    assert ex1_if_if_for_tr_pr.parent is ex1_if_if_for_tr
    assert ex1_if_if_for_tr_pr.elden is fdef
    assert ex1_if_if_for_tr_pr.depth == 6

    ex1_if_if_for_ex1 = ex1_if_if_for_tr.handlers[0]
    assert ex1_if_if_for_ex1.parent is ex1_if_if_for_tr
    assert ex1_if_if_for_ex1.elden is fdef
    assert ex1_if_if_for_ex1.depth == 5

    ex1_if_if_for_ex1_if = ex1_if_if_for_ex1.body[0]
    assert ex1_if_if_for_ex1_if.parent is ex1_if_if_for_ex1
    assert ex1_if_if_for_ex1_if.elden is fdef
    assert ex1_if_if_for_ex1_if.depth == 6

    ex1_if_if_for_ex1_if_pass = ex1_if_if_for_ex1_if.body[0]
    assert ex1_if_if_for_ex1_if_pass.parent is ex1_if_if_for_ex1_if
    assert ex1_if_if_for_ex1_if_pass.elden is fdef
    assert ex1_if_if_for_ex1_if_pass.depth == 7

    trelse_if = tr.orelse[0]
    assert trelse_if.parent is tr
    assert trelse_if.elden is fdef
    assert trelse_if.depth == 2

    trelse_if_pr = trelse_if.body[0]
    assert trelse_if_pr.parent is trelse_if
    assert trelse_if_pr.elden is fdef
    assert trelse_if_pr.depth == 3

    trfinal_if = tr.finalbody[0]
    assert trfinal_if.parent is tr
    assert trfinal_if.elden is fdef
    assert trfinal_if.depth == 2

    trfinal_if_pr = trfinal_if.body[0]
    assert trfinal_if_pr.parent is trfinal_if
    assert trfinal_if_pr.elden is fdef
    assert trfinal_if_pr.depth == 3


def test_identify_tab_offset():
    assert identify_tab_offset(ast.parse('''import ast
a = 0
b = 1
c = 2''')) == 0
    
    assert identify_tab_offset(ast.parse('''a = 0
def a():
    pass''')) == 4

    assert identify_tab_offset(ast.parse('''try:
    a = 0
except ValueError:
    a = 0

if True:
    for i in range(18):
        pass
    else:
        pass
elif False:
    pass

def a():
    pass''')) == 4