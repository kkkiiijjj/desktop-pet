from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QMenu
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize, QTime, QSettings, QThread, pyqtSignal
from PyQt6.QtGui import QMovie, QMouseEvent
import sys
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import torch
from config import Config
from chat_window import ChatWindow

# 添加一个处理对话的线程类
class ChatThread(QThread):
    response_ready = pyqtSignal(str)  # 用于发送生成的回复
    started_processing = pyqtSignal()  # 添加开始处理的信号
    finished_processing = pyqtSignal()  # 添加结束处理的信号
    
    def __init__(self, model, tokenizer, message):
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer
        self.message = message
        
    def run(self):
        try:
            self.started_processing.emit()  # 发出开始信号
            
            # 编码输入文本
            inputs = self.tokenizer([self.message], return_tensors="pt", truncation=True)
            if torch.cuda.is_available():
                inputs = inputs.to('cuda')
            
            # 生成回复
            outputs = self.model.generate(
                **inputs,
                max_length=60,
                min_length=10,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                num_return_sequences=1
            )
            
            # 解码回复
            response = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            
            if not response.strip():
                response = "I'm here to chat! How can I help you?"
                
            self.response_ready.emit(response)
        except Exception as e:
            self.response_ready.emit(f"发生错误: {str(e)}")
        finally:
            self.finished_processing.emit()  # 发出结束信号

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('YourCompany', 'DesktopPet')
        # 添加加载状态标志
        self.is_loading = True
        self.initUI()
        self.is_following = False
        self.offset = None
        self.last_animation_change = 0
        self.last_mouse_pos = None
        self.chat_window = None
        self.chatbot = None
        self.tokenizer = None
        self.model = None
        # 使用定时器延迟加载聊天模型
        QTimer.singleShot(100, self.delayed_init)
        self.chat_history = []  # 添加对话历史记录
        self.is_talking = False  # 添加说话状态标志
        
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
        
        # 添加加载提示标签
        self.loading_label = QLabel("Loading...", self)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
                border-radius: 10px;
                padding: 5px;
            }
        """)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.resize(100, 30)
        self.loading_label.move(70, 105)  # 居中显示
        
        # 初始隐藏动画
        self.pet_label.hide()
        
    def delayed_init(self):
        # 初始化聊天模型
        self.initChatbot()
        # 显示动画，隐藏加载提示
        self.loading_label.hide()
        self.pet_label.show()
        self.is_loading = False
        
    def initChatbot(self):
        try:
            # 初始化 BlenderBot
            model_name = "facebook/blenderbot-400M-distill"
            self.tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
            self.model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
            if torch.cuda.is_available():
                self.model = self.model.cuda()
            self.model = self.model.eval()
        except Exception as e:
            print(f"聊天模型加载失败: {str(e)}")
            
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        # 添加聊天选项
        chat_action = menu.addAction('聊天')
        menu.addSeparator()
        settings_action = menu.addAction('设置')
        menu.addSeparator()
        quit_action = menu.addAction('退出')
        
        action = menu.exec(event.globalPos())
        if action == quit_action:
            QApplication.quit()
        elif action == settings_action:
            pass  # TODO: 设置窗口
        elif action == chat_action:
            self.show_chat_window()
            
    def show_chat_window(self):
        if not self.chat_window:
            self.chat_window = ChatWindow(self)
            self.chat_window.message_sent.connect(self.handle_chat)
            
        # 设置聊天窗口位置
        pet_pos = self.pos()
        self.chat_window.move(pet_pos.x() + self.width(), pet_pos.y())
        self.chat_window.show()
        
    def handle_chat(self, message):
        if self.model and self.tokenizer:
            # 设置说话状态
            self.is_talking = True
            self.change_animation('talking')
            
            # 创建并启动对话线程
            self.chat_thread = ChatThread(self.model, self.tokenizer, message)
            self.chat_thread.response_ready.connect(self.on_response_ready)
            self.chat_thread.start()
        else:
            self.chat_window.add_response("抱歉，我现在无法回答。")
            
    def on_response_ready(self, response):
        # 处理生成的回复
        self.chat_window.add_response(response)
        # 结束说话状态
        self.is_talking = False
        self.return_to_idle()
        
    def mousePressEvent(self, event: QMouseEvent):
        # 加载时不响应点击
        if self.is_loading:
            return
        # 处理鼠标左键点击
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()
            self.is_following = True
            
            # 切换到点击动画
            self.change_animation('click')
            
            # 设置定时器返回待机状态
            QTimer.singleShot(1000, self.return_to_idle)
            
    def mouseMoveEvent(self, event: QMouseEvent):
        # 加载时不响应移动
        if self.is_loading:
            return
        # 处理拖动和眼睛跟随
        if self.is_following and self.offset:
            # 如果正在拖动，移动窗口
            new_pos = self.mapToGlobal(event.pos() - self.offset)
            self.move(new_pos)
        else:
            # 如果不是在拖动，处理眼睛跟随
            current_time = QTime.currentTime().msecsSinceStartOfDay()
            if current_time - self.last_animation_change < 150:
                return
                
            # 获取鼠标相对于窗口的位置
            mouse_x = event.pos().x()
            mouse_y = event.pos().y()
            
            # 窗口中心点
            center_x = self.width() / 2
            center_y = self.height() / 2
            
            # 添加一个阈值，只有当鼠标移动足够远时才改变方向
            threshold = 40  # 像素
            
            # 根据鼠标位置选择对应的动画
            if self.current_animation != 'click':  # 如果不在点击动画中
                if abs(mouse_x - center_x) > threshold or abs(mouse_y - center_y) > threshold:
                    if abs(mouse_x - center_x) > abs(mouse_y - center_y):
                        # 水平方向移动更大
                        if mouse_x < center_x:
                            self.change_animation('look_left')
                        else:
                            self.change_animation('look_right')
                    else:
                        # 垂直方向移动更大
                        if mouse_y < center_y:
                            self.change_animation('look_up')
                        else:
                            self.change_animation('look_down')
                else:
                    # 如果鼠标在中心区域，返回到待机状态
                    self.change_animation('idle')
                    
                self.last_animation_change = current_time
                
    def mouseReleaseEvent(self, event: QMouseEvent):
        # 处理鼠标释放事件
        self.is_following = False
# 上面那些都是事件处理函数
# 下面是动画控制函数
    def change_animation(self, animation_type):
        # 切换动画
        try:
            if self.current_animation != animation_type:
                # 如果正在说话，不要切换到其他动画（除了返回idle）
                if self.is_talking and animation_type not in ['talking', 'idle']:
                    return
                    
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