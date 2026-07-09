import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.file_system import FileSystem
from src.model.permission import Permission
from src.utils.fs_utils import (
    du, find_duplicates, find_permission_issues, chmod_recursive,
    generate_random_fs_by_size, find_bfs
)


class TestTask1DiskUsage(unittest.TestCase):
    """任务1：磁盘使用分析测试"""

    def setUp(self):
        self.fs = FileSystem()
        self.fs.mkdir("/", "home")
        self.fs.mkdir("/home", "user")
        self.fs.touch("/home/user", "a.txt", 100)
        self.fs.touch("/home/user", "b.txt", 200)
        self.fs.mkdir("/home/user", "docs")
        self.fs.touch("/home/user/docs", "c.pdf", 300)
        self.fs.touch("/home/user/docs", "d.pdf", 400)

    def test_du_returns_correct_sizes(self):
        """测试du计算的目录大小正确"""
        result = du(self.fs, "/")
        size_dict = {path: size for path, size in result}
        # docs目录：300+400=700
        self.assertEqual(size_dict["/home/user/docs"], 700)
        # user目录：100+200+700=1000
        self.assertEqual(size_dict["/home/user"], 1000)
        # home目录：1000
        self.assertEqual(size_dict["/home"], 1000)
        # 根目录：1000
        self.assertEqual(size_dict["/"], 1000)

    def test_du_sorted_descending(self):
        """测试结果按大小降序排列"""
        result = du(self.fs, "/")
        sizes = [size for _, size in result]
        self.assertEqual(sizes, sorted(sizes, reverse=True))

    def test_du_invalid_path(self):
        """测试无效路径返回空列表"""
        result = du(self.fs, "/nonexist")
        self.assertEqual(result, [])

    def test_du_file_path(self):
        """测试文件路径返回空列表（du只对目录有效）"""
        result = du(self.fs, "/home/user/a.txt")
        self.assertEqual(result, [])

    def test_du_empty_directory(self):
        """测试空目录"""
        self.fs.mkdir("/", "empty")
        result = du(self.fs, "/empty")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 0)


class TestTask2DuplicateFiles(unittest.TestCase):
    """任务2：复制文件检测测试"""

    def setUp(self):
        self.fs = FileSystem()
        self.fs.mkdir("/", "dir1")
        self.fs.mkdir("/", "dir2")
        self.fs.touch("/dir1", "same.txt", 500)
        self.fs.touch("/dir2", "same.txt", 500)  # 同名同大小 - 重复
        self.fs.touch("/dir1", "diffsize.txt", 100)
        self.fs.touch("/dir2", "diffsize.txt", 200)  # 同名不同大小 - 不重复
        self.fs.touch("/dir1", "unique.txt", 300)  # 唯一文件

    def test_find_duplicates_same_name_same_size(self):
        """测试同名同大小文件被识别为重复"""
        dups = find_duplicates(self.fs, "/")
        self.assertEqual(len(dups), 1)
        self.assertEqual(len(dups[0]), 2)
        self.assertEqual(dups[0][0][1], "same.txt")
        self.assertEqual(dups[0][0][2], 500)

    def test_find_duplicates_same_name_diff_size(self):
        """测试同名不同大小文件不被识别为重复"""
        dups = find_duplicates(self.fs, "/")
        all_names = [group[0][1] for group in dups]
        self.assertNotIn("diffsize.txt", all_names)

    def test_find_duplicates_unique_file(self):
        """测试唯一文件不出现在结果中"""
        dups = find_duplicates(self.fs, "/")
        all_names = [group[0][1] for group in dups]
        self.assertNotIn("unique.txt", all_names)

    def test_find_duplicates_no_duplicates(self):
        """测试无重复文件时返回空"""
        fs2 = FileSystem()
        fs2.touch("/", "a.txt", 100)
        fs2.touch("/", "b.txt", 200)
        dups = find_duplicates(fs2, "/")
        self.assertEqual(dups, [])

    def test_find_duplicates_invalid_path(self):
        """测试无效路径返回空"""
        result = find_duplicates(self.fs, "/nonexist")
        self.assertEqual(result, [])


class TestTask3PermissionAudit(unittest.TestCase):
    """任务3：权限审计测试"""

    def setUp(self):
        self.fs = FileSystem()
        self.fs.mkdir("/", "testdir")
        self.fs.touch("/testdir", "readonly.txt", 100)
        self.fs.touch("/testdir", "writable.txt", 100)
        # 设置只读文件权限：可读不可写
        self.fs._get_node_by_path("/testdir/readonly.txt").permissions = {Permission.READ, Permission.EXECUTE}

    def test_find_permission_issues_readonly(self):
        """测试查找可读不可写的文件"""
        issues = find_permission_issues(
            self.fs, "/",
            required_perms={Permission.READ},
            forbidden_perms={Permission.WRITE}
        )
        issue_paths = [path for path, _, _ in issues]
        self.assertIn("/testdir/readonly.txt", issue_paths)
        self.assertNotIn("/testdir/writable.txt", issue_paths)

    def test_chmod_recursive_add_permission(self):
        """测试递归添加权限"""
        chmod_recursive(self.fs, "/testdir", add_permission=Permission.WRITE)
        node = self.fs._get_node_by_path("/testdir/readonly.txt")
        self.assertIn(Permission.WRITE, node.permissions)

    def test_chmod_recursive_remove_permission(self):
        """测试递归移除权限"""
        chmod_recursive(self.fs, "/testdir", remove_permission=Permission.WRITE)
        node = self.fs._get_node_by_path("/testdir/writable.txt")
        self.assertNotIn(Permission.WRITE, node.permissions)

    def test_chmod_recursive_affects_children(self):
        """测试递归chmod影响所有子节点"""
        self.fs.mkdir("/testdir", "subdir")
        self.fs.touch("/testdir/subdir", "deep.txt", 100)
        chmod_recursive(self.fs, "/testdir", remove_permission=Permission.WRITE)
        deep_node = self.fs._get_node_by_path("/testdir/subdir/deep.txt")
        self.assertNotIn(Permission.WRITE, deep_node.permissions)

    def test_chmod_recursive_invalid_path(self):
        """测试无效路径返回False"""
        result = chmod_recursive(self.fs, "/nonexist", add_permission=Permission.READ)
        self.assertFalse(result)


class TestTask4RandomFSGeneration(unittest.TestCase):
    """任务4：随机文件系统生成测试"""

    def test_generate_exact_node_count(self):
        """测试生成指定节点数的文件系统"""
        for n in [50, 200, 500]:
            fs = generate_random_fs_by_size(n, wide_shallow=True)
            nodes = find_bfs(fs, "/", "*")
            self.assertEqual(len(nodes), n, f"宽浅型生成{n}节点失败，实际{len(nodes)}")

    def test_generate_narrow_deep(self):
        """测试窄深型生成"""
        fs = generate_random_fs_by_size(200, wide_shallow=False)
        nodes = find_bfs(fs, "/", "*")
        self.assertEqual(len(nodes), 200)

    def test_generate_root_exists(self):
        """测试根节点存在"""
        fs = generate_random_fs_by_size(100)
        self.assertIsNotNone(fs.root)
        self.assertEqual(fs.root.name, "/")


if __name__ == "__main__":
    unittest.main()
