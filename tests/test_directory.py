import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.model.directory import Directory
from src.model.fs_node import FSNode

class TestDirectory(unittest.TestCase):
    def setUp(self):
        self.root = Directory("/", None)

    def test_init_children_empty(self):
        self.assertEqual(self.root.children, [])

    def test_get_size_empty(self):
        self.assertEqual(self.root.get_size(), 0)

    def test_child_count_empty(self):
        self.assertEqual(self.root.child_count(), 0)

if __name__ == "__main__":
    unittest.main()
