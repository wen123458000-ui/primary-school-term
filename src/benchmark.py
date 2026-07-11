"""
任务4：实验性基准测试
生成不同大小的文件系统，测试BFS/DFS搜索、total_size计算、find_duplicates性能
并绘制结果图表
"""
import sys
import os
import random

# 添加项目根目录到路径
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import numpy as np

from src.core import FileSystem
from src.utils import (
    generate_random_fs_by_size,
    benchmark_search,
    benchmark_total_size,
    benchmark_find_duplicates,
    find_bfs,
    find_dfs
)


def run_benchmarks():
    """运行所有基准测试"""
    node_sizes = [50, 200, 1000, 5000, 20000]
    
    results = {
        'sizes': node_sizes,
        'bfs_wide': [],
        'dfs_wide': [],
        'bfs_deep': [],
        'dfs_deep': [],
        'size_wide': [],
        'size_deep': [],
        'dup_wide': [],
        'dup_deep': []
    }
    
    print("=" * 60)
    print("任务4：实验性基准测试")
    print("=" * 60)
    
    for n in node_sizes:
        print(f"\n--- 测试 N={n} 节点 ---")
        
        # 宽浅型树
        print(f"  生成宽浅型文件系统 (分支因子5-10)...")
        fs_wide = generate_random_fs_by_size(n, wide_shallow=True)
        actual_nodes_wide = len(find_bfs(fs_wide, "/", "*"))
        print(f"  实际节点数: {actual_nodes_wide}")
        
        # 窄深型树
        print(f"  生成窄深型文件系统 (分支因子2-3)...")
        fs_deep = generate_random_fs_by_size(n, wide_shallow=False)
        actual_nodes_deep = len(find_bfs(fs_deep, "/", "*"))
        print(f"  实际节点数: {actual_nodes_deep}")
        
        # BFS vs DFS 搜索测试（搜索叶子节点附近的文件）
        search_pattern = "*.log"  # 通常在深层目录
        
        bfs_t_w, dfs_t_w, matches_w = benchmark_search(fs_wide, search_pattern)
        bfs_t_d, dfs_t_d, matches_d = benchmark_search(fs_deep, search_pattern)
        
        results['bfs_wide'].append(bfs_t_w * 1000)  # 转换为毫秒
        results['dfs_wide'].append(dfs_t_w * 1000)
        results['bfs_deep'].append(bfs_t_d * 1000)
        results['dfs_deep'].append(dfs_t_d * 1000)
        
        print(f"  BFS(宽浅): {bfs_t_w*1000:.3f}ms, DFS(宽浅): {dfs_t_w*1000:.3f}ms, 匹配: {matches_w}")
        print(f"  BFS(窄深): {bfs_t_d*1000:.3f}ms, DFS(窄深): {dfs_t_d*1000:.3f}ms, 匹配: {matches_d}")
        
        # total_size 计算测试
        size_t_w, total_w = benchmark_total_size(fs_wide)
        size_t_d, total_d = benchmark_total_size(fs_deep)
        
        results['size_wide'].append(size_t_w * 1000)
        results['size_deep'].append(size_t_d * 1000)
        
        print(f"  total_size(宽浅): {size_t_w*1000:.3f}ms, 总大小: {total_w} bytes")
        print(f"  total_size(窄深): {size_t_d*1000:.3f}ms, 总大小: {total_d} bytes")
        
        # find_duplicates 测试
        dup_t_w, dup_count_w = benchmark_find_duplicates(fs_wide)
        dup_t_d, dup_count_d = benchmark_find_duplicates(fs_deep)
        
        results['dup_wide'].append(dup_t_w * 1000)
        results['dup_deep'].append(dup_t_d * 1000)
        
        print(f"  find_duplicates(宽浅): {dup_t_w*1000:.3f}ms, 重复组数: {dup_count_w}")
        print(f"  find_duplicates(窄深): {dup_t_d*1000:.3f}ms, 重复组数: {dup_count_d}")
    
    return results


