import json
import random
import re
import time
from datetime import datetime
from collections import defaultdict
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


# ==================== 任务1：磁盘使用分析（后序遍历） ====================
def _get_node_path(node):
    """获取节点的完整路径"""
    path_parts = []
    current = node
    while current.parent is not None:
        path_parts.insert(0, current.name)
        current = current.parent
    return "/" + "/".join(path_parts) if path_parts else "/"


def du(fs, start_path="/"):
    """
    磁盘使用分析命令 - 使用后序遍历
    报告每个子目录的总大小，并按从大到小排序
    
    为什么使用后序遍历？
    - 后序遍历遵循左-右-根顺序，必须先访问完所有子节点才能计算父节点大小
    - 目录大小 = 所有子文件大小 + 所有子目录大小，因此必须先计算子目录大小
    - 如果使用前序/中序遍历，会在子目录大小计算完成前就访问父节点，导致结果错误
    
    返回: [(path, size), ...] 按size降序排列
    """
    start = fs._get_node_by_path(start_path)
    if not start or not isinstance(start, Directory):
        return []
    
    result = []
    
    def post_order_traverse(node):
        """后序遍历：先处理所有子节点，再处理当前节点"""
        total_size = 0
        # 先递归处理所有子节点（左-右）
        for child in node.children:
            if isinstance(child, Directory):
                child_size = post_order_traverse(child)
                total_size += child_size
            else:
                total_size += child.get_size()
        
        # 最后处理当前节点（根）- 记录目录大小
        if isinstance(node, Directory):
            node_path = _get_node_path(node)
            result.append((node_path, total_size))
        
        return total_size
    
    # 执行后序遍历
    post_order_traverse(start)
    
    # 按大小从大到小排序
    result.sort(key=lambda x: x[1], reverse=True)
    return result


# ==================== 任务2：复制文件检测 ====================
def find_duplicates(fs, start_path="/"):
    """
    查找文件系统中所有重复文件（同名且同大小），按（名称、大小）成对返回
    
    遍历方式：BFS广度优先遍历（队列实现），确保完整扫描所有节点
    数据结构：使用字典分组，key为(name, size)元组，value为文件路径列表
    时间复杂度：O(n) - n为节点总数，每个节点访问一次
    空间复杂度：O(n) - 最坏情况所有文件都唯一，字典存储n个条目
    
    返回: [[(path1, name, size), (path2, name, size)], ...] 成对的重复文件列表
    """
    start = fs._get_node_by_path(start_path)
    if not start:
        return []
    
    # 使用字典按(名称, 大小)分组
    file_groups = defaultdict(list)
    
    # BFS遍历所有节点
    queue = CustomQueue()
    queue.enqueue(start)
    
    while not queue.is_empty():
        node = queue.dequeue()
        
        # 只对文件进行重复检测（目录不参与）
        if isinstance(node, File):
            key = (node.name, node.size_bytes)
            file_groups[key].append((_get_node_path(node), node.name, node.size_bytes))
        
        if isinstance(node, Directory):
            queue.extend(node.children)
    
    # 筛选出有重复的组（数量>=2）
    duplicates = []
    for (name, size), files in file_groups.items():
        if len(files) >= 2:
            duplicates.append(files)
    
    return duplicates


# ==================== 任务3：权限审计 ====================
def find_permission_issues(fs, start_path="/", required_perms=None, forbidden_perms=None):
    """
    查找存在特定权限缺失情况的文件或目录
    例如：查找所有可读但不可写的文件
    
    遍历方式：带过滤条件的完整树遍历（BFS）
    """
    start = fs._get_node_by_path(start_path)
    if not start:
        return []
    
    if required_perms is None:
        required_perms = {Permission.READ}
    if forbidden_perms is None:
        forbidden_perms = {Permission.WRITE}
    
    result = []
    queue = CustomQueue()
    queue.enqueue(start)
    
    while not queue.is_empty():
        node = queue.dequeue()
        
        # 检查权限：拥有所有required_perms，且不包含任何forbidden_perms
        has_required = required_perms.issubset(node.permissions)
        has_forbidden = any(p in node.permissions for p in forbidden_perms)
        
        if has_required and not has_forbidden:
            result.append((_get_node_path(node), node.name, node.permissions.copy()))
        
        if isinstance(node, Directory):
            queue.extend(node.children)
    
    return result


