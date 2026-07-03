import unittest
import os
import sys

# ==========================================================
# 【关键步骤】：由于我们位于 tests/ 子目录，必须将项目根目录添加到 sys.path 中，
# 否则 Python 找不到 core 和 engine 这些包。
# ==========================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 获取 tests/ 的上一级目录（即项目根目录）
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# ==========================================================
# 导入拆分后的类（此时项目的根目录已在 sys.path 中，原有的 import 写法无需修改）
# ==========================================================
from core.base_node import FSNode
from core.directory import Directory
from core.file import File
from core.permission import Permission

from engine.file_system import FileSystem
from engine.json_persistence import save_fs_to_json, load_fs_from_json

from navigator.shell_navigator import ShellNavigator
from navigator.search_bfs import find_bfs
from navigator.search_dfs import find_dfs


class TestFileSystemTasks(unittest.TestCase):

    def setUp(self):
        """每个测试用例开始前执行：创建一个标准的文件树"""
        self.fs = FileSystem()
        self.fs.mkdir("/", "home")
        self.fs.mkdir("/home", "user")
        self.fs.touch("/home/user", "readme.md", 1024, "Hello World")
        self.fs.touch("/home/user", "config.json", 512)
        self.fs.mkdir("/home/user", "docs")
        self.fs.touch("/home/user/docs", "report.pdf", 4096)
        
        self.fs.mkdir("/home/user", "pictures")
        self.fs.mkdir("/", "tmp")

    # ==========================================
    # 任务 1: 数据建模 (继承、抽象基类、递归)
    # ==========================================
    def test_task1_inheritance_and_abstraction(self):
        """Verify inheritance and abstract base class constraints"""
        with self.assertRaises(TypeError):
            FSNode("abstract_node")
        
        dir_node = Directory("test_dir")
        file_node = File("test.txt", 100)
        self.assertIsInstance(dir_node, FSNode)
        self.assertIsInstance(file_node, FSNode)

        self.assertEqual(dir_node.get_size(), 0)
        self.assertEqual(file_node.get_size(), 100)

    def test_task1_directory_tree_recursion(self):
        """Verify directory tree recursion and parent-child relationships"""
        dir_home = self.fs._get_node_by_path("/home")
        dir_user = self.fs._get_node_by_path("/home/user")
        
        self.assertEqual(dir_user.parent, dir_home)
        self.assertIn(dir_user, dir_home.children)
        
        expected_home_size = 1024 + 512 + 4096
        self.assertEqual(dir_home.get_size(), expected_home_size)
        
        self.assertEqual(self.fs.root.child_count() + 1, 9)

    # ==========================================
    # 任务 2: 文件系统操作 (mkdir, touch, rm, mv, ls)
    # ==========================================
    def test_task2_operations(self):
        """Verify core file system operations (mkdir, touch, rm, mv, ls)"""
        self.assertTrue(self.fs.mkdir("/home/user", "bin"))
        self.assertIn("bin", self.fs.ls("/home/user"))
        self.assertIn("pictures", self.fs.ls("/home/user"))
        
        self.assertTrue(self.fs.touch("/home/user/pictures", "vacation.jpg", 5120))
        target_node = self.fs._get_node_by_path("/home/user/pictures/vacation.jpg")
        self.assertIsNotNone(target_node, "File creation failed, path not found!")
        if target_node:
            self.assertEqual(target_node.get_size(), 5120)

        self.assertTrue(self.fs.rm("/home/user/docs"))
        self.assertNotIn("docs", self.fs.ls("/home/user"))
        self.assertIsNone(self.fs._get_node_by_path("/home/user/docs/report.pdf"))

        self.assertTrue(self.fs.mv("/home/user/config.json", "/tmp"))
        self.assertIsNone(self.fs._get_node_by_path("/home/user/config.json"))
        self.assertEqual(self.fs._get_node_by_path("/tmp/config.json").parent, self.fs._get_node_by_path("/tmp"))
        self.assertIn("config.json", self.fs.ls("/tmp"))

        self.assertFalse(self.fs.rm("/"))

    # ==========================================
    # 任务 3: 导航 (ShellNavigator - 栈)
    # ==========================================
    def test_task3_shell_navigation_stack(self):
        """Verify navigation history management using a stack"""
        shell = ShellNavigator(self.fs)
        
        self.assertEqual(shell.pwd(), "/")
        self.assertEqual(len(shell.history_stack), 0)
        
        self.assertTrue(shell.cd("home"))
        self.assertEqual(shell.pwd(), "/home")
        self.assertEqual(len(shell.history_stack), 1) 
        
        self.assertTrue(shell.cd("user"))
        self.assertEqual(shell.pwd(), "/home/user")
        self.assertEqual(len(shell.history_stack), 2) 
        
        self.assertTrue(shell.cd_back())
        self.assertEqual(shell.pwd(), "/home")
        self.assertEqual(len(shell.history_stack), 1)
        
        self.assertTrue(shell.cd_back())
        self.assertEqual(shell.pwd(), "/")
        self.assertEqual(len(shell.history_stack), 0)
        
        shell.cd("home")
        shell.cd("user")
        shell.cd_root()
        self.assertEqual(shell.pwd(), "/")
        self.assertEqual(len(shell.history_stack), 0)

        self.assertFalse(shell.cd_back())
        
        self.assertIsInstance(shell.history_stack, list)

    # ==========================================
    # 任务 4: 搜索队列 (BFS vs DFS)
    # ==========================================
    def test_task4_search_bfs_dfs(self):
        """Verify BFS and DFS search functionality and order differences"""
        bfs_res = find_bfs(self.fs, "/", "*.json")
        dfs_res = find_dfs(self.fs, "/", "*.json")
        
        self.assertIn("config.json", bfs_res)
        self.assertIn("config.json", dfs_res)
        
        bfs_res_set = set(find_bfs(self.fs, "/", "r*"))
        dfs_res_set = set(find_dfs(self.fs, "/", "r*"))
        self.assertEqual(bfs_res_set, dfs_res_set)

        new_fs = FileSystem()
        new_fs.mkdir("/", "A")
        new_fs.mkdir("/", "B")
        new_fs.touch("/A", "A1.txt", 10)
        new_fs.touch("/B", "B1.txt", 10)
        
        bfs_res = find_bfs(new_fs, "/", "*.txt")
        dfs_res = find_dfs(new_fs, "/", "*.txt")
        
        self.assertEqual(set(bfs_res), set(dfs_res))

    # ==========================================
    # 任务 5: 数据持久化
    # ==========================================
    def test_task5_persistence(self):
        """Verify JSON persistence functionality"""
        save_fs_to_json(self.fs, "test_fs_save.json")
        new_fs = load_fs_from_json("test_fs_save.json")
        
        self.assertEqual(new_fs.root.get_size(), self.fs.root.get_size())
        self.assertEqual(len(new_fs.ls("/")), len(self.fs.ls("/")))
        
        if os.path.exists("test_fs_save.json"):
            os.remove("test_fs_save.json")

if __name__ == "__main__":
    unittest.main()