from playwright.sync_api import sync_playwright, Playwright
import logging
import time
import sys

# --- Log 設定 ---
# 建立一個 logger
logger = logging.getLogger('TicketBotLogger')
logger.setLevel(logging.INFO) # 設定 logger 的最低等級

# 建立檔案處理器 (FileHandler)，將日誌寫入檔案
# 'w' 表示每次執行都覆蓋舊檔案，'utf-8' 確保能處理中文
file_handler = logging.FileHandler('bot.log', 'w', 'utf-8')
file_handler.setLevel(logging.INFO)

# 建立控制台處理器 (StreamHandler)，將日誌輸出到螢幕
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# 建立格式器 (Formatter) 並設定給處理器
# 格式：時間 - Logger名稱 - 等級 - 訊息
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 將處理器加入 logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 防止日誌訊息重複輸出
logger.propagate = False
# --- Log 設定結束 ---

# --- 設定區 ---
TARGET_URL = "https://tixcraft.com/activity/game/25_dellatp"
TARGET_DATE = "2025/11/16"
SEAT_WISHLIST = ["夜貓狂歡 特A區", "夜貓狂歡 特B區", "不眠派對 特C區", "紅2C區", "黃2B區"]
TICKET_COUNT = 2

class TicketBot:
    def __init__(self, target_url, target_date, seat_wishlist, ticket_count):
        self.target_url = target_url
        self.target_date = target_date
        self.seat_wishlist = seat_wishlist
        self.ticket_count = ticket_count

    def navigate_and_select_seats(self, page):
        # 步驟 1: 前往活動頁面
        logger.info(f"正在前往活動頁面: {self.target_url}")
        page.goto(self.target_url)

        # 步驟 2: 選擇場次日期 (如果需要)
        logger.info(f"正在尋找並點擊場次: {self.target_date}")
        try:
            date_row = page.locator("tr", has_text=self.target_date)
            purchase_button = date_row.get_by_role("button", name="立即訂購")
            logger.info("找到購票按鈕，正在點擊...")
            purchase_button.click()
            logger.info(f"成功點擊場次: {self.target_date}")
        except Exception as e:
            logger.error(f"點擊日期 '{self.target_date}' 失敗，將直接嘗試選擇區域。", exc_info=True)

        # 步驟 3: 根據願望清單選擇區域
        logger.info("進入區域選擇頁面，將依據願望清單嘗試點擊...")
        
        seat_found = False
        for seat_area in self.seat_wishlist:
            try:
                # 新的定位策略：尋找一個包含願望清單文字、但又不包含 "已售完" 的連結。
                # 這能更精準地找到可點擊的區域。
                area_locator = page.locator(
                    f"//a[contains(normalize-space(.), '{seat_area}') and not(contains(., '已售完'))]"
                )
                
                # 直接嘗試點擊，Playwright 的 click 會自動等待元素出現並可被點擊
                # 我們設定一個較短的超時(3秒)，如果3秒內點不到就換下一個志願
                logger.info(f"正在嘗試點擊志願: '{seat_area}'")
                area_locator.first.click(timeout=3000)
                
                logger.info(f"成功點擊 '{seat_area}'!")
                seat_found = True
                break # 點到了就跳出迴圈
            except Exception:
                logger.warning(f"'{seat_area}' 無法點擊或找不到，嘗試下一個志願...")
                
        if not seat_found:
            logger.critical("願望清單中的所有區域都無法選擇，腳本結束。")
            page.close()
            return

        # --- 後續步驟 ---
        logger.info("成功進入下一步！")
        page.wait_for_load_state() # 等待新頁面載入

    def set_tickets_and_checkout(self, page):
        # 步驟 4: 設定票數
        logger.info(f"正在設定票數為: {self.ticket_count}")
        
        # 新策略：使用下拉選單設定票數
        # 根據使用者提供的 element，我們定位 class 為 'form-select' 的 <select> 標籤
        ticket_selector = page.locator("select.form-select")
        
        # 等待下拉選單出現
        ticket_selector.wait_for(state="visible", timeout=5000)

        # 直接選擇指定的票數，注意 select_option 的值需要是字串
        ticket_selector.select_option(str(self.ticket_count))
        
        logger.info(f"成功從下拉選單將票數設定為: {self.ticket_count}")

        # 步驟 5: 處理驗證碼 (手動輸入)
        logger.info("等待使用者手動輸入驗證碼...")
        try:
            captcha_input = page.locator("#TicketForm_verifyCode")
            captcha_input.wait_for(timeout=10000) # 等待輸入框出現
            captcha_code = input("請在瀏覽器中查看驗證碼，並在此手動輸入後按下 Enter: ")
            captcha_input.fill(captcha_code)
            logger.info("驗證碼已填寫。")
        except Exception as e:
            logger.error("找不到或填寫驗證碼輸入框時發生錯誤", exc_info=True)

        # 步驟 6: 同意條款並提交
        try:
            logger.info("正在勾選同意條款...")
            page.locator("#TicketForm_agree").check()
            logger.info("已勾選同意條款。")

            logger.info("準備點擊 '確認張數' 按鈕...")
            # 根據使用者提供的最新 element, 我們點擊 "確認張數" 按鈕
            submit_button = page.get_by_role("button", name="確認張數")
            submit_button.click()

        except Exception as e:
            logger.error(f"勾選同意或點擊 '確認張數' 時失敗: {e}")

        logger.info("腳本執行完畢，若成功，應已在結帳頁面。")
        # logger.info(f"瀏覽器將在 {self.close_browser_delay} 秒後自動關閉。") # 已移除
        # time.sleep(self.close_browser_delay / 1000) # 已移除

