import sys
import os
import unittest

# 添加项目根目录到Python路径，保证跨目录导入正常
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.model.permission import Permission

class TestPermission(unittest.TestCase):
    def test_enum_members_exist(self):
        self.assertTrue(hasattr(Permission, "READ"))
        self.assertTrue(hasattr(Permission, "WRITE"))
        self.assertTrue(hasattr(Permission, "EXECUTE"))

    def test_enum_value_mapping(self):
        self.assertEqual(Permission.READ.value, 1)
        self.assertEqual(Permission.WRITE.value, 2)
        self.assertEqual(Permission.EXECUTE.value, 3)

    def test_enum_name_mapping(self):
        self.assertEqual(Permission.READ.name, "READ")
        self.assertEqual(Permission.WRITE.name, "WRITE")
        self.assertEqual(Permission.EXECUTE.name, "EXECUTE")

    def test_enum_is_enum_instance(self):
        from enum import Enum
        self.assertIsInstance(Permission.READ, Enum)

    def test_iter_all_permissions(self):
        all_perms = list(Permission)
        self.assertEqual(len(all_perms), 3)

if __name__ == "__main__":
    unittest.main()
