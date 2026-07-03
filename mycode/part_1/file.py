from mycode.part_1.fs_node import FSNode

# 文件子类
class File(FSNode):
    def __init__(self, name, size_bytes, content="", parent=None):
        super().__init__(name, parent)
        self.size_bytes = size_bytes
        self.content = content
        self.extension = name.split(".")[-1] if "." in name else ""

    def get_size(self):
        return self.size_bytes