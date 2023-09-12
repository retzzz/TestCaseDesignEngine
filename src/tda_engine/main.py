from _ast import AST
import argparse
import logging
import ast
import copy
import enum
from typing import Optional, Literal

from .util import dump

# from .testcase import generate_test_case
testcaseset = []
# bool_conditions = []
class TestCaseGenerationError(Exception):
    pass

class PrameterConflictError(Exception):
    pass

class FormatError(Exception):
    pass

class SetStatus(enum.Enum):
    FREETOSET = 'free_to_set' #可以自由的设置某个节点的值
    RESTRICTED = 'restricted' #可以设置节点的值, 但是受到已经取值的变量的限制, 一旦变量变化, 这个取值也会变化
    NEGATIVE = 'negative'     #由于收到已经取值的变量的限制, 无法设置成预定的值.

SetStatusType = Literal[SetStatus.FREETOSET, SetStatus.RESTRICTED, SetStatus.NEGATIVE]

def isAncestor(node_ancestor:ast.AST, node:ast.AST) -> bool:
    tmp_node = node
    while tmp_node is not None:
        tmp_node = tmp_node.parent
        if tmp_node is node_ancestor:
            return True
    return False

class Parameter:
    #代表伪代码里能直接赋值的变量
    parameter_pool = []
    def __init__(self, node: ast.Name, type_:type):
        self.name = node.id
        self.ast_nodes = []
        self.ast_nodes.append(node)
        self.type_ = type_

    def append(self, node: ast.Name):
        self.ast_nodes.append(node)

    def __in__(self, node):
        return (node in self.ast_nodes)

    @classmethod
    def create(cls, node: ast.Name, type_:type):
        obj = None
        for param in cls.parameter_pool:
            if param.name == node.id:
                param.append(node)
                obj = param
                break
        if obj is None:
            obj = Parameter(node, type_)
            cls.parameter_pool.append(obj)
        return obj

class ValueAssignement(dict):
    # key: value
    # for bool, value is True or False
    # for string, value is a set type include all valid string
    # for int/float, value is a pair of [ops, comparators],
    #   ops is the list of operators, element can be '==', '>', '>=', '<', '<='
    #   comparators is a list of values
    def __or__(self, other):
        res = ValueAssignement()
        for p in other:
            assert isinstance(p, Parameter)
            if p in self:
                if p.type_ is bool:
                    if self[p] != other[p]:
                        raise PrameterConflictError()
                    else:
                        res[p] = other[p]
                elif p.type_ is str:
                    res[p] = self[p] | other[p]
                elif p.type is int or p.type is float:
                    if self[p]:
                        pass #####################
            else:
                res[p] = other[p]
        return res

class Output:
    #代表伪代码里每个if分支输出, 形式上必须是有一个输入参数的OUTPUT(value)函数调用
    #相同的value即便在不同的分支里也要算不同的输出
    output_pool = []
    def __init__(self, node: ast.Assert):
        assert isinstance(node.test, ast.Constant)
        self.value = node.test.value
        self.ast_nodes = []
        self.ast_nodes.append(node)

    def append(self, node: ast.Name):
        self.ast_nodes.append(node)

    def __in__(self, node):
        return (node in self.ast_nodes)

    @classmethod
    def create(cls, node: ast.Assert):
        assert isinstance(node.test, ast.Constant)
        obj = None
        for output in cls.output_pool:
            if output.value == node.test.value:
                output.append(node)
                obj = output
                break
        if obj is None:
            obj = Output(node)
            cls.output_pool.append(obj)
        return obj

class TestCase(dict):
    test_case_pool = []
    # key is parameter, value is the value of parameter
    def __init__(self, root):
        super().__init__()
        self.root = root
        # self.parameter_values = {} #parameter: value
        self.node_values = {} #node: value
        self.output = None #node

    def __getitem__(self, key):
        assert isinstance(key, Parameter)
        return super()[key]

    def __setitem__(self, key, value):
        assert isinstance(key, Parameter)
        assert type(value) == value.type_
        super()[key] = value

    def __eq__(self, tc):
        assert self.output == tc.output
        assert self.node_values == tc.node_values
        return super().__eq__(tc)

    def setNode(self, node, value):
        assert isinstance(node, ast.AST)
        self.node_values[node] = value

    def getNode(self, node):
        return self.node_values[node]

    def setOutput(self, output):
        self.output = output

    def getOutput(self, output):
        return self.output

    def addTestCase(self, tc):
        for existed_tc in self.test_case_pool:
            if tc == existed_tc:
                return False
        self.test_case_pool.append(tc)
        return True

