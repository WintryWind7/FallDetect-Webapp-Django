from ultralytics import YOLO

model = YOLO("./model/yaml/yolov8s.yaml")
# model = YOLO("yolov8s-rtdetr.pt")
model = YOLO("./model/pt/yolov8s.pt")

if __name__ == "__main__":
    results = model.train(data="./model/yaml/data.yaml", epochs=200, imgsz=640, batch=16)