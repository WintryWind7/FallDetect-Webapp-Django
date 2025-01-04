import torch
from torchvision.ops import nms

boxes = torch.tensor([[25, 25, 50, 50], [24, 24, 49, 49]], dtype=torch.float32)
scores = torch.tensor([0.9, 0.8])
keep = nms(boxes, scores, 0.1)

print(keep)
