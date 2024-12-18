# 桌面宠物项目中的算法与数据结构

## 1. 数据结构

### 1.1 字典（Dictionary）
用于状态和资源管理：
```python
# 在 desktop_pet.py 中管理动画状态
self.animations = {
    'idle': QMovie("assets/idle.gif"),
    'look_left': QMovie("assets/look_left.gif"),
    'look_right': QMovie("assets/look_right.gif"),
    'look_up': QMovie("assets/look_up.gif"),
    'look_down': QMovie("assets/look_down.gif"),
    'click': QMovie("assets/click.gif"),
    'talking': QMovie("assets/talking.gif")
}
```

优点：
- O(1) 的访问时间复杂度
- 便于状态管理和切换
- 代码清晰易维护

### 1.2 队列（Queue）
用于消息历史管理：
```python
# 在 chat_window.py 中使用 QTextEdit 实现消息队列
self.chat_history = QTextEdit()
self.chat_history.append(message)  # 添加新消息
self.chat_history.verticalScrollBar().setValue(  # 自动滚动到最新消息
    self.chat_history.verticalScrollBar().maximum()
)
```

特点：
- 先进先出（FIFO）
- 自动滚动到最新消息
- 支持富文本显示

### 1.3 栈（Stack）
用于动画状态管理：
```python
# 在 desktop_pet.py 中的动画切换逻辑
def change_animation(self, animation_type):
    if self.current_animation != animation_type:
        # 弹出当前状态
        if self.current_animation in self.animations:
            current_movie = self.animations[self.current_animation]
            current_movie.stop()  # 停止当前动画（出栈）
            
        # 压入新状态
        new_movie = self.animations[animation_type]
        self.current_animation = animation_type  # 新状态入栈
        self.pet_label.setMovie(new_movie)
        new_movie.start()
```

特点：
- 后进先出（LIFO）
- 用于状态切换管理
- 支持状态回退
- 便于管理动画生命周期


## 2. 算法

### 2.1 阈值判断算法
用于眼睛跟随功能：
```python
def mouseMoveEvent(self, event: QMouseEvent):
    # 获取鼠标和窗口中心的位置
    mouse_x = event.pos().x()
    mouse_y = event.pos().y()
    center_x = self.width() / 2
    center_y = self.height() / 2
    
    # 阈值判断
    threshold = 40  # 像素
    if abs(mouse_x - center_x) > threshold or abs(mouse_y - center_y) > threshold:
        if abs(mouse_x - center_x) > abs(mouse_y - center_y):
            # 水平移动更大
            if mouse_x < center_x:
                self.change_animation('look_left')
            else:
                self.change_animation('look_right')
```

算法特点：
- 使用阈值避免频繁切换
- 比较水平和垂直方向的偏移
- 实现平滑的视觉效果

### 2.2 防抖动算法
用于优化动画切换：
```python
def mouseMoveEvent(self, event: QMouseEvent):
    current_time = QTime.currentTime().msecsSinceStartOfDay()
    if current_time - self.last_animation_change < 150:  # 150ms 防抖
        return
```

算法特点：
- 时间戳比较
- 固定延迟窗口
- 减少不必要的状态切换

### 2.3 坐标转换算法
用于窗口拖动：
```python
def mouseMoveEvent(self, event: QMouseEvent):
    if self.is_following and self.offset:
        # 相对坐标转全局坐标
        new_pos = self.mapToGlobal(event.pos() - self.offset)
        self.move(new_pos)
```

算法特点：
- 相对坐标转换
- 平滑的拖动效果
- 准确的位置计算

## 3. 设计模式

### 3.1 状态机模式
用于动画状态管理：
```python
def change_animation(self, animation_type):
    if self.current_animation != animation_type:
        # 停止当前动画
        if self.current_animation in self.animations:
            current_movie = self.animations[self.current_animation]
            current_movie.stop()
        
        # 切换到新动画
        new_movie = self.animations[animation_type]
        self.current_animation = animation_type
        self.pet_label.setMovie(new_movie)
        new_movie.start()
```

特点：
- 清晰的状态转换
- 易于维护和扩展
- 状态集中管理

### 3.2 观察者模式
使用信号槽机制：
```python
class ChatThread(QThread):
    response_ready = pyqtSignal(str)  # 信号定义
    
    def run(self):
        # 生成回复
        response = self.model.generate(...)
        # 发送信号
        self.response_ready.emit(response)
```

特点：
- 解耦通信机制
- 异步处理
- 事件驱动

## 4. 性能优化

### 4.1 异步处理
```python
# AI 对话的异步处理
class ChatThread(QThread):
    def run(self):
        # 在后台线程处理耗时操作
        response = self.model.generate(...)
```

### 4.2 事件过滤
```python
def eventFilter(self, obj, event):
    if obj == self.input_box and event.type() == event.Type.KeyPress:
        if event.key() == Qt.Key.Key_Return and not event.modifiers():
            self.send_message()
            return True
    return False
```

### 4.3 资源管理
```python
# 配置集中管理
class Config:
    WINDOW_SIZE = (240, 240)
    ANIMATIONS = {...}
    CHAT_CONFIG = {...}
    UI_CONFIG = {...}
```

## 总结

项目中的算法和数据结构特点：
1. 注重实时性和响应速度
2. 关注用户体验和交互流畅度
3. 合理使用设计模式
4. 优化性能和资源使用

主要应用：
1. 状态管理和切换
2. 用户交互处理
3. 异步通信
4. 资源管理 