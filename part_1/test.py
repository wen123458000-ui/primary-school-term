import unittest
import unittest
from permission import Permission
from fs_node import FSNode
from directory import Directory
from file import File
from file_system import FileSystem
from shell_navigator import ShellNavigator
from fs_utils import find_bfs, find_dfs, find_duplicates, save_fs_to_json, load_fs_from_json, generate_random_fs



class TestFileSystem(unittest.TestCase):
    def setUp(self):
        self.fs = FileSystem()
        self.fs.mkdir("/", "dir1")
        self.fs.mkdir("/", "dir2")
        self.fs.touch("/dir1", "file1.txt", 100)
        self.fs.touch("/dir1", "file2.txt", 200)
        self.fs.touch("/dir2", "file1.txt", 150)
        self.fs.mkdir("/dir1", "subdir")
        self.fs.touch("/dir1/subdir", "file3.txt", 300)

    # 1. 父子节点关联正确性
    def test_parent_child_relation(self):
        dir1 = self.fs._get_node_by_path("/dir1")
        self.assertEqual(len(dir1.children), 3)
        for child in dir1.children:
            self.assertEqual(child.parent, dir1)
        subdir = self.fs._get_node_by_path("/dir1/subdir")
        self.assertEqual(subdir.parent, dir1)

    # 2. 根目录总大小 = 全部文件字节总和
    def test_total_size(self):
        total = 100 + 200 + 150 + 300
        self.assertEqual(self.fs.root.get_size(), total)

    # 3. BFS/DFS 结果集合一致，仅顺序不同
    def test_bfs_dfs_consistent(self):
        bfs_res = find_bfs(self.fs, "/", "file*")
        dfs_res = find_dfs(self.fs, "/", "file*")
        self.assertEqual(set(bfs_res), set(dfs_res))
        self.assertNotEqual(bfs_res, dfs_res)

    # 4. 重复文件识别
    def test_find_duplicates(self):
        dups = find_duplicates(self.fs)
        self.assertIn("file1.txt", dups)

    # 5. 导航栈回退逻辑正确性
    def test_shell_navigation(self):
        shell = ShellNavigator(self.fs)
        shell.cd("dir1")
        self.assertEqual(shell.pwd(), "/dir1")
        shell.cd("subdir")
        self.assertEqual(shell.pwd(), "/dir1/subdir")
        shell.cd_back()
        self.assertEqual(shell.pwd(), "/dir1")
        shell.cd_root()
        self.assertEqual(shell.pwd(), "/")

    # 附加：JSON持久化正确性
    def test_json_serialization(self):
        save_fs_to_json(self.fs, "test_fs.json")
        loaded = load_fs_from_json("test_fs.json")
        self.assertEqual(loaded.root.get_size(), self.fs.root.get_size())
        self.assertEqual(len(loaded.root.children), len(self.fs.root.children))


if __name__ == "__main__":
    unittest.main()