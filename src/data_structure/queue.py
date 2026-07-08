# 自定义队列实现（FIFO先进先出，基于链表，不依赖任何第三方包）
class QueueNode:
    """队列节点，单链表结构"""
    def __init__(self, value):
        self.value = value
        self.next = None

class CustomQueue:
    def __init__(self):
        self.front = None  # 队首指针，出队操作
        self.rear = None   # 队尾指针，入队操作
        self._size = 0     # 队列元素个数

    def enqueue(self, val):
        """元素入队（添加到队尾）"""
        new_node = QueueNode(val)
        if self.is_empty():
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self._size += 1

    def dequeue(self):
        """元素出队（从队首移除并返回）"""
        if self.is_empty():
            raise IndexError("队列为空，无法执行出队操作")
        pop_node = self.front
        self.front = self.front.next
        self._size -= 1
        # 出队后队列为空，重置队尾指针
        if self.front is None:
            self.rear = None
        return pop_node.value

    def peek(self):
        """查看队首元素，不移除"""
        if self.is_empty():
            raise IndexError("队列为空，无法查看队首元素")
        return self.front.value

    def is_empty(self):
        """判断队列是否为空"""
        return self._size == 0

    def size(self):
        """返回队列元素个数"""
        return self._size

    def extend(self, iterable):
        """批量入队，支持可迭代对象"""
        for item in iterable:
            self.enqueue(item)
