import requests
import json
import os
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT_DIR, "wm_rating.txt")

# 檢查檔案是否存在
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("")

BotTokenWM = os.environ.get("BOT_TOKEN_WM")
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.telegram.org")
CHAT_ID = os.environ.get("TG_CHAT_ID")
WM_ACCOUNT = os.environ.get("WM_ACCOUNT")

def get_api(userId):
    url = f"https://api.gamer.com.tw/acg/v1/reviews_user.php?userId={userId}&sort=4"
    json_data = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}).text
    # print(json_data)
    j = json.loads(json_data)['data']['list']
    # print(j)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        old = f.read().split("\n")
    for i in j:
        it = i[0]
        a_id = it['id']
        if a_id in old:
            continue
        ctime = it['ctime']
        content = it['content'].replace("微妙", "<b>微妙</b>")

        reviews = it['reviews']
        r_name = reviews['name']
        r_id = reviews['id']
        r_rating = reviews['rating']
        print(r_name, r_rating)
        r_type = reviews['dc_type']['title']

        publisher = it['publisher']
        p_name = publisher['name']
        p_id = publisher['id']
        send_data = f"<a href='https://wall.gamer.com.tw/user.php?userId={p_id}'>{p_name}</a>\n評價了\n<a href='https://wall.gamer.com.tw/fanpage.php?sn={r_id}'>{r_name}({r_type})</a> {r_rating}分\n<blockquote>{content}</blockquote>\n——————————\n#微妙哥\n<blockquote>時間： {ctime}\n貼文： <a href='https://wall.gamer.com.tw/post.php?sn={a_id}'>{a_id}</a></blockquote>"
        # print(send_data)
        # print("---------------------------------\n")
        rtn = send_tg_message(CHAT_ID, "192", send_data)
        if rtn:
            with open(DATA_FILE, "a", encoding="utf-8") as f:
                f.write(f"{a_id}\n")
        else:
            print("Telegram 傳送失敗。")

# Telegram 傳送訊息函數（重試機制）
def send_tg_message(chat_id, thread_id, text, parse_mode="HTML", retry=0):
    if retry > 3:
        return False
    url = f"{API_BASE_URL}/bot{BotTokenWM}/sendMessage"
    data = {
        "chat_id": chat_id,
        "message_thread_id": thread_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }
    response = requests.post(url, data=data)
    if response.ok:
        return True
    print(response.text)
    print(data)
    response_json = json.loads(response.text)
    if response_json['error_code'] == 429:
        try:
            need_sleep = response_json['parameters']['retry_after']
            print(f"請求被限制，等待 {need_sleep} 秒鐘後再重試。")
            time.sleep(need_sleep)
        except:
            time.sleep(30)
    return send_tg_message(chat_id, thread_id, text, parse_mode, retry + 1)

get_api(WM_ACCOUNT)
