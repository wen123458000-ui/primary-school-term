import sys
import os
import unittest
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.file_system import FileSystem
from src.utils.fs_utils import (
    wildcard_match,
    find_bfs,
    find_dfs,
    find_duplicates,
    generate_random_fs,
    save_fs_to_json,
    load_fs_from_json
)

class TestFsUtils(unittest.TestCase):
    def setUp(self):
        # 初始化基础文件系统结构
        self.fs = FileSystem()
        self.fs.mkdir("/", "src")
        self.fs.mkdir("/src", "utils")
        self.fs.touch("/", "readme.md", 100, "root readme")
        self.fs.touch("/src", "main.py", 200)
        self.fs.touch("/src", "utils.py", 150)
        self.fs.touch("/src/utils", "utils.py", 150)  # 同名且同大小，才算重复
        self.fs.touch("/src/utils", "log.txt", 50)

    # 1. 测试通配符匹配 wildcard_match
    def test_wildcard_match_exact(self):
        self.assertTrue(wildcard_match("main.py", "main.py"))
        self.assertFalse(wildcard_match("main.py", "utils.py"))

    def test_wildcard_match_star_suffix(self):
        self.assertTrue(wildcard_match("*.py", "main.py"))
        self.assertTrue(wildcard_match("*.py", "utils.py"))
        self.assertFalse(wildcard_match("*.py", "readme.md"))

    def test_wildcard_match_star_prefix(self):
        self.assertTrue(wildcard_match("util*", "utils.py"))
        self.assertFalse(wildcard_match("util*", "main.py"))

    def test_wildcard_match_mid_star(self):
        self.assertTrue(wildcard_match("u*.py", "utils.py"))
        self.assertFalse(wildcard_match("u*.py", "log.txt"))

    # 2. BFS广度优先搜索
    def test_find_bfs_nonexist_start(self):
        res = find_bfs(self.fs, "/fake_path", "*")
        self.assertEqual(res, [])

    def test_find_bfs_match_all(self):
        all_names = find_bfs(self.fs, "/", "*")
        expect_raw = [
            "/", "readme.md", "src", "main.py", "utils.py", "utils", "utils.py", "log.txt"
        ]
        # 两边同时排序再对比，消除遍历顺序差异导致失败
        self.assertListEqual(sorted(all_names), sorted(expect_raw))

    def test_find_bfs_match_py(self):
        py_files = find_bfs(self.fs, "/", "*.py")
        self.assertListEqual(sorted(py_files), sorted(["main.py", "utils.py", "utils.py"]))

    # 3. DFS深度优先搜索
    def test_find_dfs_nonexist_start(self):
        res = find_dfs(self.fs, "/fake_path", "*")
        self.assertEqual(res, [])

    def test_find_dfs_order_depth(self):
        res = find_dfs(self.fs, "/", "*.txt")
        self.assertEqual(res, ["log.txt"])

    def test_find_dfs_match_md(self):
        md_list = find_dfs(self.fs, "/", "*.md")
        self.assertEqual(md_list, ["readme.md"])

    # 4. 查找重复文件 find_duplicates（同名且同大小，成对返回）
    def test_find_duplicates_has_dup(self):
        dup_groups = find_duplicates(self.fs, "/")
        # 应该有1组重复
        self.assertEqual(len(dup_groups), 1)
        # 每组有2个文件
        self.assertEqual(len(dup_groups[0]), 2)
        # 文件名都是utils.py，大小都是150
        self.assertEqual(dup_groups[0][0][1], "utils.py")
        self.assertEqual(dup_groups[0][0][2], 150)

    def test_find_duplicates_no_dup_after_clean(self):
        # 删除一处重复文件
        self.fs.rm("/src/utils/utils.py")
        dup_groups = find_duplicates(self.fs, "/")
        self.assertEqual(len(dup_groups), 0)

    def test_find_duplicates_invalid_path(self):
        res = find_duplicates(self.fs, "/none")
        self.assertEqual(res, [])

    # 5. 随机生成文件树 generate_random_fs
    def test_generate_random_fs_min_constraint(self):
        rand_fs = generate_random_fs(min_depth=2, min_nodes=10)
        # 节点总数大于等于最小节点数
        all_nodes = find_bfs(rand_fs, "/", "*")
        self.assertGreaterEqual(len(all_nodes), 10)

    def test_generate_random_fs_depth_limit(self):
        rand_fs = generate_random_fs(min_depth=5, min_nodes=20)
        tree_str = rand_fs.tree("/")
        self.assertIn("  " * 4, tree_str)

    # 6. JSON序列化与反序列化 save_fs_to_json / load_fs_from_json
    def test_json_save_load_consistent(self):
        # 创建临时json文件，测试完成自动删除
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False, encoding="utf-8") as tmp_file:
            tmp_path = tmp_file.name
        try:
            # 保存
            save_fs_to_json(self.fs, tmp_path)
            # 加载新文件系统
            loaded_fs = load_fs_from_json(tmp_path)
            # 校验ls列表一致
            self.assertEqual(sorted(self.fs.ls("/")), sorted(loaded_fs.ls("/")))
            self.assertEqual(sorted(self.fs.ls("/src")), sorted(loaded_fs.ls("/src")))
            # 校验重复文件查找结果一致
            original_dup = find_duplicates(self.fs, "/")
            loaded_dup = find_duplicates(loaded_fs, "/")
            self.assertEqual(original_dup, loaded_dup)
        finally:
            os.unlink(tmp_path)

    def test_load_fs_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            load_fs_from_json("not_exist_12345.json")

if __name__ == "__main__":
    unittest.main()
