import os
import shutil
from xml.etree import ElementTree
import random
import cv2


def restart():
    if os.path.exists('./data/images'):
        shutil.rmtree('./data/images')
    if os.path.exists('./data/labels'):
        shutil.rmtree('./data/labels')
    if os.path.exists('./data/test'):
        shutil.rmtree('./data/test')
    os.makedirs('./data/test', exist_ok=True)


# 将xml数据转化为yolo数据
def convert_xml_to_yolo(xml_file, img_width, img_height):
    tree = ElementTree.parse(xml_file)
    root = tree.getroot()
    objects = root.findall('object')
    yolo_data = []
    for obj in objects:
        class_id = 1 if obj.find('name').text == 'fall' else 0
        bndbox = obj.find('bndbox')
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)

        x_center = ((xmin + xmax) / 2) / img_width
        y_center = ((ymin + ymax) / 2) / img_height
        width = (xmax - xmin) / img_width
        height = (ymax - ymin) / img_height

        yolo_data.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

    return yolo_data


def create_pp_fall(source_dir, target_dir_images, target_dir_labels):
    random.seed(42)  # 设置随机种子以保证结果的可重复性

    source_annotations = os.path.join(source_dir, "Annotations")
    source_images = os.path.join(source_dir, "JPEGImages")

    target_train_images = os.path.join(target_dir_images, "train")
    target_train_labels = os.path.join(target_dir_labels, "train")

    os.makedirs(target_train_images, exist_ok=True)
    os.makedirs(target_train_labels, exist_ok=True)

    # 获取所有XML文件名
    all_files = os.listdir(source_annotations)

    def process_file(filename, img_dir, label_dir):
        xml_path = os.path.join(source_annotations, filename)
        tree = ElementTree.parse(xml_path)
        root = tree.getroot()
        img_name = root.find('filename').text
        img_path = os.path.join(source_images, img_name)
        img_width = int(root.find('size/width').text)
        img_height = int(root.find('size/height').text)

        # 提取编号并格式化为四位数
        number = img_name.split('_')[1].split('.')[0]  # 提取数字部分
        formatted_number = f"{int(number):04d}"  # 格式化为四位数
        new_img_name = f"PPF_{formatted_number}.jpg"  # 生成新的文件名

        # 复制图片到新位置
        new_img_path = os.path.join(img_dir, new_img_name)
        shutil.copy(img_path, new_img_path)

        # 转换标签数据为YOLO格式
        yolo_data = convert_xml_to_yolo(xml_path, img_width, img_height)
        new_label_name = f"PPF_{formatted_number}.txt"  # 标签文件的新名称
        label_path = os.path.join(label_dir, new_label_name)
        with open(label_path, 'w') as file:
            file.write("\n".join(yolo_data))

    # 将所有文件都处理为训练集
    for filename in all_files:
        process_file(filename, target_train_images, target_train_labels)

    print('[Create_data] Create PP_Fall Done!')



def create_fdd(source_dir, target_dir_images, target_dir_labels):
    # 分别处理train和val子文件夹
    for folder in ['train', 'test']:
        source_images = os.path.join(source_dir, 'images', folder)
        source_labels = os.path.join(source_dir, 'labels', folder)

        target_images = os.path.join(target_dir_images, folder)
        target_labels = os.path.join(target_dir_labels, folder)

        # 创建目标目录
        os.makedirs(target_images, exist_ok=True)
        os.makedirs(target_labels, exist_ok=True)

        # 复制图片文件并更改文件名
        for img_file in os.listdir(source_images):
            # 获取文件名中的后三位编号
            num_suffix = img_file[-7:-4]
            new_img_name = f'FDD_{num_suffix}.jpg' if img_file.endswith('.jpg') else f'FDD_{num_suffix}.png'
            shutil.copy(os.path.join(source_images, img_file), os.path.join(target_images, new_img_name))

        # 修改标签文件并复制，同时更改文件名
        for label_file in os.listdir(source_labels):
            with open(os.path.join(source_labels, label_file), 'r') as file:
                lines = file.readlines()

            # 处理每一行的标签
            modified_labels = []
            for line in lines:
                parts = line.strip().split()
                class_id = int(parts[0])
                # 映射第一位数字：0 -> 1，其他 -> 0
                if class_id == 0:
                    parts[0] = '1'
                else:
                    parts[0] = '0'
                modified_labels.append(' '.join(parts))

            # 生成新文件名并写入
            num_suffix = label_file[-7:-4]
            new_label_name = f'FDD_{num_suffix}.txt'
            with open(os.path.join(target_labels, new_label_name), 'w') as file:
                file.write("\n".join(modified_labels))

    print('[Create_data] Enhanced Process FDD Data Done!')


