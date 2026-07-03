import sys
sys.path.append(r"D:\software\vscode\code")
import os
from mycode.part_1.file_system import FileSystem
from mycode.part_1.shell_navigator import ShellNavigator
from mycode.part_1.fs_utils import save_fs_to_json, generate_random_fs, find_bfs, find_dfs, find_duplicates, load_fs_from_json

if __name__ == "__main__":
    json_full_path = r"D:\software\vscode\code\mycode\part_1\filesystem.json"

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
    print(f"Actual file save path：{json_full_path}")