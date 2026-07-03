import unittest
from mycode.part_1.file_system import FileSystem
from mycode.part_1.shell_navigator import ShellNavigator
from mycode.part_1.directory import Directory

class TestShellNavigator(unittest.TestCase):
    def setUp(self):
        # 初始化文件系统与导航器
        self.fs = FileSystem()
        self.nav = ShellNavigator(self.fs)
        # 预先创建测试目录
        self.fs.mkdir("/", "usr")
        self.fs.mkdir("/usr", "local")
        self.fs.mkdir("/usr/local", "bin")

    def test_init_state(self):
        # 初始当前目录为根，栈为空
        self.assertEqual(self.nav.current_dir, self.fs.root)
        self.assertEqual(len(self.nav.history_stack), 0)

    def test_cd_into_exist_dir_success(self):
        # 进入存在目录，入栈
        res = self.nav.cd("usr")
        self.assertTrue(res)
        self.assertEqual(self.nav.current_dir.name, "usr")
        self.assertEqual(len(self.nav.history_stack), 1)
        self.assertEqual(self.nav.history_stack[0], self.fs.root)

    def test_cd_nonexist_dir_fail(self):
        # 进入不存在目录返回False，栈不变
        res = self.nav.cd("fake_dir")
        self.assertFalse(res)
        self.assertEqual(self.nav.current_dir, self.fs.root)
        self.assertEqual(len(self.nav.history_stack), 0)

    def test_cd_into_file_fail(self):
        # cd不能进入文件，仅识别Directory
        self.fs.touch("/", "test.txt")
        res = self.nav.cd("test.txt")
        self.assertFalse(res)
        self.assertEqual(self.nav.current_dir, self.fs.root)

    def test_cd_back_normal(self):
        # 正常回退上一级目录
        self.nav.cd("usr")
        self.nav.cd("local")
        self.assertEqual(len(self.nav.history_stack), 2)
        res = self.nav.cd_back()
        self.assertTrue(res)
        self.assertEqual(self.nav.current_dir.name, "usr")
        self.assertEqual(len(self.nav.history_stack), 1)

    def test_cd_back_empty_stack_fail(self):
        # 栈为空无法回退
        res = self.nav.cd_back()
        self.assertFalse(res)
        self.assertEqual(self.nav.current_dir, self.fs.root)

    def test_pwd_root(self):
        # 在根目录pwd输出 /
        self.assertEqual(self.nav.pwd(), "/")

    def test_pwd_nested_path(self):
        # 多层目录pwd拼接完整路径
        self.nav.cd("usr")
        self.nav.cd("local")
        self.nav.cd("bin")
        self.assertEqual(self.nav.pwd(), "/usr/local/bin")

    def test_cd_root_clear_stack(self):
        # cd_root清空历史栈，切回根目录
        self.nav.cd("usr")
        self.nav.cd("local")
        self.nav.cd_root()
        self.assertEqual(self.nav.current_dir, self.fs.root)
        self.assertEqual(len(self.nav.history_stack), 0)

if __name__ == "__main__":
    unittest.main()