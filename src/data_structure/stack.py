# 自定义栈实现（LIFO后进先出，基于链表，不依赖任何第三方包）
class StackNode:
    """栈节点，单链表结构"""
    def __init__(self, value):
        self.value = value
        self.next = None

class CustomStack:
    def __init__(self):
        self.top = None    # 栈顶指针，入栈出栈操作
        self._size = 0     # 栈元素个数

    def push(self, val):
        """元素入栈（压入栈顶）"""
        new_node = StackNode(val)
        new_node.next = self.top
        self.top = new_node
        self._size += 1

    def pop(self):
        """元素出栈（从栈顶移除并返回）"""
        if self.is_empty():
            raise IndexError("栈为空，无法执行出栈操作")
        pop_node = self.top
        self.top = self.top.next
        self._size -= 1
        return pop_node.value

    def peek(self):
        """查看栈顶元素，不移除"""
        if self.is_empty():
            raise IndexError("栈为空，无法查看栈顶元素")
        return self.top.value

    def is_empty(self):
        """判断栈是否为空"""
        return self._size == 0

    def size(self):
        """返回栈元素个数"""
        return self._size

    def clear(self):
        """清空栈"""
        self.top = None
        self._size = 0

    def extend(self, iterable):
        """批量入栈，支持可迭代对象"""
        for item in iterable:
            self.push(item)
