# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest
from cmdb.config_item import *

class TestTools(unittest.TestCase):
    def test_tableName2Type(self):
        self.assertEqual(tableName2Type("NS_NAME_1_0_0"), "NS-NAME-1.0.0")

    def test_id2rid(self):
        self.assertEqual(id2rid("22_0"), "#22:0")

    def test_rid2id(self):
        self.assertEqual(rid2id("#22:10"), "22_10")

    def test_valid_not(self):
        self.assertEqual(valid_not("not ()", 0, 6), (True, 3))
        self.assertEqual(valid_not("not()", 0, 5), (True, 3))
        self.assertEqual(valid_not("not   ()", 0, 8), (True, 3))
        self.assertEqual(valid_not(" not()", 0, 6), (False, 0))
        self.assertEqual(valid_not("not", 0, 3), (False, 0))
        self.assertEqual(valid_not("not[", 0, 4), (False, 0))
        self.assertEqual(valid_not("notA", 0, 4), (False, 0))
        self.assertEqual(valid_not("", 0, 0), (False, 0))

    def test_valid_key(self):
        self.assertEqual(valid_key("name ", 0, 5), (True, 4))
        self.assertEqual(valid_key("name= ", 0, 5), (True, 4))
        self.assertEqual(valid_key("name123 = ", 0, 10), (True, 7))
        self.assertEqual(valid_key("name123", 0, 7), (False, 0))
        self.assertEqual(valid_key(" name123 = ", 0, 11), (False, 0))
        self.assertEqual(valid_key("name123-", 0, 8), (False, 0))
        self.assertEqual(valid_key("name123[", 0, 8), (False, 0))
        self.assertEqual(valid_key("name123(", 0, 8), (False, 0))
        self.assertEqual(valid_key("123name(", 0, 8), (False, 0))

    def test_valid_op(self):
        self.assertEqual(valid_op('> ', 0, 2), (True, 1))
        self.assertEqual(valid_op('< ', 0, 2), (True, 1))
        self.assertEqual(valid_op('= ', 0, 2), (True, 1))
        self.assertEqual(valid_op('>= ', 0, 3), (True, 2))
        self.assertEqual(valid_op('<= ', 0, 3), (True, 2))
        self.assertEqual(valid_op('<> ', 0, 3), (True, 2))
        self.assertEqual(valid_op('like "', 0, 6), (True, 5))
        self.assertEqual(valid_op('in [', 0, 4), (True, 3))
        self.assertEqual(valid_op('+ ', 0, 2), (False, 0))
        self.assertEqual(valid_op('- ', 0, 2), (False, 0))
        self.assertEqual(valid_op('& ', 0, 2), (False, 0))
        self.assertEqual(valid_op('* ', 0, 2), (False, 0))
        self.assertEqual(valid_op('=', 0, 1), (False, 0))

    def test_valid_logic_op(self):
        self.assertEqual(valid_logic_op('And ', 0, 4), (True, 3))
        self.assertEqual(valid_logic_op('and ', 0, 4), (True, 3))
        self.assertEqual(valid_logic_op('AND ', 0, 4), (True, 3))
        self.assertEqual(valid_logic_op('and(', 0, 4), (True, 3))
        self.assertEqual(valid_logic_op('Or ', 0, 3), (True, 2))
        self.assertEqual(valid_logic_op('OR ', 0, 3), (True, 2))
        self.assertEqual(valid_logic_op('or ', 0, 3), (True, 2))
        self.assertEqual(valid_logic_op('or ', 0, 3), (True, 2))
        self.assertEqual(valid_logic_op('or(', 0, 3), (True, 2))
    def test_valid_str(self):
        self.assertEqual(valid_str('"I <> string"', 0, 13), (True, 13))
        self.assertEqual(valid_str("'I 18 string'", 0, 13), (True, 13))
        self.assertEqual(valid_str('"I \\"am string"', 0, 15), (True, 15))
        self.assertEqual(valid_str("'I \\'am string'", 0, 15), (True, 15))
        self.assertEqual(valid_str("'I am \"string'", 0, 14), (True, 14))
        self.assertEqual(valid_str('"I am \'string"', 0, 14), (True, 14))
        self.assertEqual(valid_str('"I am string', 0, 12), (False, 0))
        self.assertEqual(valid_str("'I am string", 0, 12), (False, 0))
        self.assertEqual(valid_str("'I am string", 0, 12), (False, 0))

    def test_valid_number(self):
        self.assertEqual(valid_number("10", 0, 2), (True, 2))
        self.assertEqual(valid_number("10 ", 0, 3), (True, 2))
        self.assertEqual(valid_number("10.0", 0, 4), (True, 4))
        self.assertEqual(valid_number("10.0 ", 0, 5), (True, 4))
        self.assertEqual(valid_number("10)", 0, 3), (True, 2))
        self.assertEqual(valid_number("10.00)", 0, 6), (True, 5))

    def test_valid_list(self):
        self.assertEqual(valid_list("['a', 'b', 'c']", 0, 15), (True, 15))
        self.assertEqual(valid_list("[ 1 ,  2 ,  3 ]", 0, 15), (True, 15))
        self.assertEqual(valid_list("[1, 2, 3]", 0, 9), (True, 9))

    def test_valid_single_statement(self):
        for s in ["name = 'value'", "name = 12", "name=12", "name='value'", "name='value'", "name='value'","name in ['value', \"value\"]", "name in [1, 2, 3]", "name like 'name%'", "name > 12", "name >= 12", "name <> 12"]:
            self.assertEqual(valid_single_statement(s, 0, len(s)), (True, len(s)))

    def test_valid_not_statement(self):
        for s in ["not(a=12)", "not (a = 12)"]:
            self.assertEqual(valid_not_statement(s, 0, len(s)), (True, len(s)))
    def test_valid_bracket_statement(self):
        for s in ["(name = 12)", "((name = 12))", "(name = 12 and name2 = 13)", "(name = 13 and not(name2 = 12))"]:
            self.assertEqual(valid_bracket_statement(s, 0, len(s)), (True, len(s)))
    def test_valid_statement(self):
        test_cases = ["attr = 12 and attr2 = 'str' or not(attr3 in [1 , 2])",
                "(attr = 12 or attr2 = 'str') and attr3 = 'str'",
                "attr = 'str' or (attr2 = 2 and attr3 = 3)"
                ]
        for s in test_cases:
            self.assertEqual(valid_statement(s, 0, len(s)), (True, len(s)))
