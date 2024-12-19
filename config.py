from PyQt6.QtCore import QSize

class Config:
    # 窗口设置
    WINDOW_SIZE = (240, 240)
    
    # 宠物个性设定
    PET_PROFILE = {
        'name': '黑贝',
        'age': 0.5,
        'personality': '傲娇、粘人、喜欢撒娇、聪明',
        'likes': ['主人'],
        'birthday': '5月27日',
        'catchphrase': ['嘣嘣~', '主人最好啦~', '主任贴贴~']
    }
    
    # 动画路径配置
    ANIMATIONS = {
        'idle': 'assets/idle.gif',
        'look_left': 'assets/look_left.gif',
        'look_right': 'assets/look_right.gif',
        'look_up': 'assets/look_up.gif',
        'look_down': 'assets/look_down.gif',
        'click': 'assets/click.gif',
        'talking': 'assets/talking.gif'
    }
    
    # AI 对话配置
    CHAT_CONFIG = {
        'model_name': "facebook/blenderbot-400M-distill",
        'max_length': 60,
        'min_length': 10,
        'temperature': 0.7,
        'top_p': 0.9,
        'do_sample': True,
    }
    
    # 界面配置
    UI_CONFIG = {
        'chat_window_size': (400, 500),
        'chat_window_title': "和黑贝贝聊天",
        'font_family': "Microsoft YaHei",
        'font_size': 9,
        
        # 颜色配置
        'colors': {
            'user_bubble': "#A8D8B9",
            'user_text': "#2E8B57",
            'ai_bubble': "#FFB6C1",
            'ai_text': "#8B3A62",
            'window_bg': "#fff0f5",
            'border': "#ffb6c1",
        }
    }
    
# - `Config` 类存储全局配置：
#   - 窗口大小
#   - 动画文件路径
#   - 聊天模型设置
#   （注：目前主程序直接硬编码了这些设置）