# def create_le2i(source_dir, target_dir_images, target_dir_labels):
#     # 定义需要处理的文件夹名称和目标目录
#     folders = ['Coffee_room_01', 'Home_01', 'Coffee_room_02', 'Home_02']
#     train_folders = ['Coffee_room_01', 'Home_01']
#     test_folders = ['Coffee_room_02', 'Home_02']
#
#     for folder in folders:
#         print(f"[Create_data] Processing Le2i_{folder}...", end='')
#         source_annotation = os.path.join(source_dir, folder, folder, 'Annotation_files')
#         source_videos = os.path.join(source_dir, folder, folder, 'Videos')
#
#         # 确定当前文件夹是训练集还是测试集
#         if folder in train_folders:
#             target_images = os.path.join(target_dir_images, 'train')
#             target_labels = os.path.join(target_dir_labels, 'train')
#         else:
#             target_images = os.path.join('.', 'data', 'test', 'Le2i', 'images', 'test')
#             target_labels = os.path.join('.', 'data', 'test', 'Le2i', 'labels', 'test')
#             os.makedirs(target_images, exist_ok=True)
#             os.makedirs(target_labels, exist_ok=True)
#
#         # 确保目标目录存在
#         os.makedirs(target_images, exist_ok=True)
#         os.makedirs(target_labels, exist_ok=True)
#
#         # 处理视频和标注文件
#         for video_file in os.listdir(source_videos):
#             if video_file.endswith('.avi'):
#                 video_path = os.path.join(source_videos, video_file)
#                 # 获取视频文件名中的序号
#                 video_index = video_file.split(' ')[-1].split('.')[0]
#
#                 # 读取对应的标注文件
#                 annotation_file = video_file.replace('.avi', '.txt')
#                 annotation_path = os.path.join(source_annotation, annotation_file)
#                 with open(annotation_path, 'r') as file:
#                     lines = file.readlines()
#
#                 try:
#                     if len(lines[0])<8:
#                         fall_start, fall_end = int(lines[0].strip()), int(lines[1].strip())
#                     else:
#                         continue
#                 except:
#                     continue
#
#                 # 开始处理视频文件
#                 temp_num_safe = 0
#                 temp_num_fall = 0
#                 cap = cv2.VideoCapture(video_path)
#                 frame_count = 0
#                 while True:
#                     ret, frame = cap.read()
#                     if not ret:
#                         break
#                     frame_count += 1
#
#                     # 标注文件的第一部分完成，开始写标注
#                     label_line = lines[frame_count + 1].strip() if frame_count + 1 < len(lines) else "0,0,0,0,0,0"
#                     parts = label_line.split(',')
#                     class_id = 1 if frame_count >= fall_start else 0
#                     if class_id == 0:
#                         if temp_num_safe > 0:
#                             temp_num_safe -= 1
#                             continue
#                         else:
#                             temp_num_safe += 4
#                     elif class_id == 1:
#                         if temp_num_fall > 0:
#                             temp_num_fall -= 1
#                             continue
#                         else:
#                             temp_num_fall += 3
#                     try:
#                         x_min, y_min, x_max, y_max = map(int, parts[2:])
#                         if (x_min + y_min) > 1:
#                             # 计算YOLO格式的中心坐标和宽高
#                             x_center = (x_min + x_max) / 2 / frame.shape[1]
#                             y_center = (y_min + y_max) / 2 / frame.shape[0]
#                             width = (x_max - x_min) / frame.shape[1]
#                             height = (y_max - y_min) / frame.shape[0]
#                             label_content = f"{class_id} {x_center} {y_center} {width} {height}"
#                         else:
#                             continue
#                     except:
#                         continue
#
#                     # 保存帧和标注
#                     img_name = f"{folder}_{video_index}_{frame_count}.jpg"
#                     label_name = f"{folder}_{video_index}_{frame_count}.txt"
#                     cv2.imwrite(os.path.join(target_images, img_name), frame)
#                     with open(os.path.join(target_labels, label_name), 'w') as label_file:
#                         label_file.write(label_content + '\n')
#
#                 cap.release()
#         print(f"\r[Create_data] Process Le2i_{folder} Done!")
#     source_images_dir = './data/test/Le2i/images/test'
#     source_labels_dir = './data/test/Le2i/labels/test'
#     target_images_dir = './data/images/test'
#     target_labels_dir = './data/labels/test'
#     all_images = [f for f in os.listdir(source_images_dir) if f.endswith('.jpg')]
#     # 初始化选中的图片列表
#     selected_images = []
#
#     # 筛选标签为0的图片
#     for image_name in all_images:
#         label_name = image_name.replace('.jpg', '.txt')
#         label_path = os.path.join(source_labels_dir, label_name)
#         with open(label_path, 'r') as file:
#             lines = file.readlines()
#             # 检查标签是否包含'0'
#             for line in lines:
#                 if line.split()[0] == '0':
#                     selected_images.append(image_name)
#
#     # 如果筛选后的图片少于300张，则选择全部，否则随机选择300张
#     print(len(selected_images))
#     if len(selected_images) > 450:
#         selected_images = random.sample(selected_images, 450)
#
#     # 复制选中的图片及其对应的标签文件
#     # for image_name in all_images:
#     for image_name in selected_images:
#         src_image_path = os.path.join(source_images_dir, image_name)
#         dst_image_path = os.path.join(target_images_dir, image_name)
#         shutil.copy(src_image_path, dst_image_path)
#
#         label_name = image_name.replace('.jpg', '.txt')
#         src_label_path = os.path.join(source_labels_dir, label_name)
#         dst_label_path = os.path.join(target_labels_dir, label_name)
#         shutil.copy(src_label_path, dst_label_path)


