###############################################################################
#  AST visualizer - generates a DOT file for Graphviz.                        #
#                                                                             #
#  To generate an image from the DOT file run $ dot -Tpng -o ast.png ast.dot  #
#                                                                             #
###############################################################################
import argparse
import textwrap

from interpreter.lexical_analysis.lexer import Lexer
from interpreter.syntax_analysis.parser import Parser
from interpreter.syntax_analysis.tree import NodeVisitor


class ASTVisualizer(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.ncount = 1
        self.dot_header = [textwrap.dedent("""\
        digraph astgraph {
          node [shape=circle, fontsize=12, fontname="Courier", height=.1];
          ranksep=.3;
          edge [arrowsize=.5]

        """)]
        self.dot_body = []
        self.dot_footer = ['}']

    def visit_Program(self, node):
        s = '  node{} [label="Program"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for child in node.children:
            self.visit(child)
            s = '  node{} -> node{}\n'.format(node._num, child._num)
            self.dot_body.append(s)

    def visit_VarDecl(self, node):
        s = '  node{} [label="VarDecl"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.var_node)
        s = '  node{} -> node{}\n'.format(node._num, node.var_node._num)
        self.dot_body.append(s)

        self.visit(node.type_node)
        s = '  node{} -> node{}\n'.format(node._num, node.type_node._num)
        self.dot_body.append(s)

    def visit_FunctionDecl(self, node):
        s = '  node{} [label="FunctionDecl:{}"]\n'.format(
            self.ncount,
            node.func_name
        )
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for param_node in node.params:
            self.visit(param_node)
            s = '  node{} -> node{}\n'.format(node._num, param_node._num)
            self.dot_body.append(s)

        self.visit(node.body)
        s = '  node{} -> node{}\n'.format(node._num, node.body._num)
        self.dot_body.append(s)

    def visit_Body(self, node):
        s = '  node{} [label="Body"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for child in node.children:
            self.visit(child)
            s = '  node{} -> node{}\n'.format(node._num, child._num)
            self.dot_body.append(s)

    def visit_Param(self, node):
        s = '  node{} [label="Param"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for child_node in (node.var_node, node.type_node):
            self.visit(child_node)
            s = '  node{} -> node{}\n'.format(node._num, child_node._num)
            self.dot_body.append(s)


    def visit_Assign(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for child_node in (node.left, node.right):
            self.visit(child_node)
            s = '  node{} -> node{}\n'.format(node._num, child_node._num)
            self.dot_body.append(s)


    def visit_Type(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.token.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_Var(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_Num(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.token.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_BinOp(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.left)
        self.visit(node.right)

        for child_node in (node.left, node.right):
            s = '  node{} -> node{}\n'.format(node._num, child_node._num)
            self.dot_body.append(s)

    def visit_UnaryOp(self, node):
        s = '  node{} [label="unary {}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.expr)
        s = '  node{} -> node{}\n'.format(node._num, node.expr._num)
        self.dot_body.append(s)

    def visit_NoOp(self, node):
        s = '  node{} [label="NoOp"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_IncludeLibrary(self, node):
        s = '  node{} [label="Include:{}"]\n'.format(
            self.ncount,
            node.library_name
        )
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_String(self, node):
        s = '  node{} [label="String:{}"]\n'.format(
            self.ncount,
            node.token.value
        )
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1


    def visit_Block(self, node):
        s = '  node{} [label="Block"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for child in node.children:
            self.visit(child)
            s = '  node{} -> node{}\n'.format(node._num, child._num)
            self.dot_body.append(s)

    def visit_IfStmt(self, node):
        s = '  node{} [label="IfStmt"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.condition_stmt)
        s = '  node{} -> node{} [label="condition"]\n'.format(node._num, node.condition_stmt._num)
        self.dot_body.append(s)

        self.visit(node.if_body)
        s = '  node{} -> node{} [label="IF block"]\n'.format(node._num, node.if_body._num)
        self.dot_body.append(s)

        self.visit(node.else_body)
        s = '  node{} -> node{} [label="ELSE block"]\n'.format(node._num, node.else_body._num)
        self.dot_body.append(s)

    def visit_ReturnStmt(self, node):
        s = '  node{} [label="ReturnStmt"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.expr)
        s = '  node{} -> node{}\n'.format(node._num, node.expr._num)
        self.dot_body.append(s)


    def visit_FunctionCall(self, node):
        s = '  node{} [label="FunctionCall:{}"]\n'.format(
            self.ncount,
            node.func_name
        )
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for i, param_node in enumerate(node.params):
            self.visit(param_node)
            s = '  node{} -> node{} [label="Param{:02d}"]\n'.format(node._num, param_node._num, i)
            self.dot_body.append(s)


    def gendot(self):
        tree = self.parser.parse()
        self.visit(tree)
        return ''.join(self.dot_header + self.dot_body + self.dot_footer)



def main():
    argparser = argparse.ArgumentParser(
        description='Generate an AST DOT file.'
    )
    argparser.add_argument(
        'fname',
        help='Pascal source file'
    )
    args = argparser.parse_args()
    fname = args.fname
    text = open(fname, 'r').read()

    lexer = Lexer(text)
    parser = Parser(lexer)
    viz = ASTVisualizer(parser)
    content = viz.gendot()
    print(content)


if __name__ == '__main__':
    main()