# 📦 FatPig 智能倉儲管理系統 (Voice-Controlled Warehouse System)

這是一個結合 **語音辨識 (STT)**、**文字轉語音 (TTS)** 與 **Google Gemini AI** 的現代化倉儲管理桌面應用程式。
透過自然語言對話，使用者可以直接用語音下達「入庫」、「出庫」、「查詢庫存」等指令，AI 會自動解析意圖並連動 SQLite 資料庫完成操作。

## ✨ 核心功能 (Features)

* 🎤 **智慧語音指令**：免動手打字，用語音說出「幫我把蘋果入庫50個」，系統自動辨識並執行。
* 🤖 **Gemini AI 意圖解析**：採用 `gemini-1.5-flash` 模型，精準將自然語言轉換為 JSON 結構化指令，容錯率極高。
* 🗣️ **即時語音回饋**：操作成功、失敗或查詢結果，系統皆會以語音 (TTS) 播報。
* 🗄️ **輕量化資料庫**：內建 SQLite (`database.py`)，無須額外架設伺服器即可管理商品建檔與庫存增減。
* 🖥️ **現代化深色 UI**：使用 `customtkinter` 打造美觀、流暢的圖形化使用者介面。

## 📂 專案架構 (Project Structure)

```text
FatPig-Warehouse/
│
├── main.py             # 主程式：負責 GUI 介面與系統整合 (執行這個檔案)
├── ai_engine.py        # AI 模組：封裝 Gemini API 連線與 Prompt 設定
├── database.py         # 資料庫模組：處理 SQLite 的 CRUD 操作
├── config.example.py   # 設定檔範本 (請複製並改名為 config.py)
├── .gitignore          # Git 忽略清單 (保護 API Key 與資料庫不外洩)
└── README.md           # 專案說明文件
