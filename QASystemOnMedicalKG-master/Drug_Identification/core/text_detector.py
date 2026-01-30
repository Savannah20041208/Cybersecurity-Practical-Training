#!/usr/bin/env python3
# coding: utf-8
"""
文本检测模块
集成 CRAFT 模型进行文字区域检测
"""

import os
import sys
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional

# 添加 CRAFT 路径
CRAFT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'CRAFT-pytorch')
if os.path.exists(CRAFT_DIR):
    sys.path.insert(0, CRAFT_DIR)

# 尝试导入 CRAFT
CRAFT_AVAILABLE = False
try:
    import torch
    from craft import CRAFT
    from craft_utils import getDetBoxes, adjustResultCoordinates
    from imgproc import resize_aspect_ratio, normalizeMeanVariance
    CRAFT_AVAILABLE = True
    print("[TextDetector] CRAFT 模块加载成功")
except ImportError as e:
    print(f"[Warning] CRAFT 未安装或导入失败: {e}")
except Exception as e:
    print(f"[Warning] CRAFT 加载失败: {e}")


class TextDetector:
    """文本区域检测器"""
    
    def __init__(self, 
                 model_path: str = None,
                 use_gpu: bool = False,
                 text_threshold: float = 0.7,
                 link_threshold: float = 0.4,
                 low_text: float = 0.4,
                 canvas_size: int = 1280,
                 mag_ratio: float = 1.5):
        """
        初始化文本检测器
        
        Args:
            model_path: CRAFT 模型路径
            use_gpu: 是否使用 GPU
            text_threshold: 文本置信度阈值
            link_threshold: 链接置信度阈值
            low_text: 低文本阈值
            canvas_size: 画布大小
            mag_ratio: 放大比例
        """
        self.use_gpu = use_gpu and torch.cuda.is_available() if CRAFT_AVAILABLE else False
        self.text_threshold = text_threshold
        self.link_threshold = link_threshold
        self.low_text = low_text
        self.canvas_size = canvas_size
        self.mag_ratio = mag_ratio
        
        self.model = None
        self.device = 'cuda' if self.use_gpu else 'cpu'
        
        if CRAFT_AVAILABLE:
            self._load_model(model_path)
    
    def _load_model(self, model_path: str = None):
        """加载 CRAFT 模型"""
        if not CRAFT_AVAILABLE:
            print("[TextDetector] CRAFT 不可用")
            return
        
        try:
            self.model = CRAFT()
            
            # 尝试加载预训练权重
            if model_path and os.path.exists(model_path):
                print(f"[TextDetector] 加载模型: {model_path}")
                state_dict = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
            else:
                # 检查默认路径
                default_paths = [
                    os.path.join(CRAFT_DIR, 'craft_mlt_25k.pth'),
                    os.path.join(CRAFT_DIR, 'weights', 'craft_mlt_25k.pth'),
                ]
                for path in default_paths:
                    if os.path.exists(path):
                        print(f"[TextDetector] 加载模型: {path}")
                        state_dict = torch.load(path, map_location=self.device)
                        self.model.load_state_dict(state_dict)
                        break
                else:
                    print("[TextDetector] 未找到预训练模型，使用随机初始化")
            
            self.model = self.model.to(self.device)
            self.model.eval()
            print("[TextDetector] CRAFT 模型加载成功")
            
        except Exception as e:
            print(f"[TextDetector] 模型加载失败: {e}")
            self.model = None
    
    def detect(self, image: np.ndarray) -> Dict:
        """
        检测图像中的文本区域
        
        Args:
            image: BGR 格式的图像
            
        Returns:
            {
                'boxes': [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] 列表,
                'polys': 多边形列表,
                'heatmap': 热力图 (可选)
            }
        """
        if self.model is None:
            # 使用备用方案：基于 OpenCV 的文本检测
            return self._detect_opencv(image)
        
        return self._detect_craft(image)
    
    def _detect_craft(self, image: np.ndarray) -> Dict:
        """使用 CRAFT 检测文本"""
        try:
            # BGR -> RGB
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 预处理
            img_resized, target_ratio, size_heatmap = resize_aspect_ratio(
                img_rgb, self.canvas_size, 
                interpolation=cv2.INTER_LINEAR, 
                mag_ratio=self.mag_ratio
            )
            ratio_h = ratio_w = 1 / target_ratio
            
            # 归一化
            x = normalizeMeanVariance(img_resized)
            x = torch.from_numpy(x).permute(2, 0, 1).unsqueeze(0)
            x = x.to(self.device)
            
            # 推理
            with torch.no_grad():
                y, feature = self.model(x)
            
            # 获取分数图
            score_text = y[0, :, :, 0].cpu().numpy()
            score_link = y[0, :, :, 1].cpu().numpy()
            
            # 获取检测框
            boxes, polys = getDetBoxes(
                score_text, score_link,
                self.text_threshold, self.link_threshold, self.low_text,
                poly=False
            )
            
            # 调整坐标
            boxes = adjustResultCoordinates(boxes, ratio_w, ratio_h)
            
            # 转换格式
            result_boxes = []
            for box in boxes:
                if box is not None:
                    box = box.astype(np.int32).tolist()
                    result_boxes.append(box)
            
            return {
                'boxes': result_boxes,
                'polys': polys,
                'score_text': score_text,
                'score_link': score_link,
            }
            
        except Exception as e:
            print(f"[TextDetector] CRAFT 检测失败: {e}")
            return self._detect_opencv(image)
    
    def _detect_east(self, image: np.ndarray) -> Dict:
        """
        使用 EAST 模型检测文本区域
        EAST 是一种高效的文本检测方法，适用于复杂背景
        """
        # EAST 模型路径
        east_model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'models', 'frozen_east_text_detection.pb'
        )
        
        if not os.path.exists(east_model_path):
            print(f"[TextDetector] EAST 模型不存在: {east_model_path}")
            return self._detect_opencv_morphology(image)
        
        try:
            # 加载 EAST 模型
            net = cv2.dnn.readNet(east_model_path)
            
            # 获取图像尺寸
            orig_h, orig_w = image.shape[:2]
            
            # EAST 要求输入尺寸是 32 的倍数
            new_w = (orig_w // 32) * 32
            new_h = (orig_h // 32) * 32
            new_w = max(new_w, 320)
            new_h = max(new_h, 320)
            
            ratio_w = orig_w / float(new_w)
            ratio_h = orig_h / float(new_h)
            
            # 预处理
            blob = cv2.dnn.blobFromImage(
                image, 1.0, (new_w, new_h),
                (123.68, 116.78, 103.94), 
                swapRB=True, crop=False
            )
            net.setInput(blob)
            
            # 前向传播
            output_layers = ['feature_fusion/Conv_7/Sigmoid', 'feature_fusion/concat_3']
            scores, geometry = net.forward(output_layers)
            
            # 解码检测结果
            boxes, confidences = self._decode_east(scores, geometry, 0.5)
            
            # 应用 NMS
            if len(boxes) > 0:
                indices = cv2.dnn.NMSBoxesRotated(
                    boxes, confidences, 0.5, 0.4
                )
                
                result_boxes = []
                for i in indices.flatten():
                    box = boxes[i]
                    # 调整坐标到原始尺寸
                    vertices = cv2.boxPoints(box)
                    vertices[:, 0] *= ratio_w
                    vertices[:, 1] *= ratio_h
                    result_boxes.append(vertices.astype(np.int32).tolist())
                
                return {
                    'boxes': result_boxes,
                    'polys': [],
                    'method': 'east',
                }
            
            return {'boxes': [], 'polys': [], 'method': 'east'}
            
        except Exception as e:
            print(f"[TextDetector] EAST 检测失败: {e}")
            return self._detect_opencv_morphology(image)
    
    def _decode_east(self, scores, geometry, score_thresh):
        """解码 EAST 输出"""
        num_rows, num_cols = scores.shape[2:4]
        boxes = []
        confidences = []
        
        for y in range(num_rows):
            scores_data = scores[0, 0, y]
            x0_data = geometry[0, 0, y]
            x1_data = geometry[0, 1, y]
            x2_data = geometry[0, 2, y]
            x3_data = geometry[0, 3, y]
            angles_data = geometry[0, 4, y]
            
            for x in range(num_cols):
                if scores_data[x] < score_thresh:
                    continue
                
                offset_x = x * 4.0
                offset_y = y * 4.0
                
                angle = angles_data[x]
                cos_a = np.cos(angle)
                sin_a = np.sin(angle)
                
                h = x0_data[x] + x2_data[x]
                w = x1_data[x] + x3_data[x]
                
                end_x = offset_x + cos_a * x1_data[x] + sin_a * x2_data[x]
                end_y = offset_y - sin_a * x1_data[x] + cos_a * x2_data[x]
                
                start_x = end_x - w
                start_y = end_y - h
                
                center_x = (start_x + end_x) / 2
                center_y = (start_y + end_y) / 2
                
                boxes.append(((center_x, center_y), (w, h), -angle * 180 / np.pi))
                confidences.append(float(scores_data[x]))
        
        return boxes, confidences

    def _detect_opencv_morphology(self, image: np.ndarray) -> Dict:
        """
        备用方案：使用 OpenCV 形态学操作进行文本区域检测
        """
        # 转灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 二值化
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 形态学操作：连接相邻文字
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        dilated = cv2.dilate(binary, kernel, iterations=2)
        
        # 查找轮廓
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        boxes = []
        for contour in contours:
            # 获取最小外接矩形
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int32(box)
            
            # 过滤太小的区域
            w, h = rect[1]
            if w * h < 100:
                continue
            
            boxes.append(box.tolist())
        
        return {
            'boxes': boxes,
            'polys': [],
            'method': 'opencv_morphology',
        }

    def _detect_opencv(self, image: np.ndarray) -> Dict:
        """
        OpenCV 文本检测 - 优先使用 EAST，失败则使用形态学方法
        """
        # 尝试 EAST
        result = self._detect_east(image)
        if result['boxes']:
            return result
        
        # 回退到形态学方法
        return self._detect_opencv_morphology(image)
    
    def crop_text_regions(self, image: np.ndarray, boxes: List) -> List[np.ndarray]:
        """
        根据检测框裁剪文本区域
        
        Args:
            image: 原始图像
            boxes: 检测框列表
            
        Returns:
            裁剪后的图像列表
        """
        crops = []
        for box in boxes:
            box = np.array(box, dtype=np.float32)
            
            # 获取边界矩形
            x, y, w, h = cv2.boundingRect(box)
            
            # 扩展边界
            padding = 5
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            
            # 裁剪
            crop = image[y:y+h, x:x+w]
            if crop.size > 0:
                crops.append(crop)
        
        return crops
    
    def visualize(self, image: np.ndarray, boxes: List, color=(0, 255, 0), thickness=2) -> np.ndarray:
        """
        可视化检测结果
        
        Args:
            image: 原始图像
            boxes: 检测框列表
            color: 框颜色
            thickness: 线宽
            
        Returns:
            标注后的图像
        """
        result = image.copy()
        for box in boxes:
            box = np.array(box, dtype=np.int32)
            cv2.polylines(result, [box], True, color, thickness)
        return result


def download_craft_weights():
    """下载 CRAFT 预训练权重"""
    import urllib.request
    
    weights_dir = os.path.join(CRAFT_DIR, 'weights')
    os.makedirs(weights_dir, exist_ok=True)
    
    # CRAFT 权重 URL (需要替换为实际可用的 URL)
    url = "https://drive.google.com/uc?export=download&id=1Jk4eGD7crsqCCg9C9VjCLkMN3ze8kutZ"
    output_path = os.path.join(weights_dir, 'craft_mlt_25k.pth')
    
    if os.path.exists(output_path):
        print(f"权重文件已存在: {output_path}")
        return output_path
    
    print(f"下载 CRAFT 权重到: {output_path}")
    try:
        urllib.request.urlretrieve(url, output_path)
        print("下载完成")
        return output_path
    except Exception as e:
        print(f"下载失败: {e}")
        return None


if __name__ == '__main__':
    # 测试
    detector = TextDetector()
    
    # 创建测试图像
    test_img = np.ones((480, 640, 3), dtype=np.uint8) * 255
    cv2.putText(test_img, "Test Text", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    
    result = detector.detect(test_img)
    print(f"检测到 {len(result['boxes'])} 个文本区域")
