from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import json
import random
import re
from collections import deque


# 权限枚举
class Permission(Enum):
    READ = 1
    WRITE = 2
    EXECUTE = 3


# 抽象父类
class FSNode(ABC):
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.permissions = {Permission.READ, Permission.WRITE, Permission.EXECUTE}

    @abstractmethod
    def get_size(self):
        pass


# 目录子类
class Directory(FSNode):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.children = []

    def get_size(self):
        total = 0
        for child in self.children:
            total += child.get_size()
        return total

    def child_count(self):
        count = 0
        for child in self.children:
            if isinstance(child, Directory):
                count += 1 + child.child_count()
            else:
                count += 1
        return count


# 文件子类
class File(FSNode):
    def __init__(self, name, size_bytes, content="", parent=None):
        super().__init__(name, parent)
        self.size_bytes = size_bytes
        self.content = content
        self.extension = name.split(".")[-1] if "." in name else ""

    def get_size(self):
        return self.size_bytes


# 文件系统核心操作
class FileSystem:
    def __init__(self):
        self.root = Directory("/")

    def _get_node_by_path(self, path):
        if path in ("/", ""):
            return self.root
        parts = path.strip("/").split("/")
        current = self.root
        for part in parts:
            found = False
            for child in current.children:
                if child.name == part and isinstance(child, Directory):
                    current = child
                    found = True
                    break
            if not found:
                return None
        return current

    def mkdir(self, parent_path, dir_name):
        parent = self._get_node_by_path(parent_path)
        if not parent or not isinstance(parent, Directory):
            return False
        for child in parent.children:
            if child.name == dir_name:
                return False
        parent.children.append(Directory(dir_name, parent))
        parent.modified_at = datetime.now()
        return True

    def touch(self, parent_path, file_name, size_bytes=0, content=""):
        parent = self._get_node_by_path(parent_path)
        if not parent or not isinstance(parent, Directory):
            return False
        for child in parent.children:
            if child.name == file_name:
                return False
        parent.children.append(File(file_name, size_bytes, content, parent))
        parent.modified_at = datetime.now()
        return True

    def rm(self, path):
        target = self._get_node_by_path(path)
        if not target or target == self.root:
            return False
        target.parent.children.remove(target)
        target.parent.modified_at = datetime.now()
        return True

    def mv(self, source_path, dest_path):
        source = self._get_node_by_path(source_path)
        dest = self._get_node_by_path(dest_path)
        if not source or not dest or not isinstance(dest, Directory) or source == self.root:
            return False
        source.parent.children.remove(source)
        source.parent = dest
        dest.children.append(source)
        dest.modified_at = datetime.now()
        source.modified_at = datetime.now()
        return True

    def ls(self, path="/"):
        node = self._get_node_by_path(path)
        if not node or not isinstance(node, Directory):
            return []
        return [child.name for child in node.children]

    def tree(self, path="/", indent=0):
        node = self._get_node_by_path(path)
        if not node:
            return ""
        res = "  " * indent + node.name + "\n"
        if isinstance(node, Directory):
            for child in node.children:
                child_path = f"{path.rstrip('/')}/{child.name}".replace("//", "/")
                if isinstance(child, Directory):
                    res += self.tree(child_path, indent + 1)
                else:
                    res += "  " * (indent + 1) + child.name + "\n"
        return res


# 栈式终端导航器
class ShellNavigator:
    def __init__(self, fs):
        self.fs = fs
        self.current_dir = fs.root
        self.history_stack = []

    def cd(self, dir_name):
        for child in self.current_dir.children:
            if child.name == dir_name and isinstance(child, Directory):
                self.history_stack.append(self.current_dir)
                self.current_dir = child
                return True
        return False

    def cd_back(self):
        if not self.history_stack:
            return False
        self.current_dir = self.history_stack.pop()
        return True

    def pwd(self):
        path = []
        temp = self.current_dir
        while temp.parent:
            path.insert(0, temp.name)
            temp = temp.parent
        return "/" + "/".join(path)

    def cd_root(self):
        self.history_stack.clear()
        self.current_dir = self.fs.root


# 通配符匹配工具
def wildcard_match(pattern, name):
    regex = "^" + re.escape(pattern).replace(r"\*", ".*") + "$"
    return re.match(regex, name) is not None


# BFS广度优先搜索
def find_bfs(fs, start_path, pattern):
    start = fs._get_node_by_path(start_path)
    if not start:
        return []
    res = []
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if wildcard_match(pattern, node.name):
            res.append(node.name)
        if isinstance(node, Directory):
            queue.extend(node.children)
    return res