def create_le2i(source_dir, target_dir_test_images, target_dir_test_labels):
    # 定义需要处理的文件夹名称和目标目录
    folders = ['Coffee_room_01', 'Home_01', 'Coffee_room_02', 'Home_02']

    # 统一复制所有数据到./data/test/Le2i
    for folder in folders:
        print(f"[Create_data] Processing Le2i_{folder}...", end='')
        source_annotation = os.path.join(source_dir, folder, folder, 'Annotation_files')
        source_videos = os.path.join(source_dir, folder, folder, 'Videos')

        target_images = os.path.join(target_dir_test_images, 'Le2i', 'images')
        target_labels = os.path.join(target_dir_test_labels, 'Le2i', 'labels')

        os.makedirs(target_images, exist_ok=True)
        os.makedirs(target_labels, exist_ok=True)

        # 处理视频和标注文件
        for video_file in os.listdir(source_videos):
            if video_file.endswith('.avi'):
                video_path = os.path.join(source_videos, video_file)
                video_index = video_file.split(' ')[-1].split('.')[0]

                annotation_file = video_file.replace('.avi', '.txt')
                annotation_path = os.path.join(source_annotation, annotation_file)
                with open(annotation_path, 'r') as file:
                    lines = file.readlines()

                try:
                    if len(lines[0]) < 8:
                        fall_start, fall_end = int(lines[0].strip()), int(lines[1].strip())
                        if fall_start == 0:
                            continue
                    else:
                        continue
                except:
                    continue

                temp_num_safe = 0
                temp_num_fall = 0
                cap = cv2.VideoCapture(video_path)
                frame_count = 0
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_count += 1

                    label_line = lines[frame_count + 1].strip() if frame_count + 1 < len(lines) else "0,0,0,0,0,0"
                    parts = label_line.split(',')
                    class_id = 1 if frame_count >= fall_start else 0
                    if class_id == 0:
                        if temp_num_safe > 0:
                            temp_num_safe -= 1
                            continue
                        else:
                            temp_num_safe += 3
                    elif class_id == 1:
                        if temp_num_fall > 0:
                            temp_num_fall -= 1
                            continue
                        else:
                            temp_num_fall += 3
                    try:
                        x_min, y_min, x_max, y_max = map(int, parts[2:])
                        if (x_min + y_min) > 1:
                            x_center = (x_min + x_max) / 2 / frame.shape[1]
                            y_center = (y_min + y_max) / 2 / frame.shape[0]
                            width = (x_max - x_min) / frame.shape[1]
                            height = (y_max - y_min) / frame.shape[0]
                            label_content = f"{class_id} {x_center} {y_center} {width} {height}"
                        else:
                            continue
                    except:
                        continue

                    img_name = f"{folder}_{video_index}_{frame_count}.jpg"
                    label_name = f"{folder}_{video_index}_{frame_count}.txt"
                    cv2.imwrite(os.path.join(target_images, img_name), frame)
                    with open(os.path.join(target_labels, label_name), 'w') as label_file:
                        label_file.write(label_content + '\n')

                cap.release()
        print(f"\r[Create_data] Process Le2i_{folder} Done!")

    # 第二步：将数据分发到训练集和测试集
    target_images_dir_train = './data/images/train'
    target_images_dir_test = './data/images/test'
    target_labels_dir_train = './data/labels/train'
    target_labels_dir_test = './data/labels/test'

    os.makedirs(target_images_dir_train, exist_ok=True)
    os.makedirs(target_images_dir_test, exist_ok=True)
    os.makedirs(target_labels_dir_train, exist_ok=True)
    os.makedirs(target_labels_dir_test, exist_ok=True)

    all_images = [f for f in os.listdir(target_images) if f.endswith('.jpg')]
    for image_name in all_images:
        # 根据文件名前缀分配到不同的数据集
        if 'Coffee_room_01' in image_name or 'Home_01' in image_name:
            dst_image_path = os.path.join(target_images_dir_train, image_name)
            dst_label_path = os.path.join(target_labels_dir_train, image_name.replace('.jpg', '.txt'))
        elif 'Coffee_room_02' in image_name or 'Home_02' in image_name:
            dst_image_path = os.path.join(target_images_dir_test, image_name)
            dst_label_path = os.path.join(target_labels_dir_test, image_name.replace('.jpg', '.txt'))
        else:
            continue  # 跳过不符合条件的文件

        # 复制图像和标签文件
        src_image_path = os.path.join(target_images, image_name)
        src_label_path = os.path.join(target_labels, image_name.replace('.jpg', '.txt'))
        shutil.copy(src_image_path, dst_image_path)
        shutil.copy(src_label_path, dst_label_path)


if __name__ == "__main__":
    restart()
    create_pp_fall("./data/ori/ppfall/", "./data/images", "./data/labels")
    # create_fdd('./data/ori/FDD/', './data/images', './data/labels')
    create_le2i('./data/ori/Le2i', './data/test', './data/test')