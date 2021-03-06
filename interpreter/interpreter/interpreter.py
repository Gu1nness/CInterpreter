# -*- coding:utf8 -*-
from queue import Queue
from .memory import *
from .number import Number
from ..lexical_analysis.lexer import Lexer
from ..lexical_analysis.token_type import *
from ..syntax_analysis.parser import Parser
from ..syntax_analysis.tree import *
from ..semantic_analysis.analyzer import SemanticAnalyzer
from ..utils.utils import get_functions, MessageColor
from copy import deepcopy
import sys

CQueue = Queue()

def _recurse_name(node, name=""):
    if isinstance(node, Var):
        return node.value
    else:
        return _recurse_name(node.struct_variable, name + "." + node.struct_name)

def bp_wrapper(func):
    def wrapper(self, node):
        if (node.line, node.char) in self.break_points:
            CQueue.put(((node.line, node.char), deepcopy(self.memory)))
            self.can_run.clear()
        self.can_run.wait()
        return func(self, node)
    return wrapper

class Interpreter(NodeVisitor):

    def __init__(self, break_points, event):
        self.memory = Memory()
        self.structs = Structs()
        self.break_points = break_points
        self.can_run = event
        self.can_run.set()

    def load_libraries(self, tree):
        for node in filter(lambda o: isinstance(o, IncludeLibrary), tree.children):
            functions = get_functions('interpreter.__builtins__.{}'.format(
                node.library_name
            ))

            for function in functions:
                self.memory[function.__name__] = function

    def load_functions(self, tree):
        for node in filter(lambda o: isinstance(o, FunctionDecl), tree.children):
            self.memory[node.func_name] = node

    def load_structs(self, tree):
        for node in filter(lambda o: isinstance(o, StructType), tree.children):
            self.structs.create(node)

    @bp_wrapper
    def visit_Program(self, node):
        for var in filter(lambda self: not isinstance(self, (FunctionDecl, StructType, IncludeLibrary)), node.children):
            self.visit(var)

    def visit_VarDecl(self, node):
        self.memory.declare(node.var_node.value)

    @bp_wrapper
    def visit_StructDecl(self, node):
        self.structs.declare(node, self.memory)

    @bp_wrapper
    def visit_FunctionDecl(self, node):
        for i, param in enumerate(node.params):
            self.memory[param.var_node.value] = self.memory.stack.current_frame.current_scope._values.pop(i)
        return self.visit(node.body)

    @bp_wrapper
    def visit_FunctionBody(self, node):
        for child in node.children:
            if isinstance(child, ReturnStmt):
                return self.visit(child)
            self.visit(child)

    def visit_Expression(self, node):
        expr = None
        for child in node.children:
            expr = self.visit(child)
        return expr

    @bp_wrapper
    def visit_FunctionCall(self, node):

        args = [self.visit(arg) for arg in node.args]
        if node.name == 'scanf':
            args.append(self.memory)

        if isinstance(self.memory[node.name], Node):
            self.memory.new_frame(node.name)

            for i, arg in enumerate(args):
                self.memory.declare(i)
                self.memory[i] = arg

            res = self.visit(self.memory[node.name])
            self.memory.del_frame()
            return res
        else:
            return Number(self.memory[node.name].return_type, self.memory[node.name](*args))

    @bp_wrapper
    def visit_UnOp(self, node):
        if node.prefix:
            if node.op.type == AND_OP:
                return node.expr.value
            elif node.op.type == INC_OP :
                self.memory[node.expr.value] += Number(1)
                return self.memory[node.expr.value]
            elif node.op.type == DEC_OP:
                self.memory[node.expr.value] -= Number(1)
                return self.memory[node.expr.value]
            elif node.op.type == SUB_OP:
                return Number(-1) * self.visit(node.expr)
            elif node.op.type == ADD_OP:
                return self.visit(node.expr)
            elif node.op.type == LOG_NEG:
                res = self.visit(node.expr)
                return res._not()
            else:
                res = self.visit(node.expr)
                return Number(res.val)
        else:
            if node.op.type == INC_OP :
                var = self.memory[node.expr.value]
                self.memory[node.expr.value] += Number(1)
                return var
            elif node.op.type == DEC_OP:
                var = self.memory[node.expr.value]
                self.memory[node.expr.value] -= Number(1)
                return var

        return self.visit(node.expr)

    @bp_wrapper
    def visit_CompoundStmt(self, node):
        self.memory.new_scope()

        for child in node.children:
            self.visit(child)

        self.memory.del_scope()

    def visit_ReturnStmt(self, node):
        value = self.visit(node.expression)
        self.can_run.wait()
        if (node.line, node.char) in self.break_points:
            CQueue.put(((node.line, node.char), deepcopy(self.memory)))
            self.can_run.clear()
        elif (node.line, node.char-1) in self.break_points:
            CQueue.put(((node.line, node.char-1), deepcopy(self.memory)))
            self.can_run.clear()
        return value

    @bp_wrapper
    def visit_Num(self, node):
        if node.token.type == INTEGER_CONST:
            return Number(value=node.value)
        elif node.token.type == CHAR_CONST:
            return Number(value=node.value)

    @bp_wrapper
    def visit_Var(self, node):
        return self.memory[node.value]

    def visit_StructVar(self, node):
        if (node.line, node.char) in self.break_points:
            CQueue.put(((node.line, node.char), deepcopy(self.memory)))
            self.can_run.clear()
        elif (node.line, node.char-1) in self.break_points:
            CQueue.put(((node.line, node.char-1), deepcopy(self.memory)))
            self.can_run.clear()
        self.can_run.wait()
        name = _recurse_name(node)
        return self.memory[node.struct_name][name]

    def visit_Assign(self, node):
        sub_name = ""
        if isinstance(node.left, Var):
            var_name = node.left.value
        else:
            var_name = node.left.struct_name
            sub_name = _recurse_name(node.left)
        if sub_name:
            if node.op.type == ADD_ASSIGN:
                self.memory[var_name][sub_name] += self.visit(node.right)
            elif node.op.type == SUB_ASSIGN:
                self.memory[var_name][sub_name] -= self.visit(node.right)
            elif node.op.type == MUL_ASSIGN:
                self.memory[var_name][sub_name] *= self.visit(node.right)
            elif node.op.type == DIV_ASSIGN:
                self.memory[var_name][sub_name] /= self.visit(node.right)
            else:
                self.memory[var_name][sub_name] = self.visit(node.right)
        else:
            if node.op.type == ADD_ASSIGN:
                self.memory[var_name] += self.visit(node.right)
            elif node.op.type == SUB_ASSIGN:
                self.memory[var_name] -= self.visit(node.right)
            elif node.op.type == MUL_ASSIGN:
                self.memory[var_name] *= self.visit(node.right)
            elif node.op.type == DIV_ASSIGN:
                self.memory[var_name] /= self.visit(node.right)
            else:
                self.memory[var_name] = self.visit(node.right)
        if (node.line, node.char) in self.break_points:
            CQueue.put(((node.line, node.char), deepcopy(self.memory)))
            self.can_run.clear()
        self.can_run.wait()
        return self.memory[var_name]

    @bp_wrapper
    def visit_NoOp(self, node):
        pass

    def visit_BinOp(self, node):
        if node.op.type == ADD_OP:
            value = self.visit(node.left) + self.visit(node.right)
        elif node.op.type == SUB_OP:
            value = self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL_OP:
            value = self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV_OP:
            value = self.visit(node.left) / self.visit(node.right)
        elif node.op.type == MOD_OP:
            value = self.visit(node.left) % self.visit(node.right)
        elif node.op.type == LT_OP:
            value = self.visit(node.left) < self.visit(node.right)
        elif node.op.type == GT_OP:
            value = self.visit(node.left) > self.visit(node.right)
        elif node.op.type == LE_OP:
            value = self.visit(node.left) <= self.visit(node.right)
        elif node.op.type == GE_OP:
            value = self.visit(node.left) >= self.visit(node.right)
        elif node.op.type == EQ_OP:
            value = self.visit(node.left) == self.visit(node.right)
        elif node.op.type == NE_OP:
            value = self.visit(node.left) != self.visit(node.right)
        elif node.op.type == LOG_AND_OP:
            value = self.visit(node.left) and self.visit(node.right)
        elif node.op.type == LOG_OR_OP:
            value = self.visit(node.left) or self.visit(node.right)
        elif node.op.type == AND_OP:
            value = self.visit(node.left) & self.visit(node.right)
        elif node.op.type == OR_OP:
            value = self.visit(node.left) | self.visit(node.right)
        elif node.op.type == XOR_OP:
            value = self.visit(node.left) ^ self.visit(node.right)
        if (node.line, node.char) in self.break_points:
            CQueue.put(((node.line, node.char), deepcopy(self.memory)))
            self.can_run.clear()
        self.can_run.wait()
        return value



    @bp_wrapper
    def visit_String(self, node):
        return node.value

    @bp_wrapper
    def visit_IfStmt(self, node):
        if self.visit(node.condition):
            self.visit(node.tbody)
        else:
            self.visit(node.fbody)

    def visit_WhileStmt(self, node):
        self.can_run.wait()
        if self.visit(node.condition):
            if (node.line, node.char) in self.break_points:
                CQueue.put(((node.line, node.char), deepcopy(self.memory)))
                self.can_run.clear()
            elif (node.line, node.char+5) in self.break_points:
                CQueue.put(((node.line, node.char+5), deepcopy(self.memory)))
                self.can_run.clear()
            self.can_run.wait()
            self.visit(node.body)
            if (node.line, node.char) in self.break_points:
                CQueue.put(((node.line, node.char), deepcopy(self.memory)))
                self.can_run.clear()
            elif (node.line, node.char+5) in self.break_points:
                CQueue.put(((node.line, node.char+5), deepcopy(self.memory)))
                self.can_run.clear()
            self.can_run.wait()
            self.visit(node)

    @bp_wrapper
    def visit_ForStmt(self, node):
        self.visit(node.setup)
        while self.visit(node.condition):
            self.visit(node.body)
            self.visit(node.increment)

    def interpret(self, tree):
        self.load_libraries(tree)
        self.load_functions(tree)
        self.load_structs(tree)
        self.visit(tree)
        self.memory.new_frame('main')
        node = self.memory['main']
        res = self.visit(node)
        #self.memory.del_frame()
        return res

    @staticmethod
    def run(program):
        try:
            lexer = Lexer(program)
            parser = Parser(lexer)
            tree = parser.parse()
            SemanticAnalyzer.analyze(tree)
            status = Interpreter().interpret(tree)
        except Exception as message:
            print("{}[{}] {} {}".format(
                MessageColor.FAIL,
                type(message).__name__,
                message,
                MessageColor.ENDC
            ))
            status = -1
        print()
        print(MessageColor.OKBLUE + "Process terminated with status {}".format(status) + MessageColor.ENDC)


