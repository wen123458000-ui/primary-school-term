from directory import Directory
from file import File
from datetime import datetime

# 文件系统核心操作
class FileSystem:
    def __init__(self):
        self.root = Directory("/")

    def _get_node_by_path(self, path):
        if path in ("/", ""):
            return self.root
        parts = path.strip("/").split("/")
        current = self.root
        for part in parts:
            found = False
            for child in current.children:
                if child.name == part and isinstance(child, Directory):
                    current = child
                    found = True
                    break
            if not found:
                return None
        return current

    def mkdir(self, parent_path, dir_name):
        parent = self._get_node_by_path(parent_path)
        if not parent or not isinstance(parent, Directory):
            return False
        for child in parent.children:
            if child.name == dir_name:
                return False
        parent.children.append(Directory(dir_name, parent))
        parent.modified_at = datetime.now()
        return True

    def touch(self, parent_path, file_name, size_bytes=0, content=""):
        parent = self._get_node_by_path(parent_path)
        if not parent or not isinstance(parent, Directory):
            return False
        for child in parent.children:
            if child.name == file_name:
                return False
        parent.children.append(File(file_name, size_bytes, content, parent))
        parent.modified_at = datetime.now()
        return True

    def rm(self, path):
        target = self._get_node_by_path(path)
        if not target or target == self.root:
            return False
        target.parent.children.remove(target)
        target.parent.modified_at = datetime.now()
        return True

    def mv(self, source_path, dest_path):
        source = self._get_node_by_path(source_path)
        dest = self._get_node_by_path(dest_path)
        if not source or not dest or not isinstance(dest, Directory) or source == self.root:
            return False
        source.parent.children.remove(source)
        source.parent = dest
        dest.children.append(source)
        dest.modified_at = datetime.now()
        source.modified_at = datetime.now()
        return True

    def ls(self, path="/"):
        node = self._get_node_by_path(path)
        if not node or not isinstance(node, Directory):
            return []
        return [child.name for child in node.children]

    def tree(self, path="/", indent=0):
        node = self._get_node_by_path(path)
        if not node:
            return ""
        res = "  " * indent + node.name + "\n"
        if isinstance(node, Directory):
            for child in node.children:
                child_path = f"{path.rstrip('/')}/{child.name}".replace("//", "/")
                if isinstance(child, Directory):
                    res += self.tree(child_path, indent + 1)
                else:
                    res += "  " * (indent + 1) + child.name + "\n"
        return res