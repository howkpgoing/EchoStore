# ai_engine.py
import google.generativeai as genai
import json
import config

class WarehouseAI:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        # 使用 Gemini 1.5 Flash，並強制要求回傳 JSON 格式
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        self.system_prompt = """
        你是一個專業的倉儲管理助手。請將使用者的語音指令精準轉換為 JSON 格式。
        支援的動作 (action) 包含：
        - "search" (查詢特定商品)
        - "in" (入庫/增加庫存)
        - "out" (出庫/減少庫存)
        - "list" (查詢所有庫存)
        - "error" (無法理解指令)

        輸出格式範例：
        1. "幫我查一下蘋果" -> {"action": "search", "name": "蘋果"}
        2. "蘋果進貨50個" -> {"action": "in", "name": "蘋果", "qty": 50}
        3. "香蕉拿走20個" -> {"action": "out", "name": "香蕉", "qty": 20}
        4. "倉庫還有什麼" -> {"action": "list"}
        5. "今天天氣真好" -> {"action": "error"}

        注意：qty 必須是數字。請只輸出 JSON，不要有其他文字。
        """

    def parse_intent(self, user_text):
        try:
            prompt = f"{self.system_prompt}\n使用者指令：{user_text}"
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"AI 解析失敗: {e}")
            return {"action": "error"}