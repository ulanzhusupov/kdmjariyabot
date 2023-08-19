
import sqlite3


class AdDatabase:

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                photo BLOB,
                description TEXT,
                username TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def get_all_ads(self):
        pass

    def save(self, ad):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO ads (category, photo, description, username) VALUES (?, ?, ?, ?)',
                       (ad.category, ad.photo, ad.description, ad.username))
        conn.commit()

    def update(self, ad, ad_id):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        
        cursor.execute('UPDATE ads SET category=?, photo=?, description=?, username=? WHERE id=?',
                       (ad.category, ad.photo, ad.description, ad.username, ad_id))
        conn.commit()
    
    def update_photo_by_id(self, photo_data, ad_id):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE ads SET photo=? WHERE id=?', (photo_data, ad_id))
        conn.commit()

    def update_description_by_id(self, new_text, ad_id):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE ads SET description=? WHERE id=?', (new_text, ad_id))
        conn.commit()

    def delete(self, ad_id):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ads WHERE id=?', (ad_id,))
        conn.commit()

    def get_all_ads_by_category(self, category):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM ads WHERE category = "{category}"')
        ads = cursor.fetchall()
        return ads
        # conn.commit()

    def get_ads_by_user(self, username):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM ads WHERE username = "{username}"')
        ads = cursor.fetchall()
        return ads

    def get_ad_by_id(self, ad_id):
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM ads WHERE id = "{ad_id}"')
        ads = cursor.fetchall()
        return ads