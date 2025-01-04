import os
from collections import defaultdict

def count_yolo_classes(directory):
    # 创建一个字典来存储每个类别的计数
    class_counts = defaultdict(int)

    # 遍历目录下的所有文件
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                for line in file:
                    class_id = line.strip().split()[0]
                    class_counts[class_id] += 1

    # 打印每个类别的总数
    for class_id, count in class_counts.items():
        print(f"Class ID {class_id} has {count} occurrences.")

# 用法示例
if __name__ == "__main__":
    print('Train')
    count_yolo_classes('../data/labels/train')
    print('Test')
    count_yolo_classes('../data/labels/test')
    print('Le2i Test')
    count_yolo_classes('../data/test/Le2i/labels/')
