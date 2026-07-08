import json
import random
import re
from datetime import datetime
# 导入自定义数据结构，不再使用collections.deque和原生list模拟栈/队列
from src.data_structure import CustomQueue, CustomStack
from src.model.permission import Permission
from src.model.directory import Directory
from src.model.file import File
from src.core.file_system import FileSystem

# 通配符匹配工具
def wildcard_match(pattern, name):
    regex = "^" + re.escape(pattern).replace(r"\*", ".*") + "$"
    return re.match(regex, name) is not None

# BFS广度优先搜索（使用自定义队列，FIFO保证层级遍历顺序）
def find_bfs(fs, start_path, pattern):
    start = fs._get_node_by_path(start_path)
    if not start:
        return []
    res = []
    queue = CustomQueue()
    queue.enqueue(start)
    while not queue.is_empty():
        node = queue.dequeue()
        if wildcard_match(pattern, node.name):
            res.append(node.name)
        if isinstance(node, Directory):
            queue.extend(node.children)
    return res

# DFS深度优先搜索（使用自定义栈，LIFO保证深度优先顺序）
def find_dfs(fs, start_path, pattern):
    start = fs._get_node_by_path(start_path)
    if not start:
        return []
    res = []
    stack = CustomStack()
    stack.push(start)
    while not stack.is_empty():
        node = stack.pop()
        if wildcard_match(pattern, node.name):
            res.append(node.name)
        if isinstance(node, Directory):
            # 反转子节点保证遍历顺序和原逻辑一致
            stack.extend(reversed(node.children))
    return res

# 查找重复文件名（使用自定义队列做BFS遍历）
def find_duplicates(fs, start_path="/"):
    start = fs._get_node_by_path(start_path)
    if not start:
        return []
    name_count = {}
    queue = CustomQueue()
    queue.enqueue(start)
    while not queue.is_empty():
        node = queue.dequeue()
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
