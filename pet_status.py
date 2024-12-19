import sqlite3
from datetime import datetime, timedelta
import json

class PetStatus:
    def __init__(self, db_path='pet_data.db'):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建宠物状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pet_status (
                id INTEGER PRIMARY KEY,
                mood INTEGER DEFAULT 100,
                health INTEGER DEFAULT 100,
                exp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_interaction TEXT,
                last_feed TEXT,
                total_chat_count INTEGER DEFAULT 0,
                status_effects TEXT DEFAULT '[]'
            )
        ''')
        
        # 创建互动历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interaction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                action_type TEXT,
                details TEXT,
                mood_change INTEGER,
                health_change INTEGER,
                exp_gain INTEGER
            )
        ''')
        
        # 检查是否需要初始化宠物状态
        cursor.execute('SELECT COUNT(*) FROM pet_status')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO pet_status (mood, health, exp, level, last_interaction, last_feed, status_effects)
                VALUES (100, 100, 0, 1, ?, ?, '[]')
            ''', (datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
    def get_status(self):
        """获取宠物当前状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pet_status WHERE id = 1')
        status = cursor.fetchone()
        conn.close()
        
        # 转换为字典
        status_dict = {
            'mood': status[1],
            'health': status[2],
            'exp': status[3],
            'level': status[4],
            'last_interaction': datetime.fromisoformat(status[5]),
            'last_feed': datetime.fromisoformat(status[6]),
            'total_chat_count': status[7],
            'status_effects': json.loads(status[8])
        }
        
        # 计算状态衰减
        now = datetime.now()
        hours_since_interaction = (now - status_dict['last_interaction']).total_seconds() / 3600
        hours_since_feed = (now - status_dict['last_feed']).total_seconds() / 3600
        
        # 心情值每12小时降低5点
        mood_decay = int(hours_since_interaction / 12 * 5)
        # 健康值每24小时降低3点
        health_decay = int(hours_since_feed / 24 * 3)
        
        if mood_decay > 0 or health_decay > 0:
            # 更新状态
            new_mood = max(0, min(100, status_dict['mood'] - mood_decay))
            new_health = max(0, min(100, status_dict['health'] - health_decay))
            
            # 保存新状态到数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE pet_status 
                SET mood = ?, health = ?
                WHERE id = 1
            ''', (new_mood, new_health))
            conn.commit()
            conn.close()
            
            # 更新返回的状态
            status_dict['mood'] = new_mood
            status_dict['health'] = new_health
        
        return status_dict
        
    def _calculate_decay(self):
        """计算状态自然衰减 - 已弃用，逻辑已移至 get_status"""
        pass
        
    def update_status(self, mood_change=0, health_change=0, exp_gain=0, action_type="", details="", reason=""):
        """更新宠物状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取当前状态
        cursor.execute('SELECT mood, health, exp, level FROM pet_status WHERE id = 1')
        current = cursor.fetchone()
        
        # 计算新状态
        new_mood = max(0, min(100, current[0] + mood_change))
        new_health = max(0, min(100, current[1] + health_change))
        new_exp = current[2] + exp_gain
        new_level = current[3]
        
        # 经验值升级检查
        exp_needed = new_level * 100
        while new_exp >= exp_needed:
            new_exp -= exp_needed
            new_level += 1
            exp_needed = new_level * 100
        
        # 更新状态
        cursor.execute('''
            UPDATE pet_status 
            SET mood = ?, health = ?, exp = ?, level = ?, last_interaction = ?
            WHERE id = 1
        ''', (new_mood, new_health, new_exp, new_level, datetime.now().isoformat()))
        
        # 记录互动历史
        if action_type:
            cursor.execute('''
                INSERT INTO interaction_history 
                (timestamp, action_type, details, mood_change, health_change, exp_gain)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), action_type, details, mood_change, health_change, exp_gain))
        
        conn.commit()
        conn.close()
        
    def feed(self):
        """喂食"""
        self.update_status(
            mood_change=10,
            health_change=15,
            exp_gain=5,
            action_type="feed",
            details="投喂食物",
            reason="喂食"
        )
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE pet_status SET last_feed = ? WHERE id = 1', (datetime.now().isoformat(),))
        conn.commit()
        conn.close()
        
    def play(self):
        """玩耍"""
        self.update_status(
            mood_change=15,
            health_change=-5,
            exp_gain=10,
            action_type="play",
            details="一起玩耍",
            reason="玩耍"
        )
        
    def chat(self):
        """聊天"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE pet_status SET total_chat_count = total_chat_count + 1 WHERE id = 1')
        conn.commit()
        conn.close()
        
        self.update_status(
            mood_change=5,
            exp_gain=3,
            action_type="chat",
            details="聊天互动",
            reason="聊天"
        )
        
    def get_interaction_history(self, limit=10):
        """获取最近的互动历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, action_type, details, mood_change, health_change, exp_gain
            FROM interaction_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        history = cursor.fetchall()
        conn.close()
        return history 
        
    def play_music(self):
        """演奏贝斯"""
        self.update_status(
            mood_change=15,
            exp_gain=10,
            action_type="play_music",
            details="演奏了一段贝斯",
            reason="演奏"
        )
        
    def change_strings(self):
        """换贝斯弦"""
        self.update_status(
            health_change=15,
            exp_gain=20,
            action_type="change_strings",
            details="更换贝斯琴弦",
            reason="换弦"
        )
        
    def maintenance(self):
        """保养贝斯"""
        self.update_status(
            health_change=20,
            mood_change=5,
            exp_gain=5,
            action_type="maintenance",
            details="保养贝斯",
            reason="保养"
        )
        
    def practice(self):
        """练习贝斯"""
        self.update_status(
            exp_gain=25,
            mood_change=10,
            health_change=-5,
            action_type="practice",
            details="练习贝斯技巧",
            reason="学习"
        )
        
    def add_status_effect(self, effect_name, effect_data):
        """添加状态效果
        
        Args:
            effect_name (str): 效果名称
            effect_data (dict): 效果数据，例如：
                {
                    'type': 'buff/debuff',
                    'duration': 3600,  # 持续时间（秒）
                    'start_time': '2023-09-20T10:00:00',
                    'effects': {
                        'mood_boost': 10,
                        'health_boost': -5
                    }
                }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取当前状态效果
        cursor.execute('SELECT status_effects FROM pet_status WHERE id = 1')
        current_effects = json.loads(cursor.fetchone()[0])
        
        # 添加新效果
        effect_data['start_time'] = datetime.now().isoformat()
        current_effects.append({
            'name': effect_name,
            'data': effect_data
        })
        
        # 保存回数据库
        cursor.execute('''
            UPDATE pet_status 
            SET status_effects = ?
            WHERE id = 1
        ''', (json.dumps(current_effects),))
        
        conn.commit()
        conn.close()
        
    def remove_expired_effects(self):
        """移除过期的状态效果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取当前状态效果
        cursor.execute('SELECT status_effects FROM pet_status WHERE id = 1')
        current_effects = json.loads(cursor.fetchone()[0])
        
        now = datetime.now()
        active_effects = []
        
        # 过滤出未过期的效果
        for effect in current_effects:
            start_time = datetime.fromisoformat(effect['data']['start_time'])
            duration = effect['data']['duration']
            if (now - start_time).total_seconds() < duration:
                active_effects.append(effect)
        
        # 保存活跃效果回数据库
        cursor.execute('''
            UPDATE pet_status 
            SET status_effects = ?
            WHERE id = 1
        ''', (json.dumps(active_effects),))
        
        conn.commit()
        conn.close()
        
    def apply_status_effects(self):
        """应用当前的状态效果"""
        # 首先移除过期效果
        self.remove_expired_effects()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取当前状态效果
        cursor.execute('SELECT status_effects FROM pet_status WHERE id = 1')
        current_effects = json.loads(cursor.fetchone()[0])
        
        # 计算所有效果的总和
        total_mood_change = 0
        total_health_change = 0
        
        for effect in current_effects:
            effects = effect['data']['effects']
            total_mood_change += effects.get('mood_boost', 0)
            total_health_change += effects.get('health_boost', 0)
        
        # 如果有效果需要应用
        if total_mood_change != 0 or total_health_change != 0:
            self.update_status(
                mood_change=total_mood_change,
                health_change=total_health_change,
                action_type="status_effect",
                details="应用状态效果",
                reason="状态效果"
            )
        
        conn.close()
        
    def get_active_effects(self):
        """获取当前活跃的状态效果"""
        self.remove_expired_effects()  # 首先清理过期效果
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT status_effects FROM pet_status WHERE id = 1')
        current_effects = json.loads(cursor.fetchone()[0])
        conn.close()
        
        return current_effects