class BoolHandlerVisitor(ast.NodeVisitor):
    def __init__(self, tc_generator, expected_value):
        self.gen = tc_generator
        self.expected_value = expected_value

class TestCaseGenerator:
    def __init__(self, node:ast.AST, param:Parameter, truth_values:list):
        self.target_node = node
        self.target_param = param
        self.target_truth_values = truth_values
        self.stack = []
        # assert len(target_node.rel_parameters)==1
        # self.pmap = {} #param_values_map
        # self.nmap = {} #node_values_map
        # self.true_nmap = {} #node_values_map
        # self.false_nmap = {} #node_values_map
        # self.true_output = None
        # self.true_output_node = None
        # self.false_output = None
        # self.false_output_node = None
    def red(self, node:ast.AST, fixed_params:list):
        if node is self.target_node:
            node.color = 'red'
            status, params = self.red(node.parent, fixed_params)
            if status:
                return status, params
            raise TestCaseGenerationError("Cannot find a pair of test cases for condition {}.".format(node))
        elif isinstance(node, ast.BoolOp):
            def force_child(child, siblings, boolv, fixed_params):
                params = self.force_value(child, boolv, fixed_params)
                for p in params:
                    if siblings == []:
                        yield p
                    else:
                        for p2 in force_child(siblings[0], siblings[1:], boolv, fixed_params + p):
                            yield fixed_params + p + p2

            v = True if isinstance(node.op, ast.And) else False
            nodes_need_force = [child for child in node.values if child.color != 'red']
            for params in force_child(nodes_need_force[0], nodes_need_force[1:], v, fixed_params):
                status, params = self.red(node.parent, fixed_params + params)
                if status:
                    return status, params
            raise TestCaseGenerationError("Cannot find a pair of test cases for condition {}.".format(node))

    def force_value(self, node, boolv, fixed_params):
        if node.forced_value_param[boolv]:
            pass


    # def set_bool_parameter(self, param:Parameter, value:Optional[bool], rehearsal:bool = False):
        # assert param.type_ is bool
        # if (param not in self.pmap) and (not rehearsal):
            # self.pmap[param] = value
            # for n in param.ast_nodes:
                # if n not in self.nmap:
                    # self.nmap[n] = value

    # def set_bool_operand(self, node:ast.AST, true_value:Optional[bool], rehearsal:bool = False) -> SetStatusType:
        # # node是语法树里某个布尔表达式的操作数
        # # true_value是target_node为true时当前节点的真值
        # # rehearsal 意味着想要尝试写值, 但不会把真实的值写到pmap和nmap里
        # assert node not in self.nmap
        # if isinstance(node, ast.Name):
            # assert len(node.rel_parameters) == 1
            # param = node.rel_parameters[0]
            # if param is self.target_param:
                # assert param not in self.pmap
                # if true_value == True:
                    # return SetStatus.FREETOSET
                # else:
                    # if rehearsal:
                        # return SetStatus.NEGATIVE
                    # else:
                        # raise ParamValueConflict(f'Parameter {param.name} conflict: target node {node}')
            # else:
                # if param in self.pmap:
                    # if self.pmap[param] == true_value:
                        # return SetStatus.FREETOSET
                    # else:
                        # if rehearsal:
                            # return SetStatus.NEGATIVE
                        # else:
                            # raise
                # assert param not in self.pmap
                # self.set_bool_parameter(param, value, rehearsal)
                # return True
        # if isinstance(node, ast.UnaryOp):
            # assert isinstance(node.op, ast.Not)
            # if not rehearsal:
                # self.nmap[node] = value
            # if value is not None:
                # return self.set_bool_operand(node.operand, target_param, not value, rehearsal)
            # else:
                # return self.set_bool_operand(node.operand, target_param, None, rehearsal)
        # if isinstance(node, ast.BoolOp):
            # if value is None:
                # if not rehearsal:
                    # self.nmap[node] = value
                    # for child in node.values:
                        # self.set_bool_operand(child, target_param, None)
                # return True

            # def set_and_or(andor):
                # if andor == 'and':
                    # T = True
                # else:
                    # T = False
                # if value == T:
                    # res = True
                    # for child in node.values:
                        # tmp_res = self.set_bool_operand(child, target_param, True, rehearsal)
                        # if tmp_res is None:
                            # return None
                        # res = res and tmp_res
                    # if not rehearsal:
                        # self.nmap[node] = value
                    # return res
                # else:
                    # if target_param not in node.rel_parameters:
                        # if rehearsal:
                            # return True
                        # res = self.set_bool_operand(node.values[0], target_param, (not T))
                        # for child in node.values[1:]:
                            # res = res and self.set_bool_operand(child, target_param, None)
                        # self.nmap[node] = value
                        # return res
                    # else:
                        # find = None
                        # valid = None
                        # for i, child in enumerate(node.values):
                            # if target_param not in child.rel_parameters:
                                # #找到至少1个and操作数与被测parameter无关
                                # valid = i
                                # find = i
                                # break
                        # if find is None:
                            # #所有and操作数与被测parameter有关
                            # for i, child in enumerate(node.values):
                                # res = self.set_bool_operand(child, target_param, (not T), rehearsal=True):
                                    # if res is not None and valid is None:
                                        # valid = i
                                # if res:
                                    # find = i
                                    # break
                        # if find is not None:
                            # if rehearsal:
                                # return True
                            # self.nmap[node] = value
                            # for i, child in enumerate(node.values):
                                # if i == find:
                                    # self.set_bool_operand(child, target_param, (not T))
                                # else:
                                    # self.set_bool_operand(child, target_param, None)
                        # else:
                            # if rehearsal:
                                # if valid is not None:
                                    # return False
                                # else:
                                    # return None
                            # if valid is None:
                                # raise
                            # else:
                                # self.nmap[node] = value
                                # for i, child in enumerate(node.values):
                                    # if i == valid:
                                        # self.set_bool_operand(child, target_param, (not T))
                                    # else:
                                        # self.set_bool_operand(child, target_param, None)
                                # return False

            # if isinstance(node.op, ast.And):
                # set_and_or('and')

            # elif isinstance(node.op, ast.Or):
                # set_and_or('or')


    # def set_if_statement(self, node, param, value):
        # assert(type(value) is bool)
        # if node in bool_conditions:
            # assert len(node.rel_parameters) == 1
            # param = node.rel_parameters[0]
            # if param not in self.pmap:
                # self.pmap[param] = value
            # for n in param.ast_nodes:
                # self.nmap[n] = value
            # self.pmap[param]

    # def set_node(self, node:ast.AST, value:Optional[bool], child_node:Optional[ast.AST]=None):
        # if node is None:
            # return
        # if isinstance(node, ast.Name):
            # assert len(node.rel_parameters) == 1
            # param = node.rel_parameters[0]
            # assert param is target_param
            # self.set_bool_parameter(target_param, value)
            # self.set_node(node.parent, target_param, value, node)
        # if isinstance(node, ast.UnaryOp):
            # assert isinstance(node.op, ast.Not)
            # if value is None:
                # not_value = None
            # else:
                # not_value = not value
            # self.nmap[node] = not_value
            # self.set_node(node.parent, target_param, not_value, node)
        # if isinstance(node, ast.BoolOp):
            # self.nmap[node] = value
            # if isinstance(node.op, ast.And):
                # for v in node.values:
                    # self.set_bool_operand(v, target_param, True)
            # elif isinstance(node.op, ast.Or):
                # for v in node.values:
                    # self.set_bool_operand(v, target_param, False)
            # self.set_node(node.parent, target_param, value, node)
        # if isinstance(node, ast.If):
            # if node.test is child_node:
                # #从if的test成员追溯来的, 需要搞清楚每个路径
                # self.set_if_statement(node, target_param, value)
            # if child_node in node.body:
                # #从true path追溯来的
                # res = self.set_bool_operand(node.test, target_param, True)
                # assert res is not None
            # if child_node in node.orelse:
                # #从true path追溯来的
                # res = self.set_bool_operand(node.test, target_param, False)
                # assert res is not None
            # self.set_node(node.parent, target_param, value, node)
            # for ot in node.true_path_output:
                # for of in node.true_path_output:
                    # if ot is not of:
                        # self.set_if_path(node.body, ot, target_param, value, rehearsal = True)
                        # self.set_if_path(node.orelse, of, target_param, value, rehearsal = True)
            # pass


    # def generate_test_cases_for_condition(self, node:ast.AST):
        # assert len(node.rel_parameters) == 1
        # param = node.rel_parameters[0]
        # self.set_node(node, param, True)
        # self.set_node(node, param, False)
        # return [*true_cases, *false_cases]

