from PIL import Image, ImageOps

# 图片处理为黑白色

# 打开上传的流程图图片
image_path = "img1\\轮播图管理时序图.png"
image = Image.open(image_path)

# 转为灰度图
gray_image = ImageOps.grayscale(image)

# 反转两次颜色确保黑字白底
inverted_once = ImageOps.invert(gray_image)
final_image = ImageOps.invert(inverted_once)

# 保存处理后的图像
output_path = "img2\\轮播图管理时序图"+".png"
final_image.save(output_path)

output_path
