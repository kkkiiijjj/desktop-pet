from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, 
                            QPushButton, QHBoxLayout, QLabel, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QFont, QColor

class ChatWindow(QDialog):
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.is_following = False
        self.offset = None
        # 添加事件过滤器以处理回车键
        self.input_box.installEventFilter(self)
        
    def initUI(self):
        # 设置完全透明的背景
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 关闭按钮（圆形）
        close_button = QPushButton("×")
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        close_button.clicked.connect(self.close)
        
        # 关闭按钮容器（右对齐）
        close_container = QHBoxLayout()
        close_container.addStretch()
        close_container.addWidget(close_button)
        layout.addLayout(close_container)
        
        # 聊天历史区域（透明背景）
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: black;
                font-family: 'Microsoft YaHei';
                font-size: 9pt;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: rgba(200, 200, 200, 150);
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        layout.addWidget(self.chat_history)
        
        # 输入区域（气泡式设计）
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: #A8D8B9;
                border-radius: 15px;
                padding: 5px;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 5, 10, 5)
        
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(35)
        self.input_box.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #2E8B57;
                font-family: 'Microsoft YaHei';
                font-size: 9pt;
                padding: 5px;
            }
        """)
        
        self.send_button = QPushButton('发送')
        self.send_button.setFixedSize(45, 25)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                border: none;
                border-radius: 12px;
                font-family: 'Microsoft YaHei';
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #3c9c67;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        layout.addWidget(input_container)
        
        self.setLayout(layout)
        self.resize(400, 200)
        
    def add_message(self, message):
        # 设置不同的样式
        if message.startswith("You: "):
            # 用户消息样式（右对齐，绿色背景）
            self.chat_history.append(f'''
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td align="right">
                            <span style="display: inline-block; background-color: #A8D8B9; color: #2E8B57; 
                                  padding: 8px 12px; border-radius: 15px; margin: 5px;">
                                {message[4:]}
                            </span>
                        </td>
                    </tr>
                </table>
            ''')
        else:
            # 宠物回复样式（左对齐，粉色背景）
            self.chat_history.append(f'''
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td align="left">
                            <span style="display: inline-block; background-color: #FFB6C1; color: #8B3A62; 
                                  padding: 8px 12px; border-radius: 15px; margin: 5px; max-width: 70%;">
                                {message[5:]}
                            </span>
                        </td>
                    </tr>
                </table>
            ''')
            
        # 滚动到底部
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )
        
    def add_response(self, response):
        self.add_message(f"Pet: {response}")
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_following = True
            self.offset = event.pos()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_following and self.offset:
            new_pos = self.mapToGlobal(event.pos() - self.offset)
            self.move(new_pos)
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        self.is_following = False
        
    def eventFilter(self, obj, event):
        if obj == self.input_box and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers():
                # 按下回车键时发送消息
                self.send_message()
                return True
            elif event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                # Shift+回车换行
                return False
        return super().eventFilter(obj, event)

    def send_message(self):
        message = self.input_box.toPlainText().strip()
        if message:
            self.message_sent.emit(message)
            self.input_box.clear()
            self.add_message("You: " + message)
            # 让输入框重新获得焦点
            self.input_box.setFocus()
            