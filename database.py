# database.py
import sqlite3
import config

class FatPigDB:
    def __init__(self):
        # check_same_thread=False 允許我們在背景執行緒中呼叫資料庫
        self.conn = sqlite3.connect(config.DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                price REAL,
                stock INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def add_product(self, name, price):
        try:
            self.cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # 商品已存在

    def get_product_by_name(self, name):
        self.cursor.execute("SELECT * FROM products WHERE name = ?", (name,))
        return self.cursor.fetchone()

    def update_stock(self, name, quantity):
        self.cursor.execute("UPDATE products SET stock = stock + ? WHERE name = ?", (quantity, name))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_all_products(self):
        self.cursor.execute("SELECT * FROM products")
        return self.cursor.fetchall()