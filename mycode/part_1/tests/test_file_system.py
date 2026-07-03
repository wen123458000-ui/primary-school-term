import unittest
from datetime import datetime
from mycode.part_1.file_system import FileSystem
from mycode.part_1.directory import Directory
from mycode.part_1.file import File
from mycode.part_1.fs_node import FSNode
from mycode.part_1.permission import Permission

class TestFileSystem(unittest.TestCase):
    def setUp(self):
        # 每个测试新建独立文件系统实例
        self.fs = FileSystem()

    # 测试初始化根目录
    def test_init_root_dir(self):
        self.assertEqual(self.fs.root.name, "/")
        self.assertIsInstance(self.fs.root, Directory)
        self.assertEqual(self.fs.root.children, [])

    # 测试私有路径查找方法 _get_node_by_path
    def test_get_node_by_root_path(self):
        node1 = self.fs._get_node_by_path("/")
        node2 = self.fs._get_node_by_path("")
        self.assertEqual(node1, self.fs.root)
        self.assertEqual(node2, self.fs.root)

    def test_get_node_invalid_path_return_none(self):
        res = self.fs._get_node_by_path("/nonexist")
        self.assertIsNone(res)

    def test_mkdir_create_new_dir_success(self):
        flag = self.fs.mkdir("/", "home")
        self.assertEqual(flag, True)
        self.assertEqual(self.fs.ls("/"), ["home"])

    def test_mkdir_duplicate_name_fail(self):
        self.fs.mkdir("/", "home")
        flag = self.fs.mkdir("/", "home")
        self.assertEqual(flag, False)

    def test_mkdir_invalid_parent_path_fail(self):
        flag = self.fs.mkdir("/fake", "test")
        self.assertEqual(flag, False)

    # touch 创建文件测试
    def test_touch_create_file_success(self):
        flag = self.fs.touch("/", "test.txt", 100, "test content")
        self.assertTrue(flag)
        self.assertEqual(self.fs.ls("/"), ["test.txt"])

    def test_touch_duplicate_file_fail(self):
        self.fs.touch("/", "test.txt")
        flag = self.fs.touch("/", "test.txt")
        self.assertFalse(flag)

    def test_touch_invalid_parent_fail(self):
        flag = self.fs.touch("/wrong", "a.txt")
        self.assertFalse(flag)

    # ls 列出子节点
    def test_ls_empty_root(self):
        self.assertEqual(self.fs.ls("/"), [])

    def test_ls_mixed_dir_file(self):
        self.fs.mkdir("/", "doc")
        self.fs.touch("/", "readme.md")
        output = self.fs.ls("/")
        self.assertListEqual(sorted(output), ["doc", "readme.md"])

    # rm 删除节点
    def test_rm_delete_file_success(self):
        self.fs.touch("/", "del.txt")
        self.assertTrue(self.fs.rm("/del.txt"))
        self.assertEqual(self.fs.ls("/"), [])

    def test_rm_cannot_delete_root(self):
        self.assertFalse(self.fs.rm("/"))

    def test_rm_nonexist_path_fail(self):
        self.assertFalse(self.fs.rm("/nothing"))

    # mv 移动节点
    def test_mv_move_file_to_dir(self):
        self.fs.mkdir("/", "target")
        self.fs.touch("/", "move.txt")
        flag = self.fs.mv("/move.txt", "/target")
        self.assertTrue(flag)
        self.assertEqual(self.fs.ls("/"), ["target"])
        self.assertEqual(self.fs.ls("/target"), ["move.txt"])

    def test_mv_nonexist_source_fail(self):
        self.fs.mkdir("/", "dst")
        self.assertFalse(self.fs.mv("/no", "/dst"))

    def test_mv_dest_not_dir_fail(self):
        self.fs.touch("/", "file1")
        self.fs.touch("/", "file2")
        self.assertFalse(self.fs.mv("/file1", "/file2"))

    # tree 树形字符串输出
    def test_tree_empty_root(self):
        output = self.fs.tree("/")
        self.assertEqual(output, "/\n")

    def test_tree_mixed_structure(self):
        self.fs.mkdir("/", "home")
        self.fs.touch("/home", "note.txt")
        self.fs.mkdir("/home", "work")
        tree_str = self.fs.tree("/")
        self.assertIn("/", tree_str)
        self.assertIn("home", tree_str)
        self.assertIn("note.txt", tree_str)
        self.assertIn("work", tree_str)

if __name__ == "__main__":
    unittest.main()