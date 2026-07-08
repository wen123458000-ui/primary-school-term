# 导入依赖
from src.model.directory import Directory
from src.data_structure import CustomStack

# 栈式终端导航器（使用自定义栈实现历史回退，LIFO符合导航逻辑）
class ShellNavigator:
    def __init__(self, fs):
        self.fs = fs
        self.current_dir = fs.root
        # 使用自定义栈存储导航历史，不再使用原生list
        self.history_stack = CustomStack()

    def cd(self, dir_name):
        for child in self.current_dir.children:
            if child.name == dir_name and isinstance(child, Directory):
                self.history_stack.push(self.current_dir)
                self.current_dir = child
                return True
        return False

    def cd_back(self):
        if self.history_stack.is_empty():
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
