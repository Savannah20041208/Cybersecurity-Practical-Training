#!/usr/bin/env python3
# coding: utf-8
"""
图片预处理模块
负责图片的读取、缩放、增强、去噪等预处理操作
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io


class ImageProcessor:
    """图片预处理器"""

    def __init__(self, max_size=2048, min_size=100):
        self.max_size = max_size
        self.min_size = min_size

    def load_image(self, image_source):
        """
        加载图片，支持多种输入格式
        
        Args:
            image_source: 文件路径、字节流、PIL Image 或 numpy 数组
            
        Returns:
            numpy 数组 (BGR 格式)
        """
        if isinstance(image_source, str):
            # 文件路径
            if not os.path.exists(image_source):
                raise FileNotFoundError(f"图片文件不存在: {image_source}")
            image = cv2.imread(image_source)
            if image is None:
                raise ValueError(f"无法读取图片: {image_source}")
            return image

        elif isinstance(image_source, bytes):
            # 字节流
            nparr = np.frombuffer(image_source, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("无法解码图片字节流")
            return image

        elif isinstance(image_source, Image.Image):
            # PIL Image
            if image_source.mode == 'RGBA':
                image_source = image_source.convert('RGB')
            return cv2.cvtColor(np.array(image_source), cv2.COLOR_RGB2BGR)

        elif isinstance(image_source, np.ndarray):
            # numpy 数组
            return image_source

        else:
            raise TypeError(f"不支持的图片类型: {type(image_source)}")

    def resize_image(self, image, max_size=None):
        """
        调整图片大小，保持宽高比
        
        Args:
            image: numpy 数组
            max_size: 最大边长
            
        Returns:
            调整后的图片
        """
        if max_size is None:
            max_size = self.max_size

        h, w = image.shape[:2]
        
        # 检查最小尺寸
        if max(h, w) < self.min_size:
            raise ValueError(f"图片尺寸过小: {w}x{h}")

        # 如果不需要缩放
        if max(h, w) <= max_size:
            return image

        # 计算缩放比例
        scale = max_size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)

        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    def enhance_contrast(self, image, factor=1.5):
        """
        增强对比度
        
        Args:
            image: numpy 数组 (BGR)
            factor: 增强因子
            
        Returns:
            增强后的图片
        """
        # 转换为 PIL Image
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # 增强对比度
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced = enhancer.enhance(factor)
        
        # 转回 numpy
        return cv2.cvtColor(np.array(enhanced), cv2.COLOR_RGB2BGR)

    def enhance_sharpness(self, image, factor=1.5):
        """
        增强锐度
        
        Args:
            image: numpy 数组 (BGR)
            factor: 增强因子
            
        Returns:
            增强后的图片
        """
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        enhancer = ImageEnhance.Sharpness(pil_image)
        enhanced = enhancer.enhance(factor)
        return cv2.cvtColor(np.array(enhanced), cv2.COLOR_RGB2BGR)

    def denoise(self, image, strength=10):
        """
        去噪
        
        Args:
            image: numpy 数组 (BGR)
            strength: 去噪强度
            
        Returns:
            去噪后的图片
        """
        return cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)

    def auto_rotate(self, image):
        """
        自动旋转校正（基于文字方向检测）
        简单实现：检测主要边缘方向
        
        Args:
            image: numpy 数组 (BGR)
            
        Returns:
            旋转后的图片
        """
        # 转灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 边缘检测
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # 霍夫变换检测直线
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
        
        if lines is None or len(lines) == 0:
            return image

        # 计算主要角度
        angles = []
        for line in lines[:20]:  # 只取前20条线
            rho, theta = line[0]
            angle = np.degrees(theta) - 90
            if -45 < angle < 45:
                angles.append(angle)

        if not angles:
            return image

        # 取中位数角度
        median_angle = np.median(angles)
        
        # 如果角度太小，不旋转
        if abs(median_angle) < 1:
            return image

        # 旋转图片
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(image, matrix, (w, h), 
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def deskew(self, image, delta_deg=5.0):
        """
        倾斜校正 - 使用 Hough 变换检测主水平线角度并旋转矫正
        来源：ResNet101 项目优化算法
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=200)
        
        if lines is None:
            return image
        
        angles = []
        for rho, theta in lines[:, 0, :]:
            deg = theta * 180 / np.pi
            # 仅关注接近水平的线
            if abs(deg) < delta_deg or abs(deg - 180) < delta_deg:
                ang = deg if deg < 90 else deg - 180
                angles.append(ang)
        
        if not angles:
            return image
        
        mean_angle = float(np.mean(angles))
        if abs(mean_angle) < 0.1:
            return image
        
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, mean_angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), 
                                  flags=cv2.INTER_LINEAR, 
                                  borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def build_text_mask(self, image):
        """
        构建文字掩码 - 突出文字区域，抑制背景
        来源：ResNet101 项目的 build_ink_mask 优化
        适用于药盒图片的文字检测
        """
        if image.ndim == 3 and image.shape[2] == 3:
            b, g, r = cv2.split(image)
            # 检测深色文字（非浅色背景）
            dark = (r < 180) & (g < 180) & (b < 180)
            mask_color = dark.astype(np.uint8) * 255
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # 合并颜色检测与灰度
            gray = cv2.min(gray, mask_color)
        else:
            gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Otsu 二值化
        _, bin_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 形态学处理：去除细线噪声，保留文字
        h, w = bin_img.shape
        # 轻微闭运算连通文字笔画
        kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        cleaned = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel_close)
        # 去掉小噪点
        kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel_open)
        
        return cleaned

    def enhance_for_ocr(self, image):
        """
        针对 OCR 的综合增强处理
        结合多种技术提升文字识别率
        """
        # 1. 构建文字掩码
        text_mask = self.build_text_mask(image)
        
        # 2. 基于掩码增强原图
        # 将掩码区域的对比度提升
        enhanced = image.copy()
        if image.ndim == 3:
            # 在文字区域增强对比度
            for c in range(3):
                channel = enhanced[:, :, c]
                # 文字区域变暗（更清晰）
                channel[text_mask > 0] = np.clip(channel[text_mask > 0] * 0.7, 0, 255).astype(np.uint8)
                # 背景区域变亮
                channel[text_mask == 0] = np.clip(channel[text_mask == 0] * 1.1 + 20, 0, 255).astype(np.uint8)
        
        return enhanced

    def adaptive_enhance(self, image):
        """
        自适应增强 - 针对药盒图片优化
        """
        # 转换到 LAB 色彩空间
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # CLAHE 自适应直方图均衡化
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # 合并通道
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return enhanced

    def sharpen(self, image):
        """
        锐化处理 - 让文字边缘更清晰
        """
        kernel = np.array([[-1, -1, -1],
                           [-1,  9, -1],
                           [-1, -1, -1]])
        sharpened = cv2.filter2D(image, -1, kernel)
        return sharpened

    def preprocess(self, image_source, enhance=True, denoise_img=True, auto_rotate_img=True):
        """
        完整的预处理流程 - 针对药盒OCR优化
        集成 ResNet101 项目的图像处理优化
        
        Args:
            image_source: 图片来源
            enhance: 是否增强
            denoise_img: 是否去噪
            auto_rotate_img: 是否自动旋转校正
            
        Returns:
            预处理后的图片 (numpy 数组)
        """
        # 加载图片
        image = self.load_image(image_source)
        
        # 调整大小（保持较高分辨率以便OCR）
        image = self.resize_image(image, max_size=2048)
        
        # 倾斜校正（使用 Hough 变换优化算法）
        if auto_rotate_img:
            image = self.deskew(image)
        
        # 轻度去噪（避免过度模糊文字）
        if denoise_img:
            image = self.denoise(image, strength=3)
        
        # 增强处理
        if enhance:
            # 1. CLAHE 自适应直方图均衡化
            image = self.adaptive_enhance(image)
            # 2. 针对 OCR 的文字增强
            image = self.enhance_for_ocr(image)
            # 3. 轻度锐化
            image = self.sharpen(image)
        
        return image

    def to_grayscale(self, image):
        """
        图像灰度化
        """
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    def gaussian_blur(self, image, kernel_size=5):
        """
        高斯滤波去噪
        
        Args:
            image: 输入图像
            kernel_size: 卷积核大小（奇数）
        """
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

    def binarize(self, image, method='otsu'):
        """
        图像二值化
        
        Args:
            image: 灰度图像
            method: 'otsu' 或 'adaptive'
        """
        if len(image.shape) == 3:
            image = self.to_grayscale(image)
        
        if method == 'otsu':
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == 'adaptive':
            binary = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
        else:
            _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
        
        return binary

    def detect_edges(self, image, low_threshold=100, high_threshold=200):
        """
        Canny 边缘检测
        
        Args:
            image: 输入图像
            low_threshold: 低阈值
            high_threshold: 高阈值
        """
        if len(image.shape) == 3:
            image = self.to_grayscale(image)
        
        return cv2.Canny(image, low_threshold, high_threshold)

    def morphology_open(self, image, kernel_size=3):
        """
        形态学开运算 - 去除小噪点
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    def morphology_close(self, image, kernel_size=3):
        """
        形态学闭运算 - 填充小孔洞
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

    def dilate(self, image, kernel_size=3, iterations=1):
        """
        膨胀操作 - 扩大白色区域
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.dilate(image, kernel, iterations=iterations)

    def erode(self, image, kernel_size=3, iterations=1):
        """
        腐蚀操作 - 缩小白色区域
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.erode(image, kernel, iterations=iterations)

    def preprocess_for_ocr(self, image_source):
        """
        专门针对 OCR 的预处理流程
        参考 OpenCV 标准图像预处理流程
        
        流程：灰度化 -> 高斯滤波 -> 二值化 -> 形态学处理
        
        Returns:
            预处理后的二值图像
        """
        # 加载图片
        image = self.load_image(image_source)
        
        # 调整大小
        image = self.resize_image(image, max_size=2048)
        
        # 倾斜校正
        image = self.deskew(image)
        
        # 灰度化
        gray = self.to_grayscale(image)
        
        # 高斯滤波去噪
        blurred = self.gaussian_blur(gray, kernel_size=5)
        
        # Otsu 二值化
        binary = self.binarize(blurred, method='otsu')
        
        # 形态学处理：先开运算去噪，再闭运算连接
        binary = self.morphology_open(binary, kernel_size=2)
        binary = self.morphology_close(binary, kernel_size=2)
        
        return binary

    def preprocess_multi_mode(self, image_source, mode='color'):
        """
        多模式预处理
        
        Args:
            image_source: 图片来源
            mode: 
                'color' - 彩色增强（默认，适合 PaddleOCR）
                'binary' - 二值化（适合 Tesseract）
                'edge' - 边缘检测（用于文本区域定位）
        
        Returns:
            预处理后的图像
        """
        if mode == 'color':
            return self.preprocess(image_source, enhance=True)
        elif mode == 'binary':
            return self.preprocess_for_ocr(image_source)
        elif mode == 'edge':
            image = self.load_image(image_source)
            image = self.resize_image(image)
            gray = self.to_grayscale(image)
            blurred = self.gaussian_blur(gray)
            edges = self.detect_edges(blurred)
            return edges
        else:
            return self.preprocess(image_source)

    def save_image(self, image, path):
        """保存图片"""
        cv2.imwrite(path, image)

    def to_bytes(self, image, format='JPEG'):
        """将图片转换为字节流"""
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        buffer = io.BytesIO()
        pil_image.save(buffer, format=format)
        return buffer.getvalue()
