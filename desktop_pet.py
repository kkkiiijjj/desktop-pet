from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QMenu
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize, QTime, QSettings
from PyQt6.QtGui import QMovie, QMouseEvent
import sys
from transformers import pipeline
from config import Config

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('YourCompany', 'DesktopPet')
        self.initUI()
        self.is_following = False
        self.offset = None
        self.last_animation_change = 0  # 添加这行来跟踪上次动画更改时间
        
    def initUI(self):
        # 设置窗口属性
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建标签用于显示GIF
        self.pet_label = QLabel(self)
        # 设置标签大小和位置
        self.pet_label.setFixedSize(*Config.WINDOW_SIZE)
        
        # 启用鼠标追踪
        self.setMouseTracking(True)
        self.pet_label.setMouseTracking(True)
        
        # 存储所有动画
        self.animations = {}
        for name, path in Config.ANIMATIONS.items():
            self.animations[name] = QMovie(path)
        
        # 设置所有动画的大小
        for anim in self.animations.values():
            anim.setScaledSize(QSize(240, 240))
        
        # 设置初始动画
        self.current_animation = 'idle'
        self.pet_label.setMovie(self.animations['idle'])
        self.animations['idle'].start()
        
        # 设置窗口大小
        self.setFixedSize(240, 240)
        # 恢复上次的位置，如果没有保存过就使用默认位置
        pos = self.settings.value('pos', QPoint(500, 300))
        self.move(pos)
        self.show()
        
    # def initChatbot(self):
    #     # 初始化对话模型
    #     self.chatbot = pipeline("text-generation", model="你选择的模型名称")
        
    def contextMenuEvent(self, event):
        # 创建右键菜单
        menu = QMenu(self)
        
        # 添加更多选项
        settings_action = menu.addAction('设置')
        menu.addSeparator()  # 添加分隔线
        quit_action = menu.addAction('退出')
        
        # 处理选择
        action = menu.exec(event.globalPos())
        if action == quit_action:
            QApplication.quit()
        elif action == settings_action:
            # TODO: 打开设置窗口
            pass
        
    def mousePressEvent(self, event: QMouseEvent):
        # 处理鼠标左键点击
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()
            self.is_following = True
            
            # 切换到点击动画
            self.change_animation('click')
            
            # 设置定时器返回待机状态
            QTimer.singleShot(1000, self.return_to_idle)
            
    def mouseMoveEvent(self, event: QMouseEvent):
        # 处理拖动和眼睛跟随
        if self.is_following and self.offset:
            # 如果正在拖动，移动窗口
            new_pos = self.mapToGlobal(event.pos() - self.offset)
            self.move(new_pos)
        else:
            # 如果不是在拖动，处理眼睛跟随
            current_time = QTime.currentTime().msecsSinceStartOfDay()
            if current_time - self.last_animation_change < 150:  # 可以增加到150ms使动画更平滑
                return
                
            # 获取鼠标相对于窗口的位置
            mouse_x = event.pos().x()
            mouse_y = event.pos().y()
            
            # 窗口中心点
            center_x = self.width() / 2
            center_y = self.height() / 2
            
            # 添加一个阈值，只有当鼠标移动足够远时才改变方向
            threshold = 40  # 可以增加阈值使眼睛移动不那么敏感
            
            # 根据鼠标位置选择对应的动画
            if self.current_animation != 'click':  # 如果不在点击动画中
                try:
                    if abs(mouse_x - center_x) > threshold or abs(mouse_y - center_y) > threshold:
                        new_animation = None
                        if abs(mouse_x - center_x) > abs(mouse_y - center_y):
                            # 水平方向移动更大
                            if mouse_x < center_x:
                                new_animation = 'look_left'
                            else:
                                new_animation = 'look_right'
                        else:
                            # 垂直方向移动更大
                            if mouse_y < center_y:
                                new_animation = 'look_up'
                            else:
                                new_animation = 'look_down'
                        self.change_animation(new_animation)
                    else:
                        # 如果鼠标在中心区域，返回到待机状态
                        self.change_animation('idle')
                    self.last_animation_change = current_time
                except Exception as e:
                    self.return_to_idle()     
                    
    def mouseReleaseEvent(self, event: QMouseEvent):
        # 处理鼠标释放事件
        self.is_following = False
# 上面那些都是事件处理函数
# 下面是动画控制函数
    def change_animation(self, animation_type):
        # 切换动画
        try:
            if self.current_animation != animation_type:
                # 停止当前动画
                if self.current_animation in self.animations:
                    current_movie = self.animations[self.current_animation]
                    if current_movie:
                        current_movie.stop()
                
                # 切换到新动画
                new_movie = self.animations[animation_type]
                if new_movie:
                    self.current_animation = animation_type
                    self.pet_label.setMovie(new_movie)
                    new_movie.start()
        except Exception:
            self.return_to_idle()

        
    def return_to_idle(self):
        # 返回待机动画
        self.change_animation('idle')
        
    # def chat(self, user_input):
    #     # 生成回复
    #     response = self.chatbot(user_input, max_length=50)[0]['generated_text']
    #     return response

# 下面是窗口关闭事件处理函数
    def closeEvent(self, event):
        # 保存窗口位置
        self.settings.setValue('pos', self.pos())
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec()) 
    
    
#  主程序文件（即当前文件）结构
# - 核心类 `DesktopPet`（继承自QMainWindow）包含：
#   - 初始化函数 `__init__` 和 `initUI`：设置窗口属性、加载动画
#   - 事件处理函数：
#     - `mousePressEvent`: 处理鼠标点击
#     - `mouseMoveEvent`: 处理拖动和眼睛跟随
#     - `mouseReleaseEvent`: 处理鼠标释放
#     - `contextMenuEvent`: 处理右键菜单
#   - 动画控制函数：
#     - `change_animation`: 切换动画状态
#     - `return_to_idle`: 返回待机状态
#   - 设置相关：
#     - `closeEvent`: 保存窗口位置



# 功能模块划分：
# - 界面显示：使用PyQt6实现无边框窗口
# - 动画系统：使用QMovie加载和播放GIF动画
# - 交互系统：
#   - 拖拽功能
#   - 眼睛跟随
#   - 点击反应
#   - 右键菜单
# - 设置系统：使用QSettings保存窗口位置
# - 聊天功能：预留了接口但当前未实现


# - PyQt6: 提供GUI框架
# - transformers: 预留用于聊天功能（当前未使用）
# - sys: Python标准库，用于程序控制