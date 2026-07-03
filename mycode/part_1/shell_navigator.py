# 导入Directory类，解决未定义报错
from mycode.part_1.directory import Directory

# 栈式终端导航器
class ShellNavigator:
    def __init__(self, fs):
        self.fs = fs
        self.current_dir = fs.root
        self.history_stack = []

    def cd(self, dir_name):
        for child in self.current_dir.children:
            if child.name == dir_name and isinstance(child, Directory):
                self.history_stack.append(self.current_dir)
                self.current_dir = child
                return True
        return False

    def cd_back(self):
        if not self.history_stack:
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