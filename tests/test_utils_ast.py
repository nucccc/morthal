import ast

from morthal.utils.ast import parentify

def verify_parents(ast_node: ast.AST, parent: ast.AST | None = None):
    if parent is not None:
        assert ast_node.parent is parent
    for child in ast.iter_child_nodes(ast_node):
        verify_parents(ast_node=child, parent=ast_node)

def test_parentify():
    ast_mod = ast.parse('''a = 0
def a_func():
    if True:
        return None''')
    
    parentify(ast_mod)

    verify_parents(ast_node=ast_mod)


def test_parentify_with_elden():
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

    a_if = a_func.body[1]
    a_return = a_if.body[0]

    a_class = ast_mod.body[0]
    d_func = a_class.body[0]
    e_func = d_func.body[0]
    f_func = a_class.body[1]

    assert ast_mod.parent is None
    assert ast_mod.elden is None

    assert a_func.parent is ast_mod
    assert a_func.elden is ast_mod

    assert b_func.parent is a_func
    assert b_func.elden is a_func

    assert c_func.parent is b_if
    assert c_func.elden is b_func

    assert a_if.parent is a_func
    assert a_if.elden is a_func

    assert a_return.parent is a_if
    assert a_return.elden is a_func

    assert a_class.parent is ast_mod
    assert a_class.elden is ast_mod

    assert d_func.parent is a_class
    assert d_func.elden is a_class

    assert e_func.parent is d_func
    assert e_func.elden is d_func

    assert f_func.parent is a_class
    assert f_func.elden is a_class