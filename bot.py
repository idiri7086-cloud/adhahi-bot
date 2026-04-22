import os
import json
import logging
import asyncio
import requests
from telebot import TeleBot
from playwright.async_api import async_playwright

# ====== CONFIG ======
BOT_TOKEN = os.getenv("8594674187:AAF-X2MEcEs8U2MtGDHiRnZhFacojYyjVDU")
CHAT_ID = os.getenv("7367592776")
CHECK_INTERVAL = 600
DATA_FILE = "state.json"
SITE_URL = "https://adhahi.dz/register"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = TeleBot(BOT_TOKEN)

WILAYAS = [
    "أدرار","الشلف","الأغواط","أم البواقي","باتنة","بجاية","بسكرة","بشار","البليدة","البويرة",
    "تمنراست","تبسة","تلمسان","تيارت","تيزي وزو","الجزائر","الجلفة","جيجل","سطيف","سعيدة",
    "سكيكدة","سيدي بلعباس","عنابة","قالمة","قسنطينة","المدية","مستغانم","المسيلة","معسكر","ورقلة",
    "وهران","البيض","إليزي","برج بوعريريج","بومرداس","الطارف","تندوف","تسمسيلت","الوادي","خنشلة",
    "سوق أهراس","تيبازة","ميلة","عين الدفلى","النعامة","عين تموشنت","غرداية","غليزان","تيميمون","برج باجي مختار",
    "أولاد جلال","بني عباس","عين صالح","عين قزام","تقرت","جانت","المغير","المنيعة"
]

# ====== FILE ======
def load_status():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_status(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

# ====== SCRAPER ======
async def check_site():
    result = {}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ]
            )

            page = await browser.new_page()
            await page.goto(SITE_URL, timeout=60000)
            await page.wait_for_timeout(5000)

            content = await page.content()

            for w in WILAYAS:
                if w in content:
                    if "حجز متوفر" in content:
                        result[w] = True
                    else:
                        result[w] = False

            await browser.close()

    except Exception as e:
        logger.error(f"Error: {e}")

    return result

# ====== COMMANDS ======
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🚀 البوت يعمل!\n\n/status\n/list")

@bot.message_handler(commands=['status'])
def status(msg):
    data = load_status()
    available = [w for w, s in data.items() if s]

    if available:
        bot.reply_to(msg, "✅ المتوفر:\n" + "\n".join(available))
    else:
        bot.reply_to(msg, "❌ لا يوجد متوفر")

@bot.message_handler(commands=['list'])
def list_all(msg):
    data = load_status()

    if not data:
        bot.reply_to(msg, "⏳ جاري جمع البيانات...")
        return

    text = ""
    for w, s in data.items():
        text += f"{w} {'✅' if s else '❌'}\n"

    bot.reply_to(msg, text)

# ====== LOOP ======
async def monitor():
    bot.send_message(CHAT_ID, "🚀 تم تشغيل البوت")

    while True:
        data = await check_site()

        if data:
            save_status(data)

        await asyncio.sleep(CHECK_INTERVAL)

# ====== RUN ======
import threading

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot).start()

asyncio.run(monitor())    """
    available_states = {}
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        # This is a placeholder for the actual API endpoint if discovered
        response = requests.get(API_URL, headers=headers, timeout=20, verify=False)
        if response.status_code == 200:
            data = response.json()
            # Logic to parse API data
            for item in data:
                name = item.get('name_ar') or item.get('name')
                status = item.get('available') or item.get('status') == 'active'
                if name in WILAYAS:
                    available_states[name] = status
    except Exception as e:
        logger.error(f"API fallback error: {e}")
    
    return available_states

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 مرحباً! أنا بوت مراقبة منصة أضاحي (adhahi.dz).\n\nأقوم بمراقبة جميع الولايات الـ 58 على مدار الساعة وإرسال تنبيهات فورية عند توفر الحجز.\n\nالأوامر:\n/status - الولايات المتوفرة حالياً\n/list - حالة جميع الولايات")

@bot.message_handler(commands=['status'])
def send_status(message):
    current_status = load_status()
    available = [w for w, s in current_status.items() if s]
    if available:
        msg = "✅ الولايات المتوفرة حالياً:\n" + "\n".join([f"- {w}" for w in available])
        msg += f"\n\nرابط التسجيل: {SITE_URL}"
    else:
        msg = "❌ لا توجد ولايات متوفرة حالياً."
    bot.reply_to(message, msg)

@bot.message_handler(commands=['list'])
def send_list(message):
    current_status = load_status()
    if not current_status:
        bot.reply_to(message, "جاري جمع البيانات، يرجى المحاولة بعد قليل...")
        return
        
    msg = "📊 حالة جميع الولايات:\n"
    sorted_wilayas = sorted(current_status.keys())
    for i, wilaya in enumerate(sorted_wilayas, 1):
        status_icon = "✅" if current_status[wilaya] else "❌"
        msg += f"{i}. {wilaya}: {status_icon}\n"
        if i % 30 == 0:
            bot.send_message(message.chat.id, msg)
            msg = ""
    if msg:
        bot.send_message(message.chat.id, msg)

async def monitor_loop():
    logger.info("Starting monitor loop...")
    first_run = not os.path.exists(DATA_FILE)
    
    try:
        bot.send_message(CHAT_ID, "🚀 تم تشغيل البوت بنجاح! جاري مراقبة جميع الولايات في موقع أضاحي.")
    except Exception as e:
        logger.error(f"Startup message error: {e}")

    while True:
        try:
            current_status = load_status()
            new_status = await check_site_playwright()
            
            if not new_status:
                logger.warning("Could not fetch status, retrying in 30s...")
                await asyncio.sleep(30)
                continue

            changes = False
            notifications = []
            
            for wilaya, is_available in new_status.items():
                old_available = current_status.get(wilaya, False)
                
                if is_available and not old_available:
                    if not first_run:
                        notifications.append(f"🎉 **تنبيه!** توفر الحجز في ولاية: **{wilaya}**\n🔗 سجل الآن: {SITE_URL}")
                    changes = True
                elif not is_available and old_available:
                    if not first_run:
                        notifications.append(f"⚠️ **تنبيه:** تم إغلاق الحجز في ولاية: **{wilaya}**")
                    changes = True
            
            if first_run:
                available_count = sum(1 for s in new_status.values() if s)
                available_names = [w for w, s in new_status.values() if s]
                start_msg = f"📊 الحالة الأولية:\nعدد الولايات المتوفرة: {available_count}\n"
                if available_names:
                    start_msg += "الولايات: " + ", ".join(available_names)
                bot.send_message(CHAT_ID, start_msg)
                first_run = False
                changes = True

            for note in notifications:
                bot.send_message(CHAT_ID, note, parse_mode="Markdown")
                await asyncio.sleep(1) # Avoid spamming

            if changes:
                save_status(new_status)
                
        except Exception as e:
            logger.error(f"Monitor loop error: {e}")
            await asyncio.sleep(30)
            
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    import threading
    
    # Run bot polling in a separate thread
    def run_bot():
        bot.infinity_polling()
        
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run the async monitor loop
    asyncio.run(monitor_loop())
