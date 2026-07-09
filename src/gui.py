"""
任务5：图形界面 - 文件资源管理器
使用PyQt5构建
- 左侧：树状面板（可折叠目录）
- 右侧：文件详情面板
- 顶部：路径栏 + 搜索栏
- 支持导航(cd, cd_back)、创建/删除、搜索高亮
"""
import sys
import os

# 添加项目根目录到路径
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeView, QTableView, QLineEdit, QPushButton, QSplitter,
    QHeaderView, QMessageBox, QInputDialog, QToolBar, QAction,
    QStatusBar, QStyle, QFileIconProvider
)
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QVariant
from PyQt5.QtGui import QIcon, QColor, QBrush, QFont

from src.core import FileSystem, ShellNavigator
from src.model.directory import Directory
from src.model.file import File
from src.model.permission import Permission
from src.utils import find_bfs, find_dfs, _get_node_path


class FileSystemModel(QAbstractItemModel):
    """自定义文件系统树模型"""
    
    def __init__(self, fs, parent=None):
        super().__init__(parent)
        self.fs = fs
        self.root = fs.root
        self.highlighted_nodes = set()  # 搜索高亮的节点
    
    def set_highlighted(self, node_paths):
        """设置高亮节点"""
        self.highlighted_nodes = set(node_paths)
        self.layoutChanged.emit()
    
    def index(self, row, column, parent=QModelIndex()):
        """创建索引"""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        if not parent.isValid():
            parent_node = self.root
        else:
            parent_node = parent.internalPointer()
        
        if isinstance(parent_node, Directory) and row < len(parent_node.children):
            child_node = parent_node.children[row]
            return self.createIndex(row, column, child_node)
        return QModelIndex()
    
    def parent(self, index):
        """获取父索引"""
        if not index.isValid():
            return QModelIndex()
        
        child_node = index.internalPointer()
        parent_node = child_node.parent
        
        if parent_node is None or parent_node == self.root:
            return QModelIndex()
        
        # 找到父节点在其父节点children中的位置
        grandparent = parent_node.parent
        if grandparent is None:
            return QModelIndex()
        
        row = grandparent.children.index(parent_node)
        return self.createIndex(row, 0, parent_node)
    
    def rowCount(self, parent=QModelIndex()):
        """行数"""
        if parent.column() > 0:
            return 0
        
        if not parent.isValid():
            parent_node = self.root
        else:
            parent_node = parent.internalPointer()
        
        if isinstance(parent_node, Directory):
            return len(parent_node.children)
        return 0
    
    def columnCount(self, parent=QModelIndex()):
        """列数"""
        return 4  # 名称、大小、类型、权限
    
    def data(self, index, role=Qt.DisplayRole):
        """单元格数据"""
        if not index.isValid():
            return QVariant()
        
        node = index.internalPointer()
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:
                return node.name
            elif col == 1:
                if isinstance(node, File):
                    return f"{node.size_bytes:,} B"
                return ""
            elif col == 2:
                return "文件夹" if isinstance(node, Directory) else f"文件 ({node.extension})"
            elif col == 3:
                perms = []
                if Permission.READ in node.permissions:
                    perms.append("读")
                if Permission.WRITE in node.permissions:
                    perms.append("写")
                if Permission.EXECUTE in node.permissions:
                    perms.append("执行")
                return "".join(perms)
        
        elif role == Qt.BackgroundRole:
            # 搜索高亮
            node_path = _get_node_path(node)
            if node_path in self.highlighted_nodes:
                return QBrush(QColor(255, 255, 0, 100))  # 浅黄色高亮
        
        elif role == Qt.FontRole:
            if isinstance(node, Directory):
                font = QFont()
                font.setBold(True)
                return font
        
        elif role == Qt.DecorationRole and col == 0:
            # 图标
            style = QApplication.style()
            if isinstance(node, Directory):
                return style.standardIcon(QStyle.SP_DirIcon)
            else:
                return style.standardIcon(QStyle.SP_FileIcon)
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """表头"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = ["名称", "大小", "类型", "权限"]
            return headers[section]
        return QVariant()
    
    def flags(self, index):
        """标志"""
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class FileExplorer(QMainWindow):
    """文件资源管理器主窗口"""
    
    def __init__(self):
        super().__init__()
        self.fs = self._create_demo_fs()
        self.navigator = ShellNavigator(self.fs)
        self.init_ui()
    
    def _create_demo_fs(self):
        """创建演示文件系统"""
        fs = FileSystem()
        
        # 创建目录结构
        fs.mkdir("/", "home")
        fs.mkdir("/home", "user")
        fs.mkdir("/home/user", "documents")
        fs.mkdir("/home/user", "pictures")
        fs.mkdir("/home/user", "code")
        fs.mkdir("/home/user", "downloads")
        fs.mkdir("/home/user/documents", "reports")
        fs.mkdir("/home/user/code", "python")
        fs.mkdir("/home/user/code", "cpp")
        
        # 创建文件
        fs.touch("/home/user", "readme.txt", 1024, "欢迎使用文件系统模拟器")
        fs.touch("/home/user", "notes.md", 2048, "# 学习笔记")
        fs.touch("/home/user/documents", "report1.pdf", 15360)
        fs.touch("/home/user/documents", "report2.docx", 8192)
        fs.touch("/home/user/documents/reports", "annual.pdf", 102400)
        fs.touch("/home/user/pictures", "photo1.jpg", 204800)
        fs.touch("/home/user/pictures", "photo2.png", 307200)
        fs.touch("/home/user/code/python", "main.py", 4096, "print('Hello World')")
        fs.touch("/home/user/code/python", "utils.py", 8192)
        fs.touch("/home/user/code/cpp", "main.cpp", 2048)
        fs.touch("/home/user/downloads", "file1.zip", 512000)
        
        # 添加一些重复文件用于测试
        fs.touch("/home/user/downloads", "readme.txt", 1024)  # 同名同大小
        fs.touch("/home/user/documents", "notes.md", 2048)    # 同名同大小
        
        return fs
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("模拟文件系统 - 文件资源管理器")
        self.setGeometry(100, 100, 1000, 700)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # === 顶部工具栏 ===
        toolbar = QHBoxLayout()
        
        # 返回按钮
        self.back_btn = QPushButton("← 返回")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setFixedWidth(80)
        toolbar.addWidget(self.back_btn)
        
        # 根目录按钮
        self.root_btn = QPushButton("🏠 根目录")
        self.root_btn.clicked.connect(self.go_root)
        toolbar.addWidget(self.root_btn)
        
        toolbar.addSpacing(10)
        
        # 路径栏
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setText("/")
        self.path_edit.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        toolbar.addWidget(self.path_edit, stretch=1)
        
        toolbar.addSpacing(10)
        
        # 搜索栏
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 搜索文件 (支持通配符 *)...")
        self.search_edit.returnPressed.connect(self.do_search)
        toolbar.addWidget(self.search_edit, stretch=1)
        
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.do_search)
        toolbar.addWidget(self.search_btn)
        
        self.clear_search_btn = QPushButton("清除")
        self.clear_search_btn.clicked.connect(self.clear_search)
        toolbar.addWidget(self.clear_search_btn)
        
        main_layout.addLayout(toolbar)
        
        # === 操作按钮栏 ===
        action_bar = QHBoxLayout()
        
        self.new_dir_btn = QPushButton("📁 新建文件夹")
        self.new_dir_btn.clicked.connect(self.create_directory)
        action_bar.addWidget(self.new_dir_btn)
        
        self.new_file_btn = QPushButton("📄 新建文件")
        self.new_file_btn.clicked.connect(self.create_file)
        action_bar.addWidget(self.new_file_btn)
        
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.clicked.connect(self.delete_selected)
        action_bar.addWidget(self.delete_btn)
        
        action_bar.addStretch()
        
        self.du_btn = QPushButton("📊 磁盘使用分析")
        self.du_btn.clicked.connect(self.show_disk_usage)
        action_bar.addWidget(self.du_btn)
        
        self.dup_btn = QPushButton("🔍 查找重复文件")
        self.dup_btn.clicked.connect(self.show_duplicates)
        action_bar.addWidget(self.dup_btn)
        
        main_layout.addLayout(action_bar)
        
        # === 分割器：左侧树 + 右侧详情 ===
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧树视图
        self.tree_model = FileSystemModel(self.fs)
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setHeaderHidden(False)
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tree_view.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tree_view.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tree_view.doubleClicked.connect(self.on_tree_double_clicked)
        self.tree_view.clicked.connect(self.on_tree_clicked)
        self.tree_view.setColumnWidth(0, 250)
        splitter.addWidget(self.tree_view)
        
        # 右侧详情表格
        self.detail_table = QTableView()
        self.detail_table.setModel(self.tree_model)
        self.detail_table.doubleClicked.connect(self.on_tree_double_clicked)
        self.detail_table.clicked.connect(self.on_tree_clicked)
        self.detail_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        splitter.addWidget(self.detail_table)
        
        splitter.setSizes([400, 600])
        main_layout.addWidget(splitter, stretch=1)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.update_status()
        
        # 展开根节点
        self.tree_view.expandToDepth(1)
    
    def update_path_display(self):
        """更新路径显示"""
        self.path_edit.setText(self.navigator.pwd())
    
    def update_status(self):
        """更新状态栏"""
        current = self.navigator.current_dir
        file_count = sum(1 for c in current.children if isinstance(c, File))
        dir_count = sum(1 for c in current.children if isinstance(c, Directory))
        total_size = current.get_size()
        self.statusBar.showMessage(
            f"当前目录: {self.navigator.pwd()} | {dir_count} 个文件夹, {file_count} 个文件 | 总大小: {total_size:,} 字节"
        )
        self.update_path_display()
    
    def on_tree_double_clicked(self, index):
        """双击进入目录"""
        if not index.isValid():
            return
        node = index.internalPointer()
        if isinstance(node, Directory):
            if self.navigator.cd(node.name):
                self.update_status()
                # 展开该节点
                self.tree_view.expand(index)
    
    def on_tree_clicked(self, index):
        """单击选中"""
        pass
    
    def go_back(self):
        """返回上一级"""
        if self.navigator.cd_back():
            self.update_status()
        else:
            QMessageBox.information(self, "提示", "已经在根目录，无法返回")
    
    def go_root(self):
        """回到根目录"""
        self.navigator.cd_root()
        self.update_status()
    
    def do_search(self):
        """执行搜索"""
        pattern = self.search_edit.text().strip()
        if not pattern:
            return
        
        # 使用BFS搜索
        results_bfs = find_bfs(self.fs, "/", pattern)
        results_dfs = find_dfs(self.fs, "/", pattern)
        
        # 获取所有匹配节点的路径用于高亮
        from src.data_structure import CustomQueue
        from src.utils import wildcard_match
        
        matched_paths = []
        queue = CustomQueue()
        queue.enqueue(self.fs.root)
        
        while not queue.is_empty():
            node = queue.dequeue()
            if wildcard_match(pattern, node.name):
                matched_paths.append(_get_node_path(node))
            if isinstance(node, Directory):
                queue.extend(node.children)
        
        # 设置高亮
        self.tree_model.set_highlighted(matched_paths)
        
        # 展开所有节点显示高亮
        self.tree_view.expandAll()
        
        QMessageBox.information(
            self, "搜索结果",
            f"搜索模式: {pattern}\n"
            f"BFS找到: {len(results_bfs)} 个匹配\n"
            f"DFS找到: {len(results_dfs)} 个匹配\n\n"
            f"匹配项已在树中黄色高亮显示"
        )
    
    def clear_search(self):
        """清除搜索高亮"""
        self.search_edit.clear()
        self.tree_model.set_highlighted(set())
        self.tree_view.collapseAll()
        self.tree_view.expandToDepth(1)
    
    def create_directory(self):
        """新建文件夹"""
        name, ok = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称:")
        if ok and name:
            current_path = self.navigator.pwd()
            if self.fs.mkdir(current_path, name):
                self.tree_model.layoutChanged.emit()
                self.update_status()
                QMessageBox.information(self, "成功", f"文件夹 '{name}' 创建成功")
            else:
                QMessageBox.warning(self, "失败", f"创建文件夹失败，名称可能已存在")
    
    def create_file(self):
        """新建文件"""
        name, ok = QInputDialog.getText(self, "新建文件", "请输入文件名称:")
        if ok and name:
            size, ok2 = QInputDialog.getInt(self, "新建文件", "请输入文件大小(字节):", 1024, 0, 100000000)
            if ok2:
                current_path = self.navigator.pwd()
                if self.fs.touch(current_path, name, size):
                    self.tree_model.layoutChanged.emit()
                    self.update_status()
                    QMessageBox.information(self, "成功", f"文件 '{name}' 创建成功")
                else:
                    QMessageBox.warning(self, "失败", f"创建文件失败，名称可能已存在")
    
    def delete_selected(self):
        """删除选中项"""
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            QMessageBox.information(self, "提示", "请先选择要删除的项")
            return
        
        index = indexes[0]
        node = index.internalPointer()
        
        if node == self.fs.root:
            QMessageBox.warning(self, "错误", "不能删除根目录")
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 '{node.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            node_path = _get_node_path(node)
            if self.fs.rm(node_path):
                self.tree_model.layoutChanged.emit()
                self.update_status()
                QMessageBox.information(self, "成功", "删除成功")
    
    def show_disk_usage(self):
        """显示磁盘使用分析"""
        from src.utils import du
        
        result = du(self.fs, "/")
        
        msg = "磁盘使用分析 (按大小降序，后序遍历):\n\n"
        msg += f"{'路径':<40} {'大小(字节)':>12}\n"
        msg += "-" * 55 + "\n"
        
        for path, size in result[:15]:  # 显示前15个
            msg += f"{path:<40} {size:>12,}\n"
        
        if len(result) > 15:
            msg += f"\n... 还有 {len(result) - 15} 个目录"
        
        msg += "\n\n为什么使用后序遍历？\n"
        msg += "因为目录大小依赖于所有子节点大小，必须先计算子节点再计算父节点。"
        
        QMessageBox.information(self, "磁盘使用分析", msg)
    
    def show_duplicates(self):
        """显示重复文件"""
        from src.utils import find_duplicates
        
        duplicates = find_duplicates(self.fs, "/")
        
        if not duplicates:
            QMessageBox.information(self, "重复文件检测", "未发现重复文件")
            return
        
        msg = f"发现 {len(duplicates)} 组重复文件 (同名且同大小):\n\n"
        
        for i, group in enumerate(duplicates, 1):
            msg += f"【第{i}组】名称: {group[0][1]}, 大小: {group[0][2]:,} 字节\n"
            for path, name, size in group:
                msg += f"  - {path}\n"
            msg += "\n"
        
        QMessageBox.information(self, "重复文件检测", msg)


def main():
    """启动GUI"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    window = FileExplorer()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