def chmod_recursive(fs, path, add_permission=None, remove_permission=None):
    """
    递归修改节点及其所有后代的权限
    
    递归chmod适合哪种遍历顺序？顺序重要吗？
    - 适合前序遍历（先处理当前节点，再递归处理子节点）
    - 顺序不重要：因为权限修改是独立操作，不依赖子节点的计算结果
    - 但通常使用前序遍历，先修改父目录权限保证可访问，再修改子节点
    
    参数:
        path: 起始路径
        add_permission: 要添加的权限（Permission枚举）或权限集合
        remove_permission: 要移除的权限（Permission枚举）或权限集合
    """
    start = fs._get_node_by_path(path)
    if not start:
        return False
    
    # 标准化为集合
    if add_permission is None:
        add_set = set()
    elif isinstance(add_permission, Permission):
        add_set = {add_permission}
    else:
        add_set = set(add_permission)
    
    if remove_permission is None:
        remove_set = set()
    elif isinstance(remove_permission, Permission):
        remove_set = {remove_permission}
    else:
        remove_set = set(remove_permission)
    
    # 使用DFS栈进行前序遍历
    stack = CustomStack()
    stack.push(start)
    
    while not stack.is_empty():
        node = stack.pop()
        
        # 修改当前节点权限（前序：先处理当前节点）
        node.permissions.update(add_set)
        node.permissions.difference_update(remove_set)
        node.modified_at = datetime.now()
        
        # 子节点入栈（反序保证顺序一致）
        if isinstance(node, Directory):
            stack.extend(reversed(node.children))
    
    return True


# ==================== 任务4：基准测试辅助函数 ====================
def generate_random_fs_by_size(target_nodes, wide_shallow=False):
    """
    生成指定节点数的文件系统
    wide_shallow=True: 宽浅型树（分支因子大，深度小）
    wide_shallow=False: 窄深型树（分支因子小，深度大）
    """
    fs = FileSystem()
    dir_names = ["docs", "images", "code", "data", "reports", "src", "test", "bin", "lib", "config",
                 "assets", "resources", "utils", "models", "views", "controllers", "logs", "temp"]
    file_names = ["report", "data", "log", "config", "readme", "main", "utils", "test", "output", 
                  "input", "index", "app", "helper", "constant", "settings", "error", "debug"]
    extensions = [".txt", ".py", ".json", ".csv", ".md", ".jpg", ".png", ".log", ".xml", ".html", ".css", ".js"]
    
    node_count = 1
    current_dirs = [("/", fs.root)]
    
    # 宽浅型：分支因子大；窄深型：分支因子小
    if wide_shallow:
        min_branch, max_branch = 5, 10
    else:
        min_branch, max_branch = 2, 3
    
    while node_count < target_nodes and current_dirs:
        next_dirs = []
        for path, dir_node in current_dirs:
            if node_count >= target_nodes:
                break
            # 根据剩余节点数动态调整分支数
            remaining = target_nodes - node_count
            branch = min(random.randint(min_branch, max_branch), remaining)
            for _ in range(branch):
                if node_count >= target_nodes:
                    break
                # 宽浅型：更多文件；窄深型：更多目录
                dir_prob = 0.3 if wide_shallow else 0.5
                if random.random() < dir_prob and remaining > 1:
                    name = random.choice(dir_names) + str(random.randint(1, 999))
                    if fs.mkdir(path, name):
                        node_count += 1
                        new_path = f"{path.rstrip('/')}/{name}".replace("//", "/")
                        next_dirs.append((new_path, dir_node.children[-1]))
                else:
                    name = random.choice(file_names) + str(random.randint(1, 999)) + random.choice(extensions)
                    size = random.randint(10, 102400)
                    if fs.touch(path, name, size):
                        node_count += 1
        # 如果没有生成新目录但还需要节点，强制在当前目录创建文件
        if not next_dirs and node_count < target_nodes:
            for path, dir_node in current_dirs:
                while node_count < target_nodes:
                    name = random.choice(file_names) + str(random.randint(1, 9999)) + random.choice(extensions)
                    size = random.randint(10, 102400)
                    if fs.touch(path, name, size):
                        node_count += 1
                    else:
                        break
        current_dirs = next_dirs
    
    return fs


def benchmark_search(fs, search_pattern, near_root=False):
    """BFS vs DFS搜索性能测试"""
    # BFS计时
    start_time = time.perf_counter()
    if near_root:
        bfs_result = find_bfs(fs, "/", search_pattern)
    else:
        bfs_result = find_bfs(fs, "/", search_pattern)
    bfs_time = time.perf_counter() - start_time
    
    # DFS计时
    start_time = time.perf_counter()
    dfs_result = find_dfs(fs, "/", search_pattern)
    dfs_time = time.perf_counter() - start_time
    
    return bfs_time, dfs_time, len(bfs_result)


def benchmark_total_size(fs):
    """total_size()计算性能测试"""
    start_time = time.perf_counter()
    root_size = fs.root.get_size()
    calc_time = time.perf_counter() - start_time
    return calc_time, root_size


def benchmark_find_duplicates(fs):
    """find_duplicates()性能测试"""
    start_time = time.perf_counter()
    dups = find_duplicates(fs, "/")
    calc_time = time.perf_counter() - start_time
    return calc_time, len(dups)
