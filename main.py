# main.py
import customtkinter as ctk
import speech_recognition as sr
import pyttsx3
import threading
from tkinter import messagebox

# 載入我們寫好的模組
from database import FatPigDB
from ai_engine import WarehouseAI

class WarehouseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FatPig 智能倉儲管理系統")
        self.geometry("550x650")
        ctk.set_appearance_mode("dark")

        # 初始化核心模組
        self.db = FatPigDB()
        self.ai = WarehouseAI()
        self.tts_engine = pyttsx3.init()
        
        # 建立 UI
        self.build_ui()

    def build_ui(self):
        # 標題
        ctk.CTkLabel(self, text="📦 語音倉儲管理中心", font=("Arial", 24, "bold")).pack(pady=20)

        # 新增商品區塊
        frame_add = ctk.CTkFrame(self)
        frame_add.pack(pady=10, padx=20, fill="x")
        
        self.entry_name = ctk.CTkEntry(frame_add, placeholder_text="輸入商品名稱")
        self.entry_name.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        
        self.entry_price = ctk.CTkEntry(frame_add, placeholder_text="輸入價格", width=80)
        self.entry_price.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(frame_add, text="新增建檔", command=self.add_product).pack(side="left", padx=10)

        # 語音控制區塊
        self.btn_voice = ctk.CTkButton(self, text="🎤 點擊開始語音指令", height=50, 
                                       font=("Arial", 18), fg_color="#A855F7", hover_color="#9333EA",
                                       command=self.start_voice_thread)
        self.btn_voice.pack(pady=20, padx=20, fill="x")

        # 系統日誌與列表區塊
        ctk.CTkLabel(self, text="系統訊息與庫存列表:", font=("Arial", 14)).pack(anchor="w", padx=20)
        self.text_log = ctk.CTkTextbox(self, height=250, font=("Arial", 14))
        self.text_log.pack(pady=5, padx=20, fill="both", expand=True)
        
        # 啟動時先顯示目前所有商品
        self.list_all_products()

    def log_message(self, message):
        """在文字框顯示訊息並捲動到最底"""
        self.text_log.insert("end", message + "\n")
        self.text_log.see("end")

    def speak(self, text):
        """讓 AI 說話"""
        self.log_message(f"🤖 系統: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def add_product(self):
        """按鈕：新增商品"""
        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        
        if not name or not price_str:
            messagebox.showwarning("警告", "請填寫商品名稱與價格！")
            return
            
        try:
            price = float(price_str)
            if self.db.add_product(name, price):
                self.log_message(f"✅ 成功建檔：{name} (價格: {price})")
                self.entry_name.delete(0, "end")
                self.entry_price.delete(0, "end")
            else:
                messagebox.showerror("錯誤", f"商品 '{name}' 已存在！")
        except ValueError:
            messagebox.showerror("錯誤", "價格必須是數字！")

    def list_all_products(self):
        """顯示所有商品與庫存"""
        self.text_log.delete("1.0", "end")
        products = self.db.get_all_products()
        if not products:
            self.log_message("📌 目前倉庫沒有任何商品。")
            return
            
        self.log_message("📊 --- 目前庫存清單 ---")
        for p in products:
            self.log_message(f"ID: {p[0]} | 名稱: {p[1]} | 價格: ${p[2]} | 庫存: {p[3]}件")
        self.log_message("----------------------")

    def start_voice_thread(self):
        """開啟獨立執行緒處理語音，防止 GUI 卡死"""
        self.btn_voice.configure(state="disabled", text="⏳ 處理中...")
        threading.Thread(target=self.process_voice_command, daemon=True).start()

    def process_voice_command(self):
        """語音辨識與 AI 解析核心邏輯"""
        recognizer = sr.Recognizer()
        user_text = None
        
        with sr.Microphone() as source:
            self.log_message("\n🎤 請開始說話...")
            # 自動適應環境噪音
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                user_text = recognizer.recognize_google(audio, language="zh-TW")
                self.log_message(f"🗣️ 你說了：{user_text}")
            except sr.WaitTimeoutError:
                self.speak("我沒有聽到聲音，請再試一次。")
            except sr.UnknownValueError:
                self.speak("我聽不清楚，請再說一次。")
            except Exception as e:
                self.log_message(f"❌ 語音錯誤: {e}")

        # 如果有收到語音文字，交給 Gemini 解析
        if user_text:
            intent_data = self.ai.parse_intent(user_text)
            self.execute_intent(intent_data)

        # 恢復按鈕狀態 (需透過 .after 回到主執行緒更新 UI)
        self.after(0, lambda: self.btn_voice.configure(state="normal", text="🎤 點擊開始語音指令"))

    def execute_intent(self, intent_data):
        """根據 Gemini 解析出的 JSON 執行對應的資料庫動作"""
        action = intent_data.get("action")
        name = intent_data.get("name")
        qty = intent_data.get("qty", 0)

        if action == "list":
            self.list_all_products()
            self.speak("為您列出目前所有庫存狀態。")
            
        elif action == "search":
            product = self.db.get_product_by_name(name)
            if product:
                self.speak(f"{name} 目前的庫存還有 {product[3]} 件，價格是 {product[2]} 元。")
            else:
                self.speak(f"倉庫裡找不到叫做 {name} 的商品，請先建檔。")
                
        elif action in ["in", "out"]:
            product = self.db.get_product_by_name(name)
            if not product:
                self.speak(f"找不到商品 {name}，無法操作庫存。")
                return

            if action == "in":
                self.db.update_stock(name, qty)
                self.speak(f"已將 {qty} 件 {name} 放入倉庫。")
            elif action == "out":
                # 檢查庫存是否足夠
                if product[3] < qty:
                    self.speak(f"庫存不足！{name} 只剩下 {product[3]} 件，無法出庫 {qty} 件。")
                else:
                    self.db.update_stock(name, -qty)
                    self.speak(f"已將 {qty} 件 {name} 出庫。")
            
            # 更新完畢後重新顯示列表
            self.after(0, self.list_all_products)
            
        else:
            self.speak("抱歉，我聽不懂這個指令，請再說得明確一點。")

if __name__ == "__main__":
    app = WarehouseApp()
    app.mainloop()