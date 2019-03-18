# -*- coding:utf8 -*-
from ctypes import c_int
import random
from ..syntax_analysis.tree import StructDecl, VarDecl, Type

class Scope(object):
    def __init__(self, scope_name, parent_scope=None):
        self.scope_name = scope_name
        self.parent_scope = parent_scope
        self._values = dict()

    def __setitem__(self, key, value):
        self._values[key] = value

    def __getitem__(self, item):
        return self._values[item]

    def __contains__(self, key):
        return key in self._values

    def keys(self):
        return self._values.keys()

    def __repr__(self):
        lines = [
            '{}:{}'.format(key, val) for key, val in self._values.items()
        ]
        title = '{}\n'.format(self.scope_name)
        return title + '\n'.join(lines)


class Frame(object):
    def __init__(self, frame_name, global_scope):
        self.frame_name = frame_name
        self.current_scope = Scope(
            '{}.scope_00'.format(frame_name),
            global_scope
        )
        self.scopes = [self.current_scope]

    def new_scope(self):
        self.current_scope = Scope(
            '{}{:02d}'.format(
                self.current_scope.scope_name[:-2],
                int(self.current_scope.scope_name[-2:]) + 1
            ),
            self.current_scope
        )
        self.scopes.append(self.current_scope)

    def del_scope(self):
        current_scope = self.current_scope
        self.current_scope = current_scope.parent_scope
        self.scopes.pop(-1)
        del current_scope

    def __contains__(self, key):
        return key in self.current_scope

    def __repr__(self):
        lines = [
            '{}\n{}'.format(
                scope,
                '-' * 40
            ) for scope in self.scopes
        ]

        title = 'Frame: {}\n{}\n'.format(
            self.frame_name,
            '*' * 40
        )

        return title + '\n'.join(lines)


class Stack(object):
    def __init__(self):
        self.frames = list()
        self.current_frame = None

    def __bool__(self):
        return bool(self.frames)

    def new_frame(self, frame_name, global_scope=None):
        frame = Frame(frame_name, global_scope=global_scope)
        self.frames.append(frame)
        self.current_frame = frame

    def del_frame(self):
        self.frames.pop(-1)
        self.current_frame = len(self.frames) and self.frames[-1] or None

    def __repr__(self):
        lines = [
            '{}'.format(frame) for frame in self.frames
        ]
        return '\n'.join(lines)


class Structs(object):
    def __init__(self):
        self._structs = {}

    def create(self, struct):
        _name = struct.struct_name
        body = {}
        for variable in struct.struct_body:
            if isinstance(variable, VarDecl):
                body[_name + "." + variable.var_node.value] = variable
            elif isinstance(variable, StructDecl):
                struct = self.__getitem__(struct.struct_type)
                body[_name + "." + variable.struct_name] = struct
        self._structs[_name] = body


    def declare(self, struct, memory, name=""):
        struct_found = self.__getitem__(struct.struct_type)
        if struct_found:
            res = {}
            for (name, type) in struct_found.items():
                if isinstance(type, VarDecl):
                    res[type.var_node.value] = 0
                else:
                    raise TypeError("Type %s unknown" % type(i))
            memory.declare(struct.struct_name, value=res)

    def __getitem__(self, variable):
        return self._structs.get(variable, None)

class Memory(object):
    def __init__(self):
        self.global_frame = Frame('GLOBAL_MEMORY', None)
        self.stack = Stack()

    def declare(self, key, value=0):
        ins_scope = self.stack.current_frame.current_scope if self.stack.current_frame else self.global_frame.current_scope
        ins_scope[key] = value

    def __setitem__(self, key, value):
        splitted = []
        if '.' in key:
            splitted = key.split(".")
            key = splitted[0]
        ins_scope = self.stack.current_frame.current_scope if self.stack.current_frame else self.global_frame.current_scope
        curr_scope = ins_scope
        while curr_scope and key not in curr_scope:
            curr_scope = curr_scope.parent_scope
        ins_scope = curr_scope if curr_scope else ins_scope
        if splitted:
            ins_scope[key][splitted[1]] = value
        else:
            ins_scope[key] = value

    def __getitem__(self, item):
        curr_scope = self.stack.current_frame.current_scope if self.stack.current_frame else self.global_frame.current_scope
        while curr_scope and item not in curr_scope:
            curr_scope = curr_scope.parent_scope
        return curr_scope[item]

    def keys(self):
        res = []
        curr_scope = self.stack.current_frame.current_scope if self.stack.current_frame else self.global_frame.current_scope
        while curr_scope:
            res += curr_scope.keys()
            curr_scope = curr_scope.parent_scope
        return res

    def new_frame(self, frame_name):
        self.stack.new_frame(frame_name, self.global_frame.current_scope)

    def del_frame(self):
        self.stack.del_frame()

    def new_scope(self):
        self.stack.current_frame.new_scope()

    def del_scope(self):
        self.stack.current_frame.del_scope()

    def __repr__(self):
        return "{}\nStack\n{}\n{}".format(
            self.global_frame,
            '=' * 40,
            self.stack
        )

    def __str__(self):
        return self.__repr__()


