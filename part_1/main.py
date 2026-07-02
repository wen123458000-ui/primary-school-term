import os
from file_system import FileSystem
from shell_navigator import ShellNavigator
from fs_utils import save_fs_to_json, generate_random_fs, find_bfs, find_dfs, find_duplicates, load_fs_from_json

if __name__ == "__main__":
    json_full_path = r"D:\software\vscode\code\mycode\part_1\filesystem.json"

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

    save_fs_to_json(fs, json_full_path)
    print(f"文件实际保存路径：{json_full_path}")