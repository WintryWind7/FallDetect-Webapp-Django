from ultralytics import YOLO


model = YOLO(r"D:\Codes\Works\FallDetect\api\detect\save\8s\weights\best.pt")
def predict(image_path):
    """
    使用 YOLO 模型进行目标检测。
    返回检测结果的 JSON 格式。
    :param image_path: 图片文件的路径
    :return: JSON 格式的预测结果
    """
    # 模型预测
    results = model(image_path)
    detections = results[0].boxes.data.cpu().numpy()  # 获取检测结果
    classes = results[0].names  # 获取类别名称

    # 构造 JSON 格式的返回数据
    detected_objects = []
    for detection in detections:
        x1, y1, x2, y2, confidence, cls_id = detection
        detected_objects.append({
            "bbox": [int(x1), int(y1), int(x2), int(y2)],  # 边界框
            "confidence": round(float(confidence), 2),     # 置信度
            "class": classes[int(cls_id)]                 # 类别
        })

    return detected_objects
