from PyQt6.QtCore import QPoint, Qt
import math

class EyeTracker:
    def __init__(self, pet_window):
        self.pet_window = pet_window
        self.eye_center = QPoint(64, 64)  # 根据实际眼睛位置调整
        
    def update_eye_position(self, mouse_pos):
        # 获取鼠标相对于宠物窗口的位置
        relative_pos = self.pet_window.mapFromGlobal(mouse_pos)
        
        # 计算眼睛旋转角度
        dx = relative_pos.x() - self.eye_center.x()
        dy = relative_pos.y() - self.eye_center.y()
        angle = math.atan2(dy, dx)
        
        # 这里可以根据角度切换不同的眼睛动画
        self.update_eye_animation(angle)
        
    def update_eye_animation(self, angle):
        # 根据角度选择合适的眼睛动画
        # 这部分需要根据实际的动画资源来实现
        pass 
    
# - `EyeTracker` 类：
#   - 计算鼠标位置相对于宠物的位置
#   - 更新眼睛动画
#   （注：目前这个模块的功能已经集成到主程序中）