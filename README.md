# tixcraft 自動搶票機器人

這是一個使用 Python 和 Playwright 開發的自動化腳本，旨在協助使用者在 tixcraft.com 網站上自動完成搶票流程。

## ✨ 主要功能

- **目標鎖定**: 可針對特定的活動網址與日期進行搶票。
- **志願序座位**: 可設定多個理想的座位區域，機器人會依序嘗試。
- **遠端連線模式**: 連線到使用者已手動登入的 Chrome 瀏覽器，繞過網站登入和複雜的人機驗證。
- **高度可設定**: 所有搶票參數（網址、日期、票數、座位等）皆在 `bot.py` 檔案頂部設定，方便修改。
- **詳細日誌**: 將完整的執行過程記錄在 `bot.log` 中，方便追蹤與除錯。

## 🚀 環境設定

在執行此機器人之前，請完成以下設定步驟。

### 1. 建立並啟用虛擬環境

```powershell
# 建立虛擬環境
python -m venv .venv

# 啟用虛擬環境 (在 PowerShell 中)
.\\.venv\\Scripts\\Activate.ps1
```

### 2. 安裝依賴套件

```powershell
# 安裝所有必要的套件
pip install -r requirements.txt

# 安裝 Playwright 所需的瀏覽器驅動程式
playwright install
```

### 3. 建立專用 Chrome 偵錯捷徑 (關鍵步驟)

為了讓機器人能接管已登入的瀏覽器，我們需要一個以「偵錯模式」啟動的 Chrome。

1.  在桌面上找到您現有的 Chrome 捷徑，複製並貼上它，將新的捷徑重新命名為 **"Chrome (Debug Mode)"**。
2.  在新的 **"Chrome (Debug Mode)"** 捷徑上按右鍵，選擇「**內容**」。
3.  在「**目標(T)**」欄位中，將其內容 **完全取代** 為以下路徑：
    ```
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\\chrome-debug-profile"
    ```
    > **注意**: `--user-data-dir` 參數會讓 Chrome 在 C 槽建立一個全新的設定檔資料夾 `chrome-debug-profile`，用以儲存此模式下的登入資訊，與您原本的 Chrome 環境完全隔離。

## 💡 使用流程

### 首次設定 (只需做一次)

1.  **徹底關閉**所有正在執行的 Chrome 和 Edge 瀏覽器。
2.  點兩下您剛剛建立的 **"Chrome (Debug Mode)"** 捷徑來啟動瀏覽器。
3.  在這個「乾淨」的 Chrome 視窗中，手動前往 `tixcraft.com`，**登入您的帳號**，並勾選「記住我」。
4.  登入成功後，關閉此瀏覽器。您的登入狀態現在已經被保存在 `C:\\chrome-debug-profile` 中了。

### 執行搶票

1.  **修改設定**: 打開 `bot.py` 檔案，根據您的需求修改檔案頂部的 `TARGET_URL`, `TARGET_DATE`, `SEAT_WISHLIST`, `TICKET_COUNT` 等參數。
2.  **啟動偵錯瀏覽器**: 徹底關閉所有 Chrome/Edge 瀏覽器後，點兩下 **"Chrome (Debug Mode)"** 捷徑。
3.  **執行機器人**: 在已啟用虛擬環境的 PowerShell 終端機中，執行以下指令：
    ```powershell
    python bot.py
    ```
4.  機器人將會自動接管已開啟的瀏覽器分頁，並開始執行搶票任務。