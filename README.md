# Desktop Pet

一个基于 PyQt6 的桌面宠物程序。

## 功能特性

- 无边框窗口显示
- GIF动画播放
- 眼睛跟随鼠标移动
- 点击反应
- 拖拽移动
- 位置记忆
- 右键菜单

## 依赖项

- Python 3.x
- PyQt6
- transformers (预留)

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/你的用户名/desktop-pet.git
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 准备资源文件：
在 `assets` 目录下放入以下GIF动画文件：
- idle.gif (待机动画)
- click.gif (点击动画)
- look_left.gif (向左看动画)
- look_right.gif (向右看动画)
- look_up.gif (向上看动画)
- look_down.gif (向下看动画)

## 使用方法

运行主程序：
```bash
python desktop_pet.py
```

## 操作说明

- 左键拖动：移动位置
- 右键点击：显示菜单
- 鼠标移动：眼睛跟随