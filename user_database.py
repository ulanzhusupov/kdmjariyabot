import sqlite3



class UserDatabase:

    def create_table(self):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        chat_id INTEGER UNIQUE,
                        username TEXT,
                        num_ads INTEGER DEFAULT 0
                    )''')
        conn.commit()

    
    def create_user(self, user_id, chat_id, username):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (user_id, chat_id, username) VALUES (?, ?, ?)', (user_id, chat_id, username))
        conn.commit()

    def update_chatid(self, chat_id, user_id):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET chat_id=? WHERE user_id=?', (chat_id, user_id))
        conn.commit()

    def update_user_ad_num(self, num_ads, username):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET num_ads=? WHERE username=?', (num_ads, username))
        conn.commit()

    def get_user(self, user_id):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
        user_data = cursor.fetchone()
        conn.commit()
        return user_data

    def get_all_users(self):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        user_data = cursor.fetchall()
        conn.commit()
        return user_data