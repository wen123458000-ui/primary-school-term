import sys
import os
import unittest
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.model.file import File
from src.model.fs_node import FSNode
from src.model.permission import Permission

class TestFile(unittest.TestCase):
    def setUp(self):
        self.txt_file = File("note.txt", 2048, "hello world")
        self.no_ext_file = File("readme", 512)
        self.child_file = File("data.csv", 4096, parent="fake_parent")

    def test_init_basic_attr(self):
        self.assertEqual(self.txt_file.name, "note.txt")
        self.assertEqual(self.txt_file.size_bytes, 2048)
        self.assertEqual(self.txt_file.content, "hello world")
        self.assertEqual(self.txt_file.parent, None)

    def test_extension_parse(self):
        self.assertEqual(self.txt_file.extension, "txt")
        self.assertEqual(self.no_ext_file.extension, "")
        self.assertEqual(self.child_file.extension, "csv")

    def test_get_size_return_bytes(self):
        self.assertEqual(self.txt_file.get_size(), 2048)
        self.assertEqual(self.no_ext_file.get_size(), 512)

    def test_inherit_fsnode(self):
        self.assertTrue(issubclass(File, FSNode))
        self.assertIsInstance(self.txt_file.created_at, datetime)
        self.assertEqual(self.txt_file.permissions, {Permission.READ, Permission.WRITE, Permission.EXECUTE})

    def test_parent_assignment(self):
        self.assertEqual(self.child_file.parent, "fake_parent")

if __name__ == "__main__":
    unittest.main()
