# Desktop Pet

一个基于 PyQt6 的桌面宠物程序，具有 AI 聊天功能。

## 功能特性
- 桌面宠物动画
- AI 聊天功能（使用 BlenderBot）
- 眼睛跟随鼠标
- 透明聊天窗口
- 拖拽支持

## 依赖安装
```bash
pip install -r requirements.txt
```

## 运行方法
```bash
python desktop_pet.py
```

## 项目结构
- desktop_pet.py: 主程序和核心逻辑
- chat_window.py: 聊天窗口实现
- config.py: 配置管理
- algorithms_and_structures.md: 算法和数据结构说明
- interview_qa.md: 面试问题和答案

## 使用说明
1. 右键点击宠物打开菜单
2. 选择"聊天"开始对话
3. 鼠标可以拖动宠物和聊天窗口
4. 宠物眼睛会跟随鼠标移动

## 技术特点
1. 使用 PyQt6 构建 GUI
2. 多线程处理 AI 对话
3. 事件驱动的交互设计
4. 模块化的代码结构

## 开发环境
- Python 3.8+
- PyQt6
- transformers
- torch