class InitializationVisitor(ast.NodeVisitor):
    def __init__(self, root):
        super().__init__()
        self.root = root
        for node in ast.walk(self.root):
            #add labels
            node.output=None
            node.isCondition=False
            node.rel_params=[]
            node.true_path_output=[]
            node.false_path_output=[]
            node.color=''
            for child in ast.iter_child_nodes(node):
                child.parent = node
        self.root.parent = None
        self.root.conditions = []

    def visit_Assert(self, node):
        # format: assert "messages"
        #每个if语句node都有两个list类型attribute, true_path_output, false_path_output
        #里面是真假路径上所有可能产生的output
        #多个path可能是同一个output
        #根节点里包括所有可能的output
        self.generic_visit(node)
        assert isinstance(node.test, ast.Constant)
        assert isinstance(node.test.value, str)
        assert isinstance(node.parent, ast.If)
        assert len(node.parent.body) == 1
        assert len(node.parent.orelse) == 1
        node.output = the_output = Output.create(node)

        iter_node = node
        while iter_node is not None:
            if isinstance(iter_node.parent, ast.If):
                if iter_node in iter_node.parent.body:
                    iter_node.parent.true_path_output.append(the_output)
                if iter_node in iter_node.parent.orelse:
                    iter_node.parent.false_path_output.append(the_output)
            iter_node = iter_node.parent

    def visit_Name(self, node):
        self.generic_visit(node)
        type_ = bool
        if isinstance(node.parent, ast.BoolOp) or isinstance(node.parent, ast.If):
            type_ = bool
            node.isCondition = True
            self.root.conditions.append(node)
        if isinstance(node.parent, ast.Compare):
            def find_constant(n: ast.AST) -> Optional[ast.AST]:
                # 找到compare表达式里的常量, 然后根据常量类型确定parameter的类型
                # 迭代的原因是, 如果compare的表达式里有其他计算, 需要找到叶子节点.
                for child in ast.iter_child_nodes(n):
                    if isinstance(child, ast.Constant):
                        return child
                for child in ast.iter_child_nodes(n):
                    return find_constant(child)
                return None
            c = find_constant(node.parent)
            if c is not None:
                type_ = type(c.value)
            else:
                raise FormatError('Compare expression cannot decide the type of parameter.')
        the_param = Parameter.create(node, type_)
        iter_node = node
        while iter_node is not None:
            assert the_param in Parameter.parameter_pool
            iter_node.rel_params.append(the_param)
            iter_node = iter_node.parent

    def visit_Compare(self, node):
        self.generic_visit(node)
        if isinstance(node.parent, ast.BoolOp) or isinstance(node.parent, ast.If):
            node.isCondition = True
            self.root.conditions.append(node)

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Not):
            if isinstance(node.parent, ast.BoolOp) or isinstance(node.parent, ast.If):
                node.isCondition = True
                self.root.conditions.append(node)

