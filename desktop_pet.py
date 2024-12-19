from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QDialog, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize, QTime, QSettings, QThread, pyqtSignal
from PyQt6.QtGui import QMovie, QMouseEvent
import sys
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import torch
from config import Config
from chat_window import ChatWindow
import random
from pet_status import PetStatus

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
        self.config = Config()
        
    def personalize_response(self, response):
        # 添加个性化的语气词
        if any(word in response.lower() for word in ['谢谢', '感谢']):
            response += f" {random.choice(self.config.PET_PROFILE['catchphrase'])}"
        
        # 替换机器人相关词汇
        response = response.replace('我是一个AI', f"我是{self.config.PET_PROFILE['name']}")
        response = response.replace('作为一个AI', f"作为一只{self.config.PET_PROFILE['personality']}的小宠物")
        
        # 随机添加个性化语气词
        if random.random() < 0.3:  # 30%的概率添加语气词
            response += f" {random.choice(self.config.PET_PROFILE['catchphrase'])}"
            
        return response
        
    def run(self):
        try:
            self.started_processing.emit()
            
            # 根据宠物设定调整输入（检查dislikes是否存在）
            context = f"你是一只名叫{self.config.PET_PROFILE['name']}的{self.config.PET_PROFILE['personality']}的宠物，" \
                     f"今年{self.config.PET_PROFILE['age']}岁。你喜欢{', '.join(self.config.PET_PROFILE['likes'])}。"
            
            input_text = context + " " + self.message
            
            # 编码输入文本
            inputs = self.tokenizer([input_text], return_tensors="pt", truncation=True)
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
            
            # 解码并个性化回复
            response = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            response = self.personalize_response(response)
            
            if not response.strip():
                response = f"主人想聊什么呢？{random.choice(self.config.PET_PROFILE['catchphrase'])}"
                
            self.response_ready.emit(response)
        except Exception as e:
            self.response_ready.emit(f"呜呜...{self.config.PET_PROFILE['name']}遇到了一点小问题...")
        finally:
            self.finished_processing.emit()

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('YourCompany', 'DesktopPet')
        self.pet_status = PetStatus()  # 初始化宠物状态管理器
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
        
        # 添加互动选项
        interaction_menu = menu.addMenu('互动')
        play_music_action = interaction_menu.addAction('演奏贝斯')
        change_strings_action = interaction_menu.addAction('换贝斯弦')
        maintenance_action = interaction_menu.addAction('保养贝斯')
        practice_action = interaction_menu.addAction('练习贝斯')
        menu.addSeparator()
        
        # 添加查看资料选项
        profile_action = menu.addAction('查看资料')
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
        elif action == profile_action:
            self.show_profile_window()
        elif action == play_music_action:
            self.pet_status.play_music()
            self.show_interaction_result("演奏", "演奏了一段超酷的贝斯！")
        elif action == change_strings_action:
            self.pet_status.change_strings()
            self.show_interaction_result("换弦", "给贝斯换上了新琴弦！")
        elif action == maintenance_action:
            self.pet_status.maintenance()
            self.show_interaction_result("保养", "认真地保养了贝斯！")
        elif action == practice_action:
            self.pet_status.practice()
            self.show_interaction_result("学习", "学到了新的贝斯技巧！")
            
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
            # 更新聊天状态
            self.pet_status.chat()
            
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

    def show_profile_window(self):
        profile_dialog = QDialog(self)
        profile_dialog.setWindowTitle(f"{Config.PET_PROFILE['name']}的个人资料")
        profile_dialog.setFixedSize(280, 200)  # 减小窗口高度
        
        profile_dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {Config.UI_CONFIG['colors']['window_bg']};
                border: 2px solid {Config.UI_CONFIG['colors']['border']};
                border-radius: 12px;
            }}
            QLabel {{
                color: {Config.UI_CONFIG['colors']['ai_text']};
                font-family: {Config.UI_CONFIG['font_family']};
                font-size: {Config.UI_CONFIG['font_size']}pt;
                margin: 0;
                padding: 0;
                background-color: transparent;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)  # 移除所有边距
        
        # 获取最新状态
        status = self.pet_status.get_status()
        
        # 添加资料信息，使用更紧凑的样式
        info_text = f"""
        <div style='text-align: center; margin: 0; padding: 0;'>
            <h3 style='color: {Config.UI_CONFIG['colors']['ai_text']}; margin: 0 0 2px 0;'>
                ✨ {Config.PET_PROFILE['name']} ✨
            </h3>
            <table style='width: 100%; margin: 2px 0; border-spacing: 0; border-collapse: collapse;'>
                <tr>
                    <td style='padding: 1px;'>🎈 年龄：{Config.PET_PROFILE['age']}岁</td>
                    <td style='padding: 1px;'>🎂 生日：{Config.PET_PROFILE['birthday']}</td>
                </tr>
                <tr>
                    <td colspan='2' style='padding: 1px;'>✨ 性格：{Config.PET_PROFILE['personality']}</td>
                </tr>
                <tr>
                    <td colspan='2' style='padding: 1px;'>💝 喜欢：{', '.join(Config.PET_PROFILE['likes'])}</td>
                </tr>
                <tr>
                    <td colspan='2' style='padding: 1px;'>💫 口头禅：{' '.join(Config.PET_PROFILE['catchphrase'])}</td>
                </tr>
            </table>
            
            <div style='margin: 4px 0 0 0;'>
                <div style='margin: 2px 0;'>
                    <b>🌟 等级 {status['level']}</b>
                </div>
                <div style='margin: 1px 0;'>
                    ⭐ 经验值：{status['exp']}/{status['level'] * 100}
                </div>
                <div style='margin: 1px 0;'>
                    💖 心情值：{status['mood']}/100
                </div>
                <div style='margin: 1px 0;'>
                    💪 健康值：{status['health']}/100
                </div>
                <div style='margin: 1px 0;'>
                    💭 互动次数：{status['total_chat_count']}
                </div>
            </div>
        </div>
        """
        
        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        profile_dialog.setLayout(layout)
        
        # 设置窗口位置在宠物旁边
        pet_pos = self.pos()
        profile_dialog.move(pet_pos.x() + self.width(), pet_pos.y())
        
        profile_dialog.exec()

    def show_interaction_result(self, action_type, message):
        """显示互动结果的提示框"""
        msg = QMessageBox(self)
        msg.setWindowTitle(f"{Config.PET_PROFILE['name']}的反应")
        msg.setText(f"{Config.PET_PROFILE['name']}{message}")
        msg.setInformativeText(f"""
当前状态：
💖 心情值：{self.pet_status.get_status()['mood']}/100
💪 健康值：{self.pet_status.get_status()['health']}/100
⭐ 经验值：{self.pet_status.get_status()['exp']}/{self.pet_status.get_status()['level'] * 100}
""")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

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