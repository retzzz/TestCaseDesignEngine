import unittest
import ast
import pathlib

import tda_engine

class Test_Req_Init(unittest.TestCase):
    engine = None

    @classmethod
    def setUpClass(cls):
        cls.engine = tda_engine.TDA_Engine()
        path = pathlib.Path(__file__).parent.resolve()
        cls.engine.load_file(path/'req1.txt')

    def test_parent(self):
        self.assertIsNone(self.engine.root.parent)
        self.assertIsInstance(self.engine.root.body[0], ast.If)
        self.assertIs(self.engine.root.body[0].parent, self.engine.root)
        self.assertIs(self.engine.root.body[0].test.parent, self.engine.root.body[0])

    def test_condition(self):
        self.assertEqual(len(self.engine.root.conditions), 7)
        self.assertIsInstance(self.engine.root.conditions[0], ast.Name)
        self.assertEqual(self.engine.root.conditions[0].id, 'A')
        self.assertEqual(self.engine.root.conditions[0].isCondition, True)
        self.assertEqual(self.engine.root.conditions[1].id, 'B')
        self.assertEqual(self.engine.root.conditions[1].isCondition, True)
        self.assertEqual(self.engine.root.conditions[2].id, 'C')
        self.assertEqual(self.engine.root.conditions[2].isCondition, True)
        self.assertIsInstance(self.engine.root.conditions[3], ast.UnaryOp)
        self.assertEqual(self.engine.root.conditions[3].isCondition, True)
        self.assertIsInstance(self.engine.root.conditions[4], ast.Compare)
        self.assertEqual(self.engine.root.conditions[4].isCondition, True)
        self.assertIsInstance(self.engine.root.conditions[5], ast.Name)
        self.assertEqual(self.engine.root.conditions[5].id, 'B')
        self.assertIsInstance(self.engine.root.conditions[6], ast.Name)
        self.assertEqual(self.engine.root.conditions[6].id, 'C')

    def test_parameter(self):
        self.assertEqual(len(tda_engine.Parameter.parameter_pool), 4)
        self.assertEqual(tda_engine.Parameter.parameter_pool[0].name, 'A')
        self.assertEqual(len(tda_engine.Parameter.parameter_pool[0].ast_nodes), 1)
        self.assertIs(tda_engine.Parameter.parameter_pool[0].type_, bool)
        self.assertEqual(tda_engine.Parameter.parameter_pool[1].name, 'B')
        self.assertEqual(len(tda_engine.Parameter.parameter_pool[1].ast_nodes), 3)
        self.assertIs(tda_engine.Parameter.parameter_pool[1].ast_nodes[0].rel_params[0], tda_engine.Parameter.parameter_pool[1])
        self.assertIs(tda_engine.Parameter.parameter_pool[1].type_, bool)
        self.assertEqual(tda_engine.Parameter.parameter_pool[2].name, 'C')
        self.assertEqual(len(tda_engine.Parameter.parameter_pool[2].ast_nodes), 2)
        self.assertIs(tda_engine.Parameter.parameter_pool[2].type_, bool)
        self.assertEqual(tda_engine.Parameter.parameter_pool[3].name, 'D')
        self.assertEqual(len(tda_engine.Parameter.parameter_pool[3].ast_nodes), 1)
        self.assertIs(tda_engine.Parameter.parameter_pool[3].type_, int)

    def test_output(self):
        self.assertEqual(len(tda_engine.Output.output_pool), 2)
        self.assertEqual(tda_engine.Output.output_pool[0].value, 'output 1')
        self.assertEqual(len(tda_engine.Output.output_pool[0].ast_nodes), 2)
        self.assertIs(tda_engine.Output.output_pool[0].ast_nodes[0].output, tda_engine.Output.output_pool[0])
        self.assertIs(tda_engine.Output.output_pool[0].ast_nodes[1].output, tda_engine.Output.output_pool[0])
        self.assertEqual(tda_engine.Output.output_pool[1].value, 'output 2')
        self.assertEqual(len(tda_engine.Output.output_pool[1].ast_nodes), 2)
        self.assertEqual(tda_engine.Output.output_pool[1].ast_nodes[0].output, tda_engine.Output.output_pool[1])
        self.assertEqual(tda_engine.Output.output_pool[1].ast_nodes[1].output, tda_engine.Output.output_pool[1])

    # @classmethod
    # def tearDownClass(cls):
        # print(tda_engine.util.dump(cls.engine.root, indent=2))
        # print(cls.engine.root.conditions)

if __name__ == '__main__':
    unittest.main()