# DFS深度优先搜索
def find_dfs(fs, start_path, pattern):
    start = fs._get_node_by_path(start_path)
    if not start:
        return []
    res = []
    stack = [start]
    while stack:
        node = stack.pop()
        if wildcard_match(pattern, node.name):
            res.append(node.name)
        if isinstance(node, Directory):
            stack.extend(reversed(node.children))
    return res


# 查找重复文件名
def find_duplicates(fs, start_path="/"):
    start = fs._get_node_by_path(start_path)
    if not start:
        return []
    name_count = {}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        name_count[node.name] = name_count.get(node.name, 0) + 1
        if isinstance(node, Directory):
            queue.extend(node.children)
    return [name for name, cnt in name_count.items() if cnt > 1]


# 随机生成文件树
def generate_random_fs(min_depth=4, min_nodes=30):
    fs = FileSystem()
    dir_names = ["docs", "images", "code", "data", "reports", "src", "test", "bin", "lib", "config"]
    file_names = ["report", "data", "log", "config", "readme", "main", "utils", "test", "output", "input"]
    extensions = [".txt", ".py", ".json", ".csv", ".md", ".jpg", ".png", ".log"]

    node_count = 1
    depth = 0
    current_dirs = [("/", fs.root)]

    while node_count < min_nodes or depth < min_depth:
        next_dirs = []
        for path, dir_node in current_dirs:
            branch = random.randint(2, 4)
            for _ in range(branch):
                if random.random() < 0.6:
                    name = random.choice(dir_names) + str(random.randint(1, 99))
                    new_path = f"{path.rstrip('/')}/{name}".replace("//", "/")
                    if fs.mkdir(path, name):
                        node_count += 1
                        next_dirs.append((new_path, dir_node.children[-1]))
                else:
                    name = random.choice(file_names) + str(random.randint(1, 99)) + random.choice(extensions)
                    size = random.randint(10, 10240)
                    if fs.touch(path, name, size):
                        node_count += 1
        current_dirs = next_dirs
        depth += 1
        if depth > 6:
            break
    return fs


# JSON序列化与持久化
def _serialize_node(node):
    data = {
        "name": node.name,
        "type": "directory" if isinstance(node, Directory) else "file",
        "created_at": node.created_at.isoformat(),
        "modified_at": node.modified_at.isoformat(),
        "permissions": [p.name for p in node.permissions]
    }
    if isinstance(node, Directory):
        data["children"] = [_serialize_node(c) for c in node.children]
    else:
        data["size_bytes"] = node.size_bytes
        data["content"] = node.content
        data["extension"] = node.extension
    return data


def save_fs_to_json(fs, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(_serialize_node(fs.root), f, ensure_ascii=False, indent=2)


def _deserialize_node(data, parent=None):
    if data["type"] == "directory":
        node = Directory(data["name"], parent)
        node.children = [_deserialize_node(c, node) for c in data["children"]]
    else:
        node = File(data["name"], data["size_bytes"], data["content"], parent)
        node.extension = data["extension"]
    node.created_at = datetime.fromisoformat(data["created_at"])
    node.modified_at = datetime.fromisoformat(data["modified_at"])
    node.permissions = {Permission[p] for p in data["permissions"]}
    return node


def load_fs_from_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    fs = FileSystem()
    fs.root = _deserialize_node(data)
    return fs


# 运行演示
if __name__ == "__main__":
    fs = FileSystem()
    fs.mkdir("/", "home")
    fs.mkdir("/home", "user")
    fs.touch("/home/user", "test.txt", 1024, "hello world")
    fs.touch("/home/user", "report1.docx", 2048)
    fs.mkdir("/home/user", "docs")
    fs.touch("/home/user/docs", "report2.pdf", 4096)

    print("=== 目录树 ===")
    print(fs.tree())
    print("=== ls /home/user ===", fs.ls("/home/user"))

    shell = ShellNavigator(fs)
    shell.cd("home")
    shell.cd("user")
    print("=== 当前路径 ===", shell.pwd())
    shell.cd_back()
    print("=== 回退后路径 ===", shell.pwd())

    print("=== BFS搜索report* ===", find_bfs(fs, "/", "report*"))
    print("=== DFS搜索report* ===", find_dfs(fs, "/", "report*"))

    print("\n=== 随机生成文件树 ===")
    random_fs = generate_random_fs()
    print("总节点数:", random_fs.root.child_count() + 1)
    print(random_fs.tree())

    save_fs_to_json(fs, "filesystem.json")
    print("已保存到 filesystem.json")