def plot_results(results):
    """绘制基准测试结果图表"""
    sizes = results['sizes']
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('文件系统算法基准测试结果', fontsize=16, fontweight='bold')
    
    # 图1: BFS vs DFS 搜索性能对比
    ax1 = axes[0, 0]
    x = np.arange(len(sizes))
    width = 0.2
    
    ax1.bar(x - 1.5*width, results['bfs_wide'], width, label='BFS (Wide and shallow type)', color='#3498db', alpha=0.8)
    ax1.bar(x - 0.5*width, results['dfs_wide'], width, label='DFS (Wide and shallow type)', color='#e74c3c', alpha=0.8)
    ax1.bar(x + 0.5*width, results['bfs_deep'], width, label='BFS (Narrow and deep type)', color='#2ecc71', alpha=0.8)
    ax1.bar(x + 1.5*width, results['dfs_deep'], width, label='DFS (Narrow and deep type)', color='#f39c12', alpha=0.8)
    
    ax1.set_xlabel('Number of nodes')
    ax1.set_ylabel('Time (ms)')
    ax1.set_title('BFS vs DFS Search Performance Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(sizes)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 图2: total_size() 递归计算性能
    ax2 = axes[0, 1]
    ax2.plot(sizes, results['size_wide'], 'o-', label='Wide and shallow tree', linewidth=2, markersize=8, color='#3498db')
    ax2.plot(sizes, results['size_deep'], 's-', label='Narrow and deep tree', linewidth=2, markersize=8, color='#e74c3c')
    ax2.set_xlabel('Number of nodes')
    ax2.set_ylabel('Time (ms)')
    ax2.set_title('total_size() Recursive computation performance')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 图3: find_duplicates() 性能
    ax3 = axes[1, 0]
    ax3.plot(sizes, results['dup_wide'], 'o-', label='Wide and shallow tree', linewidth=2, markersize=8, color='#3498db')
    ax3.plot(sizes, results['dup_deep'], 's-', label='Narrow and deep tree', linewidth=2, markersize=8, color='#e74c3c')
    ax3.set_xlabel('Number of nodes')
    ax3.set_ylabel('Time (ms)')
    ax3.set_title('find_duplicates() Duplicate detection performance')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 图4: BFS/DFS 性能比
    ax4 = axes[1, 1]
    ratio_wide = [b/d if d > 0 else 1 for b, d in zip(results['bfs_wide'], results['dfs_wide'])]
    ratio_deep = [b/d if d > 0 else 1 for b, d in zip(results['bfs_deep'], results['dfs_deep'])]
    
    ax4.axhline(y=1.0, color='gray', linestyle='--', alpha=0.7, label='Performance equivalence line')
    ax4.plot(sizes, ratio_wide, 'o-', label='BFS/DFS Time Ratio (Wide and shallow type)', linewidth=2, markersize=8, color='#9b59b6')
    ax4.plot(sizes, ratio_deep, 's-', label='BFS/DFS Time Ratio (Narrow and deep type)', linewidth=2, markersize=8, color='#1abc9c')
    ax4.fill_between(sizes, 1, ratio_wide, alpha=0.2, color='#9b59b6')
    ax4.set_xlabel('Number of nodes')
    ax4.set_ylabel('BFS Time / DFS Time')
    ax4.set_title('BFS vs DFS Relative Performance (>1 means DFS is faster, <1 means BFS is faster)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    output_path = os.path.join(BASE_DIR, "data", "benchmark_results.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n图表已保存到: {output_path}")
    
    return output_path


def print_analysis():
    """打印结果分析"""
    print("\n" + "=" * 60)
    print("结果分析与结论")
    print("=" * 60)
    print("""
1. BFS vs DFS 在根节点附近 vs 叶子节点附近文件搜索:
   - 根节点附近文件: BFS通常更快，因为BFS按层遍历，先访问浅层节点
   - 叶子节点附近文件: DFS在窄深型树上可能更快到达深层
   - 但在实际测试中，由于需要完整遍历，两者差异不大

2. 树形状对性能的影响 (宽浅 vs 窄深):
   - 宽浅型树: BFS和DFS性能接近，因为分支多但深度小
   - 窄深型树: DFS可能在深层搜索有优势，但递归开销可能更大
   - 对于total_size()递归计算，窄深型树递归深度大，但Python递归深度有限制
   
3. 时间复杂度分析:
   - BFS/DFS搜索: O(n)，每个节点访问一次
   - total_size(): O(n)，后序遍历计算每个节点大小
   - find_duplicates(): O(n)，BFS遍历+哈希表分组
   
4. 空间复杂度:
   - BFS: O(w)，w为树的最大宽度（队列大小）
   - DFS: O(d)，d为树的最大深度（栈大小）
   - 宽浅型树BFS空间开销大，窄深型树DFS递归栈空间开销大
    """)


if __name__ == "__main__":
    random.seed(42)  # 固定随机种子保证可复现
    results = run_benchmarks()
    plot_results(results)
    print_analysis()
