class Config:
    # 窗口设置
    WINDOW_SIZE = (128, 128)
    
    # 动画文件路径
    ANIMATIONS = {
        'idle': 'assets/idle.gif',
        'click': 'assets/click.gif',
        'eye_left': 'assets/eye_left.gif',
        'eye_right': 'assets/eye_right.gif',
        'eye_up': 'assets/eye_up.gif',
        'eye_down': 'assets/eye_down.gif'
    }
    
    # 聊天模型设置
    MODEL_NAME = "你选择的模型名称"
    MAX_LENGTH = 50 
    
# - `Config` 类存储全局配置：
#   - 窗口大小
#   - 动画文件路径
#   - 聊天模型设置
#   （注：目前主程序直接硬编码了这些设置）