# class DumpVisitor(ast.NodeVisitor):
    # def __init__(self):
        # self.indent = ""
    # def generic_visit(self, node):
        # if node in bool_conditions:
            # leaf = 'LEAF'
        # else:
            # leaf = ''
        # print(f"{self.indent}ast.{node.__class__.__name__},id={id(node)} {leaf}")
        # print(f"{self.indent}rel_parameters=[", end='')
        # for name in {p.name for p in node.rel_parameters}:
            # print(f'{name},', end='')
        # print(']')
        # if isinstance(node, ast.If):
            # print(f'{self.indent}true_path_output=[',end='')
            # for value in {p.value for p in node.true_path_output}:
                # print(f'{value},', end='')
            # print(']')
            # print(f'{self.indent}false_path_output=[',end='')
            # for value in {p.value for p in node.false_path_output}:
                # print(f'{value},', end='')
            # print(']')

        # # if isinstance(node.parent, ast.BoolOp) \
                # # and node in node.parent.values \
                # # and not isinstance(node, ast.BoolOp) \
                # # and not node.tested:
            # # node.istarget = True
            # # generate_test_cases_for_parameter(self.root)
            # # node.istarget = False
        # self.indent += "  "
        # super().generic_visit(node)
        # self.indent = self.indent[:-4]

class TDA_Engine():
    def __init__(self):
        self.root = None
    def load_file(self, filename):
        """Load a python style pseudo-code into ast.AST object"""
        with open(filename) as f:
            code = f.read().encode('utf-8')
        self.root = ast.parse(code)
        InitializationVisitor(self.root).visit(self.root)
        # breakpoint()

    def dump(self):
        if self.root:
            # breakpoint()
            print(dump(self.root, self.root.body[0].test.values[0], indent=2))
            print('')
            print(ast.unparse(self.root))
            # DumpVisitor().visit(self.root)


def start_tda_engine():
    # Setup logging level
    parser = argparse.ArgumentParser()
    parser.add_argument("reqfile", nargs="?")
    parser.add_argument("--loglevel")
    args = parser.parse_args()

    loglevel = str(args.loglevel).upper()
    loglevel = getattr(logging, loglevel, logging.WARNING)
    logging.getLogger("").setLevel(loglevel)

    engine = TDA_Engine()
    engine.load_file(args.reqfile)
    engine.dump()