def run(playwright: Playwright, bot: TicketBot) -> None:
    """主執行函式"""
    
    logger.info("--- 機器人啟動 (遠端連線模式) ---")
    logger.info("--- 請先手動開啟帶有 --remote-debugging-port=9222 參數的 Chrome ---")
    logger.info(f"目標網址: {bot.target_url}")
    logger.info(f"目標日期: {bot.target_date}")
    logger.info(f"座位願望清單: {bot.seat_wishlist}")
    logger.info(f"預計票數: {bot.ticket_count}")

    try:
        # 連接到您手動開啟的 Chrome 瀏覽器
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0] # 取得預設的瀏覽器上下文
        page = context.new_page() # 開啟一個新的分頁來執行任務
        
        logger.info("成功連線到現有的 Chrome 瀏覽器！")

    except Exception as e:
        logger.critical(f"無法連線到指定的 Chrome 瀏覽器(http://localhost:9222)。")
        logger.critical("請確認：1. 所有其他的 Chrome 都已關閉。 2. 您是透過帶有 --remote-debugging-port=9222 參數的捷徑啟動 Chrome。")
        logger.critical(f"錯誤訊息: {e}")
        return

    # 隱身措施在這種模式下不再必要，因為我們用的是真實的瀏覽器設定
    # stealth_sync(page) 
    page.set_viewport_size({"width": 1920, "height": 1080})

    bot.navigate_and_select_seats(page)
    bot.set_tickets_and_checkout(page)

    logger.info("腳本執行完畢，若成功，應已在結帳頁面。")
    # logger.info(f"瀏覽器將在 {self.close_browser_delay} 秒後自動關閉。") # 已移除
    # time.sleep(self.close_browser_delay / 1000) # 已移除
    context.close()

if __name__ == "__main__":
    # USER_DATA_DIR 的設定在此模式下已不需要
    bot_config = TicketBot(
        target_url=TARGET_URL,
        target_date=TARGET_DATE,
        seat_wishlist=SEAT_WISHLIST,
        ticket_count=TICKET_COUNT,
    )
    with sync_playwright() as playwright:
        run(playwright, bot_config) 