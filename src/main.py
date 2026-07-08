import sys
import os

# 自动添加项目根目录到Python路径，跨平台兼容，无需硬编码
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core import FileSystem, ShellNavigator
from src.utils import save_fs_to_json, generate_random_fs, find_bfs, find_dfs, find_duplicates, load_fs_from_json

if __name__ == "__main__":
    # 数据文件存放在项目根目录的data文件夹下，跨平台相对路径，无硬编码
    json_full_path = os.path.join(BASE_DIR, "data", "filesystem.json")

    fs = FileSystem()
    fs.mkdir("/", "home")
    fs.mkdir("/home", "user")
    fs.touch("/home/user", "test.txt", 1024, "hello world")
    fs.touch("/home/user", "report1.docx", 2048)
    fs.mkdir("/home/user", "docs")
    fs.touch("/home/user/docs", "report2.pdf", 4096)

    print("=== Directory tree ===")
    print(fs.tree())
    print("=== ls /home/user ===", fs.ls("/home/user"))

    shell = ShellNavigator(fs)
    shell.cd("home")
    shell.cd("user")
    print("=== Current path ===", shell.pwd())
    shell.cd_back()
    print("=== Fallback path ===", shell.pwd())

    print("=== BFS Search report* ===", find_bfs(fs, "/", "report*"))
    print("=== DFS Search report* ===", find_dfs(fs, "/", "report*"))

    print("\n=== Randomly generate a file tree ===")
    random_fs = generate_random_fs()
    all_nodes = find_bfs(random_fs, "/", "*")
    print("Total number of nodes:", len(all_nodes))
    print(random_fs.tree())

    save_fs_to_json(fs, json_full_path)
    print(f"File saved to: {json_full_path}")
