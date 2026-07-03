import unittest
from mycode.part_1.directory import Directory
from mycode.part_1.fs_node import FSNode

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