# -*- coding:utf8 -*-
import sys

class Node(object):
    def __init__(self, line, char):
        self.line = line
        self.char = char


class NoOp(Node):
    pass

class StructType(Node):
    def __init__(self, token, struct_name, struct_body, line, char):
        Node.__init__(self, line, char)
        self.token = token
        self.struct_name = struct_name# A struct name
        self.struct_body = struct_body

class FunctionBody(Node):
    def __init__(self, children, line, char):
        Node.__init__(self, line, char)
        self.children = children

class Num(Node):
    def __init__(self, token, line, char):
        Node.__init__(self, line, char)
        self.token = token
        self.value = token.value


class String(Node):
    def __init__(self, token, line, char):
        Node.__init__(self, line, char)
        self.token = token
        self.value = token.value


class Type(Node):
    def __init__(self, token, line, char):
        Node.__init__(self, line, char)
        self.token = token
        self.value = token.value


class Var(Node):
    def __init__(self, token, line, char):
        Node.__init__(self, line, char)
        self.token = token
        self.value = token.value

class StructVar(Node):
    def __init__(self, token, struct_name, struct_variable, line, char):
        Node.__init__(self, line, char)
        self.token = token
        self.struct_name = struct_name
        self.struct_variable = struct_variable


class BinOp(Node):
    def __init__(self, left, op, right, line, char):
        Node.__init__(self, line, char)
        self.left = left
        self.token = self.op = op
        self.right = right


class UnOp(Node):
    def __init__(self, op, expr, line, char, prefix=True):
        Node.__init__(self, line, char)
        self.token = self.op = op
        self.expr = expr
        self.prefix = prefix


class TerOp(Node):
    def __init__(self, condition, texpression, fexpression, line, char):
        Node.__init__(self, line, char)
        self.condition = condition
        self.texpression = texpression
        self.fexpression = fexpression


class Assign(Node):
    def __init__(self, left, op, right, line, char):
        Node.__init__(self, line, char)
        self.left = left
        self.token = self.op = op
        self.right = right


class Expression(Node):
    def __init__(self, children, line, char):
        Node.__init__(self, line, char)
        self.children = children


class FunctionCall(Node):
    def __init__(self, name, args, line, char):
        Node.__init__(self, line, char)
        self.name = name
        self.args = args            # a list of Param nodes


class IfStmt(Node):
    def __init__(self, condition, tbody, line, char, fbody=None):
        Node.__init__(self, line, char)
        self.condition = condition
        self.tbody = tbody
        self.fbody = fbody


class WhileStmt(Node):
    def __init__(self, condition, body, line, char):
        Node.__init__(self, line, char)
        self.condition = condition
        self.body = body


class DoWhileStmt(WhileStmt):
    pass


class ReturnStmt(Node):
    def __init__(self, expression, line, char):
        Node.__init__(self, line, char)
        self.expression = expression


class BreakStmt(Node):
    pass


class ContinueStmt(Node):
    pass


class ForStmt(Node):
    def __init__(self, setup, condition, increment, body, line, char):
        Node.__init__(self, line, char)
        self.setup = setup
        self.condition = condition
        self.increment = increment
        self.body = body


class CompoundStmt(Node):
    def __init__(self, children, line, char):
        Node.__init__(self, line, char)
        self.children = children

class StructDecl(Node):
    def __init__(self, token, struct_name, struct_type, line, char):
        Node.__init__(self, line, char)
        self.struct_name = struct_name# A struct name
        self.struct_type = struct_type


class VarDecl(Node):
    def __init__(self, var_node, type_node, line, char):
        Node.__init__(self, line, char)
        self.var_node = var_node
        self.type_node = type_node


class IncludeLibrary(Node):
    def __init__(self, library_name, line, char):
        Node.__init__(self, line, char)
        self.library_name = library_name


class Param(Node):
    def __init__(self, type_node, var_node, line, char):
        Node.__init__(self, line, char)
        self.var_node = var_node
        self.type_node = type_node


class FunctionDecl(Node):
    def __init__(self, type_node, func_name, params, body, line, char):
        Node.__init__(self, line, char)
        self.type_node = type_node
        self.func_name = func_name
        self.params = params            # a list of Param nodes
        self.body = body


class FunctionBody(Node):
    def __init__(self, children, line, char):
        Node.__init__(self, line, char)
        self.children = children


class Program(Node):
    def __init__(self, declarations, line, char):
        Node.__init__(self, line, char)
        self.children = declarations


###############################################################################
#                                                                             #
#  AST visitors (walkers)                                                     #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node, dtype=None):
        #sys.stderr.write("%s\n" % self.__dict__)
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

