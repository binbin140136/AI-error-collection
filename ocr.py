from PIL import Image, ImageEnhance
import pytesseract
import os

# 添加Tesseract可执行路径配置
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def recognize_text(image_path):
    """使用OCR识别图片文字"""
    try:
        img = Image.open(image_path)
        # 图像预处理
        img = img.convert('L')  # 转为灰度
        img = ImageEnhance.Contrast(img).enhance(2.0)  # 增强对比度
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        return text.strip()
    except Exception as e:
        print(f"OCR预处理失败: {str(e)}")
        return ""
        raise Exception(f"OCR识别失败: {str(e)}")
    finally:
        if 'img' in locals(): img.close()
    
