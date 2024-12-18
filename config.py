from PyQt6.QtCore import QSize

class Config:
    # 窗口设置
    WINDOW_SIZE = (240, 240)
    
    # 动画路径配置
    ANIMATIONS = {
        'idle': 'assets/idle.gif',
        'look_left': 'assets/look_left.gif',
        'look_right': 'assets/look_right.gif',
        'look_up': 'assets/look_up.gif',
        'look_down': 'assets/look_down.gif',
        'click': 'assets/click.gif',
        'talking': 'assets/talking.gif'  # 添加说话动画
    }
    
    # AI 对话配置
    CHAT_CONFIG = {
        'model_name': "facebook/blenderbot-400M-distill",  # 模型名称
        'max_length': 60,      # 生成文本的最大长度
        'min_length': 10,      # 生成文本的最小长度
        'temperature': 0.7,    # 温度参数，控制随机性
        'top_p': 0.9,         # 核采样参数
        'do_sample': True,     # 使用采样而不是贪婪解码
    }
    
    # 界面配置
    UI_CONFIG = {
        'chat_window_size': (400, 500),  # 聊天窗口大小
        'chat_window_title': "聊天",     # 聊天窗口标题
        'font_family': "Microsoft YaHei", # 字体
        'font_size': 9,                  # 字号
        
        # 颜色配置
        'colors': {
            'user_bubble': "#A8D8B9",    # 用户消息气泡颜色
            'user_text': "#2E8B57",      # 用户消息文字颜色
            'ai_bubble': "#FFB6C1",      # AI消息气泡颜色
            'ai_text': "#8B3A62",        # AI消息文字颜色
            'window_bg': "#fff0f5",      # 窗口背景色
            'border': "#ffb6c1",         # 边框颜色
        }
    }
    
# - `Config` 类存储全局配置：
#   - 窗口大小
#   - 动画文件路径
#   - 聊天模型设置
#   （注：目前主程序直接硬编码了这些设置）