import sys
import os
# 自动添加项目根目录到Python路径，跨平台兼容，无需硬编码
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core import FileSystem, ShellNavigator
from src.model.permission import Permission
from src.utils import (
    save_fs_to_json, generate_random_fs, find_bfs, find_dfs,
    find_duplicates, load_fs_from_json, du, find_permission_issues,
    chmod_recursive, generate_random_fs_by_size
)


def demo_task1_disk_usage(fs):
    """任务1演示：磁盘使用分析（后序遍历）"""
    print("\n" + "=" * 60)
    print("任务1：磁盘使用分析 (du命令 - 后序遍历)")
    print("=" * 60)
    
    print("\n为什么使用后序遍历？")
    print("- 后序遍历遵循左-右-根顺序，必须先访问完所有子节点才能计算父节点大小")
    print("- 目录大小 = 所有子文件大小 + 所有子目录大小，必须先计算子目录")
    print("- 前序/中序遍历会在子目录大小计算完成前访问父节点，导致结果错误")
    print()
    
    result = du(fs, "/")
    print(f"{'路径':<45} {'大小(字节)':>12}")
    print("-" * 60)
    for path, size in result:
        print(f"{path:<45} {size:>12,}")


def demo_task2_find_duplicates(fs):
    """任务2演示：复制文件检测"""
    print("\n" + "=" * 60)
    print("任务2：复制文件检测")
    print("=" * 60)
    
    print("\n遍历方式：BFS广度优先遍历（队列实现）")
    print("数据结构：字典，key为(name, size)元组，value为文件路径列表")
    print("时间复杂度：O(n)，空间复杂度：O(n)")
    print()
    
    duplicates = find_duplicates(fs, "/")
    
    if duplicates:
        print(f"发现 {len(duplicates)} 组重复文件（同名且同大小）：")
        for i, group in enumerate(duplicates, 1):
            print(f"\n【第{i}组】名称: {group[0][1]}, 大小: {group[0][2]:,} 字节")
            for path, name, size in group:
                print(f"  - {path}")
    else:
        print("未发现重复文件")


def demo_task3_permission_audit(fs):
    """任务3演示：权限审计"""
    print("\n" + "=" * 60)
    print("任务3：权限审计")
    print("=" * 60)
    
    print("\n递归chmod遍历顺序问题：")
    print("- 适合前序遍历（先处理当前节点，再处理子节点）")
    print("- 权限修改是独立操作，顺序理论上不影响结果")
    print("- 但前序遍历先修改父目录权限保证可访问，更符合实际使用场景")
    print()
    
    # 先移除一些文件的写权限，制造权限问题
    print("1. 先移除docs目录下所有文件的写权限...")
    chmod_recursive(fs, "/home/user/docs", remove_permission=Permission.WRITE)
    
    # 查找可读但不可写的文件
    print("\n2. 查找所有'可读但不可写'的文件：")
    issues = find_permission_issues(
        fs, "/",
        required_perms={Permission.READ},
        forbidden_perms={Permission.WRITE}
    )
    
    for path, name, perms in issues:
        perm_str = ",".join([p.name for p in perms])
        print(f"  - {path}  权限: {perm_str}")
    
    # 演示递归chmod恢复权限
    print("\n3. 递归恢复所有文件的写权限...")
    chmod_recursive(fs, "/home/user/docs", add_permission=Permission.WRITE)
    print("权限已恢复")


def demo_basic_operations():
    """基础操作演示"""
    # 数据文件存放在项目根目录的data文件夹下
    json_full_path = os.path.join(BASE_DIR, "data", "filesystem.json")
    fs = FileSystem()
    fs.mkdir("/", "home")
    fs.mkdir("/home", "user")
    fs.touch("/home/user", "test.txt", 1024, "hello world")
    fs.touch("/home/user", "readme.txt", 2048)
    fs.mkdir("/home/user", "docs")
    fs.mkdir("/home/user", "pictures")
    fs.touch("/home/user/docs", "report1.pdf", 4096)
    fs.touch("/home/user/docs", "report2.pdf", 8192)
    fs.touch("/home/user/docs", "readme.txt", 2048)  # 同名同大小的重复文件
    fs.touch("/home/user/pictures", "photo1.jpg", 102400)
    
    print("=== 目录树结构 ===")
    print(fs.tree())
    print("=== ls /home/user ===", fs.ls("/home/user"))
    
    shell = ShellNavigator(fs)
    shell.cd("home")
    shell.cd("user")
    print("=== 当前路径 ===", shell.pwd())
    shell.cd_back()
    print("=== 返回后路径 ===", shell.pwd())
    
    print("\n=== BFS搜索 report* ===", find_bfs(fs, "/", "report*"))
    print("=== DFS搜索 report* ===", find_dfs(fs, "/", "report*"))
    
    return fs


if __name__ == "__main__":

    print("模拟文件系统 - part_2")

    
    # 基础操作演示
    fs = demo_basic_operations()
    
    # 任务1：磁盘使用分析
    demo_task1_disk_usage(fs)
    
    # 任务2：复制文件检测
    demo_task2_find_duplicates(fs)
    
    # 任务3：权限审计
    demo_task3_permission_audit(fs)
    
    # 随机文件系统演示
    print("\n" + "=" * 60)
    print("随机生成文件系统演示")
    print("=" * 60)
    random_fs = generate_random_fs(min_depth=3, min_nodes=50)
    all_nodes = find_bfs(random_fs, "/", "*")
    print(f"随机生成节点总数: {len(all_nodes)}")
    
    # 保存演示文件系统
    json_path = os.path.join(BASE_DIR, "data", "demo_fs.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    save_fs_to_json(fs, json_path)
    print(f"\n演示文件系统已保存到: {json_path}")
    
    print("\n" + "=" * 60)
    print("所有任务演示完成！")
    print("=" * 60)
    print("\n运行方式：")
    print("  - 启动GUI界面: python -m src.gui")
    print("  - 运行基准测试: python -m src.benchmark")
    print("  - 运行单元测试: python -m pytest tests/ -v")
