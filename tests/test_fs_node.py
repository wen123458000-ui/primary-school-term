import sys
import os
import unittest
from abc import ABC
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.model.fs_node import FSNode
from src.model.permission import Permission

class TempFSNode(FSNode):
    def get_size(self):
        return 1024

class TestFSNode(unittest.TestCase):
    def setUp(self):
        self.node = TempFSNode("test_node", parent=None)

    def test_parent_name_init(self):
        self.assertEqual(self.node.name, "test_node")
        self.assertEqual(self.node.parent, None)

    def test_permission_default_set(self):
        self.assertEqual(
            self.node.permissions,
            {Permission.READ, Permission.WRITE, Permission.EXECUTE}
        )

    def test_time_datatype(self):
        self.assertIsInstance(self.node.created_at, datetime)
        self.assertIsInstance(self.node.modified_at, datetime)

    def test_is_abc_abstract(self):
        self.assertTrue(issubclass(FSNode, ABC))
        with self.assertRaises(TypeError):
            FSNode("fail")

    def test_abstract_method_implemented(self):
        self.assertEqual(self.node.get_size(), 1024)

if __name__ == "__main__":
    unittest.main()
