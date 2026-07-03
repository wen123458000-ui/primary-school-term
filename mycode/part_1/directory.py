from mycode.part_1.fs_node import FSNode

# 目录子类
class Directory(FSNode):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.children = []

    def get_size(self):
        total = 0
        for child in self.children:
            total += child.get_size()
        return total

    def child_count(self):
        count = 0
        for child in self.children:
            if isinstance(child, Directory):
                count += 1 + child.child_count()
            else:
                count += 1
        return count