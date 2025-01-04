from PIL import Image, ImageOps
import numpy as np
from scipy.ndimage import binary_dilation

def extract_black_area_filled(image_path, output_path, threshold=230, dilation_iterations=2):
    """
    从图像中提取接近黑色的区域，填充内部空隙，并裁剪为正方形。
    :param image_path: 输入图像路径
    :param output_path: 输出图像路径
    :param threshold: 黑色阈值，值越大包含的“黑色”范围越广
    :param dilation_iterations: 膨胀操作的迭代次数，值越大填充越彻底
    """
    # 打开图像并转为RGBA格式
    img = Image.open(image_path).convert("RGBA")
    img_data = img.load()

    # 获取图像尺寸
    width, height = img.size

    # 创建一个掩码图像，用于存储黑色部分
    mask = Image.new("L", (width, height), 0)
    mask_data = mask.load()

    # 遍历像素，标记接近黑色的部分
    for y in range(height):
        for x in range(width):
            r, g, b, a = img_data[x, y]
            # 判断是否为接近黑色的像素
            if r < threshold and g < threshold and b < threshold:
                mask_data[x, y] = 255

    # 转换为NumPy数组并进行膨胀操作以填充内部空隙
    mask_array = np.array(mask)
    dilated_mask_array = binary_dilation(mask_array, iterations=dilation_iterations)
    dilated_mask = Image.fromarray((dilated_mask_array * 255).astype("uint8"))

    # 根据膨胀后的掩码找到黑色部分的边界框
    bbox = dilated_mask.getbbox()
    if bbox is None:
        print("未找到黑色区域！")
        return

    # 使用膨胀后的掩码的实际边界框
    left, top, right, bottom = bbox

    # 裁剪图像和掩码
    cropped_img = img.crop((left, top, right, bottom))
    cropped_dilated_mask = dilated_mask.crop((left, top, right, bottom))

    # 将裁剪后的黑色区域之外设为透明
    result = Image.new("RGBA", cropped_img.size, (0, 0, 0, 0))
    cropped_data = cropped_img.load()
    result_data = result.load()

    for y in range(cropped_img.size[1]):
        for x in range(cropped_img.size[0]):
            if cropped_dilated_mask.getpixel((x, y)) == 255:  # 如果掩码是黑色区域
                result_data[x, y] = cropped_data[x, y]

    # 保存结果
    result.save(output_path, "PNG")
    print(f"处理完成，结果保存到 {output_path}")

# 使用示例
extract_black_area_filled("./image/passwordimg.jpeg", "output1.png", threshold=230, dilation_iterations=2)

