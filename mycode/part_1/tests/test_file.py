import unittest
from datetime import datetime
from mycode.part_1.file import File
from mycode.part_1.fs_node import FSNode
from mycode.part_1.permission import Permission

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