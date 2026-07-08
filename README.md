# 小学期模拟文件系统项目
## 一、项目介绍
本项目是一个Python实现的模拟内存文件系统，支持目录/文件创建、删除、移动、遍历搜索、命令行导航、JSON持久化等功能，所有核心数据结构均自主实现，未依赖第三方容器包。

## 二、项目目录结构
```
primary-school-term/
├── src/                      # 业务源代码根目录
│   ├── data_structure/       # 自定义数据结构实现（栈、队列）
│   │   ├── stack.py          # 自定义栈（LIFO）
│   │   ├── queue.py          # 自定义队列（FIFO）
│   │   └── __init__.py
│   ├── model/                # 数据模型层
│   │   ├── fs_node.py        # 文件系统节点抽象基类
│   │   ├── directory.py      # 目录节点类
│   │   ├── file.py           # 文件节点类
│   │   ├── permission.py     # 权限枚举类
│   │   └── __init__.py
│   ├── core/                 # 核心业务逻辑
│   │   ├── file_system.py    # 文件系统核心操作类
│   │   ├── shell_navigator.py# 终端导航器（路径切换、回退）
│   │   └── __init__.py
│   ├── utils/                # 工具函数层
│   │   ├── fs_utils.py       # 搜索、序列化、随机生成工具
│   │   └── __init__.py
│   └── main.py               # 程序入口
├── tests/                    # 单元测试目录（与src同级，所有成员可直接运行）
│   ├── test_directory.py
│   ├── test_file.py
│   ├── test_file_system.py
│   ├── test_fs_node.py
│   ├── test_fs_utils.py
│   ├── test_permission.py
│   └── test_shell_navigator.py
├── data/                     # 持久化数据存储目录
│   └── filesystem.json
└── README.md
```

## 三、自定义数据结构选型说明（核心要求）
本项目所有核心数据结构均基于链表自主实现，未使用`collections.deque`或Python原生list直接模拟栈/队列，选型依据如下：

### 1. 栈（CustomStack）适配导航历史功能
栈遵循**后进先出（LIFO）** 的特性，完美匹配文件系统导航的回退逻辑：
- 用户每进入一个子目录，就将当前目录压入栈顶；
- 用户执行`cd_back`返回上一级时，直接弹出栈顶元素（最近访问的目录）即可回到上一级路径；
- 时间复杂度：入栈、出栈均为O(1)，效率远高于list的insert(0)等操作；
- 若使用队列实现会打乱访问顺序，无法实现"返回上一步"的导航逻辑。

### 2. 队列（CustomQueue）适配BFS广度优先搜索
队列遵循**先进先出（FIFO）** 的特性，完美匹配BFS层级遍历的要求：
- BFS需要按目录层级逐层遍历文件树，先访问的目录节点先处理；
- 每处理一个目录节点，就将它的所有子节点加入队尾，保证同层级节点按顺序遍历；
- 时间复杂度：入队、出队均为O(1)，避免了list.pop(0)的O(n)时间开销；
- 若使用栈实现会变成深度优先搜索（DFS），无法保证按层级遍历的顺序。

## 四、运行方式
1. 克隆项目到本地：
```bash
git clone https://github.com/wen123458000-ui/primary-school-term.git
cd primary-school-term
```
2. 运行主程序：
```bash
python src/main.py
```
> 注意：项目已移除所有硬编码Windows绝对路径，采用跨平台相对路径，Windows/Mac/Linux系统均可直接运行，无需修改任何路径配置。

## 五、测试运行
所有测试文件统一放在根目录`tests`文件夹，所有成员拉取代码后可直接运行所有单元测试：
```bash
# 安装pytest（如未安装）
pip install pytest
# 运行全部测试
python -m pytest tests/ -v
```
所有测试代码注释清晰，无隐藏逻辑，保证所有成员可阅读、可运行、可调试。

## 六、团队分工与协作规范
### 1. Part2任务分工
- 第二部分功能模块由团队成员每人认领一个独立模块；
- 模块认领者为该模块第10天的专属负责人，负责代码讲解、Bug修复、功能维护；
- 每周初召开同步会，汇报各自开发进度、当前分支完成情况、遇到的问题。

### 2. Git协作规范（避免多版本冲突）
所有团队成员共用本远程仓库，禁止私自创建独立仓库，严格遵循以下提交流程：
```bash
# 1. 开发前先拉取主分支最新代码
git checkout main
git pull origin main

# 2. 创建个人功能分支开发（禁止直接在main分支提交代码）
git checkout -b feature/你的功能名  # 例如feature/file-copy、feature/permission-check

# 3. 小粒度频繁提交，单次提交只改一个功能点，提交信息清晰
git add .
git commit -m "feat: 实现文件复制功能"
git commit -m "fix: 修复BFS搜索漏节点问题"

# 4. 推送个人分支到远程，提交PR合并到main分支
git push origin feature/你的功能名
```
> 要求：禁止一次性提交大量代码、禁止长时间不推送本地代码，保证提交记录清晰可追溯，避免多人开发出现代码冲突。

## 七、跨平台兼容性说明
- 所有路径均采用`os.path`拼接的相对路径，无任何硬编码Windows绝对路径；
- 新克隆的仓库可直接在任意系统运行，无需配置Python路径或修改文件路径；
- 持久化文件统一存放在项目根目录`data/`文件夹下，不会写入系统其他目录。
