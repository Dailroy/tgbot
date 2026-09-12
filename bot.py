import asyncio
import random
import string
import json
import os
import io
import time
from urllib.parse import quote
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "8815886549:AAFBBHdJa-2P5dvxPqBiaFQxoSJ2DYZC758"
OWNER = "qituh"

CHANNELS = [
    {"id": "@APKSOFTERA", "link": "https://t.me/APKSOFTERA"},
    {"id": "@jdkdkdoskcjfj", "link": "https://t.me/jdkdkdoskcjfj"},
]

PROMOS_FILE = "D:\\telegram_bot\\promos.json"
USERS_FILE = "D:\\telegram_bot\\users.json"
USERNAMES_FILE = "D:\\telegram_bot\\usernames.json"

GIFS = {
    "welcome": "https://media.giphy.com/media/26ufdipQqU2hNA4Gc/giphy.gif",
    "hack": "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",
    "loading": "https://media.giphy.com/media/VbnUQpnihPSIgIXuZv/giphy.gif",
    "denied": "https://media.giphy.com/media/l0MYt5jPRMQifVjbG/giphy.gif",
    "vip": "https://media.giphy.com/media/3o6gE8l2n7H2p6ZXMs/giphy.gif",
    "takedown": "https://media.giphy.com/media/3o7aD2GcO5E7W2W3nG/giphy.gif",
}

FIRST_NAMES = [
    "Александр","Дмитрий","Максим","Сергей","Андрей","Алексей","Артём","Илья",
    "Кирилл","Михаил","Никита","Матвей","Роман","Егор","Арсений","Иван",
    "Денис","Евгений","Тимофей","Владислав","Тарас","Павел","Даниил","Степан",
    "Антон","Олег","Мария","Анна","Елена","Дарья","Полина","Алина",
    "Арина","Екатерина","Софья","Настя","Виктория","Марина","Юлия","Татьяна"
]
LAST_NAMES = [
    "Иванов","Петров","Сидоров","Козлов","Новиков","Морозов","Волков","Зайцев",
    "Попов","Соколов","Лебедев","Кузнецов","Фёдоров","Михайлов","Белов","Комаров"
]
STREETS = [
    "ул. Пушкина","ул. Ленина","ул. Гагарина","ул. Мира","ул. Победы",
    "ул. Свободы","ул. Мичурина","ул. Чехова","ул. Толстого","ул. Достоевского"
]
CITIES = [
    "Москва","Санкт-Петербург","Новосибирск","Екатеринбург","Казань",
    "Нижний Новгород","Челябинск","Самара","Омск","Ростов-на-Дону"
]
COUNTRIES = ["Россия","Украина","Беларусь","Казахстан"]
CARRIER = {"MTS": "🟡", "Билайн": "⚫", "МегаФон": "🟢", "Теле2": "🔵"}


# ─── DATA persistence ──────────────────────────────────

def load_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_promos():
    if os.path.exists(PROMOS_FILE):
        return
    durations = {
        "1d": 86400,
        "3d": 259200,
        "7d": 604800,
        "14d": 1209600,
        "30d": 2592000,
    }
    promos = {}
    for _ in range(10):
        code = "VIP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        promos[code] = {"duration": "1d", "seconds": durations["1d"], "used": False}
    for _ in range(10):
        code = "VIP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        promos[code] = {"duration": "3d", "seconds": durations["3d"], "used": False}
    for _ in range(10):
        code = "VIP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        promos[code] = {"duration": "7d", "seconds": durations["7d"], "used": False}
    for _ in range(10):
        code = "VIP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        promos[code] = {"duration": "14d", "seconds": durations["14d"], "used": False}
    for _ in range(10):
        code = "VIP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        promos[code] = {"duration": "30d", "seconds": durations["30d"], "used": False}
    save_json(PROMOS_FILE, promos)


def get_user_vip(user_id):
    users = load_json(USERS_FILE)
    u = users.get(str(user_id), {})
    vip_until = u.get("vip_until", 0)
    if vip_until and time.time() < vip_until:
        remaining = vip_until - time.time()
        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        mins = int((remaining % 3600) // 60)
        return True, f"{days}д {hours}ч {mins}м"
    return False, ""


def set_user_vip(user_id, seconds):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    if uid not in users:
        users[uid] = {}
    current = users[uid].get("vip_until", 0)
    now = time.time()
    if current > now:
        users[uid]["vip_until"] = current + seconds
    else:
        users[uid]["vip_until"] = now + seconds
    save_json(USERS_FILE, users)


# ─── HELPERS ───────────────────────────────────────────

async def send_gif(chat, key, caption, reply_markup=None, parse_mode="Markdown"):
    try:
        return await chat.send_animation(
            animation=GIFS[key], caption=caption,
            reply_markup=reply_markup, parse_mode=parse_mode
        )
    except Exception:
        return await chat.send_message(
            text=caption, reply_markup=reply_markup, parse_mode=parse_mode
        )


def is_subscribed(context, user_id):
    return context.user_data.get(f"sub_{user_id}", False)


def sub_keyboard():
    buttons = []
    for i, ch in enumerate(CHANNELS):
        buttons.append([InlineKeyboardButton(f"📢 {ch['id']}", url=ch["link"])])
        buttons.append([InlineKeyboardButton(f"✅ Подписался на {ch['id']}", callback_data=f"sub_{i}")])
    return InlineKeyboardMarkup(buttons)


def main_menu_kb():
    buy_link = "https://t.me/qituh?text=" + quote("Здравствуйте хочу купить випку")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💣 Снос", callback_data="takedown"),
         InlineKeyboardButton("🔍 Доксинг", callback_data="doxing")],
        [InlineKeyboardButton("⚡ DDoS Атака", callback_data="ddos"),
         InlineKeyboardButton("📞 Бомбер", callback_data="bomber")],
        [InlineKeyboardButton("⭐ ВИП", callback_data="vip"),
         InlineKeyboardButton("💳 Купить VIP", url=buy_link)]
    ])


def gen_data(target):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return {
        "target": target, "first": first, "last": last,
        "age": random.randint(14, 65),
        "birthday": f"{random.randint(1,28):02d}.{random.randint(1,12):02d}.{random.randint(1960,2008)}",
        "country": random.choice(COUNTRIES), "city": random.choice(CITIES),
        "street": random.choice(STREETS), "house": random.randint(1, 200), "flat": random.randint(1, 500),
        "phone": f"+7 ({random.randint(900,999)}) {random.randint(100,999)}-{random.randint(10,99)}-{random.randint(10,99)}",
        "carrier": random.choice(list(CARRIER.keys())),
        "ip": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
        "mac": ":".join(f"{random.randint(0,255):02X}" for _ in range(6)),
        "email": f"{first.lower()}.{last.lower()}{random.randint(1,999)}@{'gmail' if random.random()>0.5 else 'mail'}.ru",
        "user": target if not target.startswith("+") else f"{first.lower()}{random.randint(100,9999)}",
        "passport": f"{random.randint(10,99)} {random.randint(10,99)} {random.randint(100000,999999)}",
        "inn": f"{random.randint(1000000000,9999999999)}",
    }


def make_html(d):
    return f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8"><title>Dox — {d['target']}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0a0a0a;color:#00ff41;font-family:'Courier New',monospace;padding:20px}}
.c{{max-width:700px;margin:0 auto;border:2px solid #00ff41;border-radius:10px;padding:30px;background:#0d0d0d;box-shadow:0 0 30px rgba(0,255,65,.2)}}
h1{{text-align:center;font-size:28px;margin-bottom:10px;text-shadow:0 0 20px #00ff41;animation:g 2s infinite}}
@keyframes g{{0%,100%{{text-shadow:0 0 20px #00ff41}}50%{{text-shadow:0 0 40px #00ff41,0 0 80px #00ff41}}}}
.sub{{text-align:center;color:#00aa2a;margin-bottom:30px;font-size:14px}}
.s{{background:#111;border:1px solid #00ff41;border-radius:8px;padding:15px;margin-bottom:15px}}
.s h2{{color:#00ff41;font-size:16px;margin-bottom:10px;border-bottom:1px solid #00aa2a;padding-bottom:5px}}
.r{{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px dashed #1a1a1a}}
.l{{color:#00aa2a}}.v{{color:#fff;font-weight:bold}}
.f{{text-align:center;margin-top:20px;color:#00aa2a;font-size:12px}}
</style></head><body><div class="c">
<h1>&#9760; DOX REPORT &#9760;</h1>
<p class="sub">target: {d['target']}</p>
<div class="s"><h2>&#128100; PERSONAL</h2>
<div class="r"><span class="l">Имя:</span><span class="v">{d['first']}</span></div>
<div class="r"><span class="l">Фамилия:</span><span class="v">{d['last']}</span></div>
<div class="r"><span class="l">ДР:</span><span class="v">{d['birthday']} ({d['age']} лет)</span></div>
<div class="r"><span class="l">Паспорт:</span><span class="v">{d['passport']}</span></div>
<div class="r"><span class="l">ИНН:</span><span class="v">{d['inn']}</span></div></div>
<div class="s"><h2>&#128205; LOCATION</h2>
<div class="r"><span class="l">Страна:</span><span class="v">{d['country']}</span></div>
<div class="r"><span class="l">Город:</span><span class="v">{d['city']}</span></div>
<div class="r"><span class="l">Адрес:</span><span class="v">{d['street']}, д.{d['house']}, кв.{d['flat']}</span></div></div>
<div class="s"><h2>&#128241; CONTACTS</h2>
<div class="r"><span class="l">Тел:</span><span class="v">{d['phone']}</span></div>
<div class="r"><span class="l">Оператор:</span><span class="v">{CARRIER[d['carrier']]} {d['carrier']}</span></div>
<div class="r"><span class="l">Email:</span><span class="v">{d['email']}</span></div>
<div class="r"><span class="l">Username:</span><span class="v">@{d['user']}</span></div></div>
<div class="s"><h2>&#127760; NETWORK</h2>
<div class="r"><span class="l">IP:</span><span class="v">{d['ip']}</span></div>
<div class="r"><span class="l">MAC:</span><span class="v">{d['mac']}</span></div></div>
<div class="f">&#9760; DARK DOXER &#9760;</div>
</div></body></html>"""


# ─── START ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    if user.username:
        usernames = load_json(USERNAMES_FILE)
        usernames[user.username.lower()] = user_id
        save_json(USERNAMES_FILE, usernames)
    if is_subscribed(context, user_id):
        await send_gif(
            update.message.chat, "welcome",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "      ☠  *D A R K  D O X E R*  ☠\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "   Добро пожаловать в тёмную зону.\n"
            "   Выбери действие из меню ↓\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=main_menu_kb()
        )
    else:
        await send_gif(
            update.message.chat, "welcome",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "      ☠  *D A R K  D O X E R*  ☠\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "   Для использования бота\n"
            "   подпишись на каналы и нажми\n"
            "   кнопку подтверждения:\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=sub_keyboard()
        )


# ─── SUBSCRIPTION ──────────────────────────────────────

async def sub_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    idx = int(query.data.split("_")[1])
    context.user_data[f"sub_{user_id}_{idx}"] = True
    try:
        await query.answer("✅ Отмечено!")
    except Exception:
        pass
    all_done = all(context.user_data.get(f"sub_{user_id}_{i}", False) for i in range(len(CHANNELS)))
    if all_done:
        context.user_data[f"sub_{user_id}"] = True
        try:
            await query.message.delete()
        except Exception:
            pass
        await send_gif(
            query.message.chat, "welcome",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "      ☠  *D A R K  D O X E R*  ☠\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "   ✅ Подписка подтверждена!\n"
            "   Добро пожаловать в тёмную зону.\n"
            "   Выбери действие из меню ↓\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=main_menu_kb()
        )
    else:
        done = sum(1 for i in range(len(CHANNELS)) if context.user_data.get(f"sub_{user_id}_{i}", False))
        try:
            await query.answer(f"✅ {done}/{len(CHANNELS)} каналов подтверждено. Подпишись на остальные!", show_alert=True)
        except Exception:
            pass


# ─── BUTTONS ───────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    chat = update.effective_chat
    user = update.effective_user
    if user.username:
        usernames = load_json(USERNAMES_FILE)
        usernames[user.username.lower()] = user.id
        save_json(USERNAMES_FILE, usernames)

    if data.startswith("sub_"):
        await sub_handler(update, context)
        return

    try:
        await query.answer()
    except Exception:
        pass

    user_id = update.effective_user.id
    if not is_subscribed(context, user_id):
        try:
            await query.answer("❌ Сначала подпишись на каналы!", show_alert=True)
        except Exception:
            pass
        return

    active, _ = get_user_vip(user_id)

    if data == "takedown":
        if not active:
            await handle_no_vip(chat)
            return
        await handle_takedown_menu(chat)
    elif data in ("takedown_users", "takedown_group", "takedown_channel", "takedown_bot"):
        if not active:
            await handle_no_vip(chat)
            return
        labels = {"takedown_users": "👤 Пользователя", "takedown_group": "👥 Группу",
                  "takedown_channel": "📢 Канал", "takedown_bot": "🤖 Бота"}
        await start_takedown(chat, context, labels[data])
    elif data == "doxing":
        if not active:
            await handle_no_vip(chat)
            return
        await start_doxing(chat, context)
    elif data in ("ddos", "bomber"):
        if not active:
            await handle_no_vip(chat)
            return
        labels = {"ddos": "⚡ DDoS АТАКА", "bomber": "📞 БОМБЕР"}
        await handle_premium(chat, labels[data])
    elif data == "vip":
        await handle_vip(chat, update.effective_user.id)
    elif data.startswith("vipbuy_"):
        await handle_vip_buy(query, data)
    elif data.startswith("dl_"):
        await handle_download(query, context)
    elif data == "back":
        try:
            await query.message.delete()
        except Exception:
            pass
        await chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "      ☠  *D A R K  D O X E R*  ☠\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "   Выбери действие из меню ↓\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=main_menu_kb(), parse_mode="Markdown"
        )
    elif data == "back_takedown":
        try:
            await query.message.delete()
        except Exception:
            pass
        await handle_takedown_menu(chat)


# ─── PROMO CODES ───────────────────────────────────────

async def start_promo(chat, context):
    context.user_data["awaiting_promo"] = True
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Назад", callback_data="back")]
    ])
    await chat.send_message(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "       🎟 *ПРОМОКОДЫ*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "   Введи промокод для активации\n"
        "   VIP-подписки:\n\n"
        "   📌 Формат: `VIP-XXXXXXXX`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard, parse_mode="Markdown"
    )


async def activate_promo(user_id, code):
    promos = load_json(PROMOS_FILE)
    code = code.strip().upper()
    if code not in promos:
        return False, "Промокод не найден!"
    if promos[code]["used"]:
        return False, "Этот промокод уже был использован!"
    promos[code]["used"] = True
    promos[code]["used_by"] = user_id
    save_json(PROMOS_FILE, promos)
    set_user_vip(user_id, promos[code]["seconds"])
    return True, promos[code]["duration"]


# ─── TAKEDOWN ──────────────────────────────────────────

async def handle_takedown_menu(chat):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Пользователь (User)", callback_data="takedown_users")],
        [InlineKeyboardButton("👥 Группа (Group)", callback_data="takedown_group")],
        [InlineKeyboardButton("📢 Канал (Channel)", callback_data="takedown_channel")],
        [InlineKeyboardButton("🤖 Бот (Bot)", callback_data="takedown_bot")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")]
    ])
    await chat.send_message(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "       💣 *СНОС*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "   Выбери цель для сноса:\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard, parse_mode="Markdown"
    )


async def start_takedown(chat, context, target_type):
    context.user_data["awaiting_takedown"] = True
    context.user_data["takedown_type"] = target_type
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Назад", callback_data="back_takedown")]
    ])
    await chat.send_message(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"       💣 *СНОС {target_type.upper()}*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "   Введи юзернейм или ссылку\n\n"
        "   📌 Пример: `@username`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard, parse_mode="Markdown"
    )


async def run_takedown(chat, target, context):
    takedown_type = context.user_data.get("takedown_type", "Цель")
    total = random.randint(500, 700)
    failed = random.randint(30, 80)
    sent = total - failed

    msg = await send_gif(
        chat, "takedown",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"       💣 *СНОС {takedown_type.upper()}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"   🎯 *Цель:* `{target}`\n\n"
        f"   ⚡ Отправка жалоб...\n\n"
        f"   `[■□□□□□□□□□] 10%`\n"
        f"   📝 Жалоба #1 из {total}..."
    )
    bars = [
        (15, "`[■■□□□□□□□□] 15%`", f"📝 Жалоба #{int(total*0.15)} — Спам"),
        (30, "`[■■■■□□□□□□] 30%`", f"📝 Жалоба #{int(total*0.30)} — Нарушение правил"),
        (45, "`[■■■■■■□□□□] 45%`", f"📝 Жалоба #{int(total*0.45)} — Мошенничество"),
        (60, "`[■■■■■■■■□□] 60%`", f"📝 Жалоба #{int(total*0.60)} — Преследование"),
        (75, "`[■■■■■■■■■□] 75%`", f"📝 Жалоба #{int(total*0.75)} — Угрозы"),
        (90, "`[■■■■■■■■■■] 90%`", f"📝 Жалоба #{int(total*0.90)} — Финал..."),
        (100, "`[■■■■■■■■■■] 100%`", f"✅ Отправлено {sent} жалоб из {total}!"),
    ]
    for bar_pct, bar, stage in bars:
        await asyncio.sleep(random.uniform(1.0, 2.0))
        try:
            await msg.edit_caption(
                caption=(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"       💣 *СНОС {takedown_type.upper()}*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"   🎯 *Цель:* `{target}`\n\n"
                    f"   ⚡ Отправка жалоб...\n\n"
                    f"   {bar}\n"
                    f"   {stage}"
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass
    await asyncio.sleep(1.5)
    try:
        await msg.delete()
    except Exception:
        pass
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Меню", callback_data="back")]
    ])
    await chat.send_message(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"       💣 *СНОС ЗАВЕРШЁН*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"   🎯 *Цель:* `{target}`\n"
        f"   📋 *Тип:* {takedown_type}\n\n"
        f"   ✅ *Статус:* Успешно\n"
        f"   📝 *Жалоб:* {sent}/{total}\n"
        f"   ❌ *Ошибок:* {failed}\n"
        f"   ⏱ *Время:* {random.randint(30,120)}с\n\n"
        f"   🔔 Результат будет рассмотрен\n"
        f"   в течение 24-72 часов.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard, parse_mode="Markdown"
    )


# ─── DOXING ────────────────────────────────────────────

async def start_doxing(chat, context):
    context.user_data["awaiting_dox"] = True
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Назад", callback_data="back")]
    ])
    await chat.send_message(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "       🔍 *DOXING MODULE*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "   Введи юзернейм или номер телефона\n"
        "   того, кого нужно задоксить:\n\n"
        "   📌 Пример: `@username` или `+79001234567`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard, parse_mode="Markdown"
    )


async def run_doxing(chat, target, context):
    msg = await send_gif(
        chat, "hack",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"       🔍 *DOXING MODULE*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"   🎯 *Цель:* `{target}`\n\n"
        f"   `[■□□□□□□□□□] 10%`\n"
        f"   🔍 Сканирование баз данных..."
    )
    progress = [
        ("`[■■■□□□□□□□] 30%`", "📡 Перехват пакетов..."),
        ("`[■■■■■□□□□□] 50%`", "🌐 Трассировка IP..."),
        ("`[■■■■■■■□□□] 70%`", "🔓 Дешифровка данных..."),
        ("`[■■■■■■■■■□] 90%`", "📋 Формирование отчёта..."),
        ("`[■■■■■■■■■■] 100%`", "✅ Данные собраны!"),
    ]
    for bar, stage in progress:
        await asyncio.sleep(1.2)
        try:
            await msg.edit_caption(
                caption=(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"       🔍 *DOXING MODULE*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"   🎯 *Цель:* `{target}`\n\n"
                    f"   {bar}\n"
                    f"   {stage}"
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass
    await asyncio.sleep(1.5)
    try:
        await msg.delete()
    except Exception:
        pass
    d = gen_data(target)
    context.user_data["dox"] = d
    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "       🔍 *DOX RESULT*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"   🎯 *Цель:* `{target}`\n\n"
        f"   👤 *Имя:* {d['first']} {d['last']}\n"
        f"   🎂 *ДР:* {d['birthday']} ({d['age']} лет)\n"
        f"   📍 *Страна:* {d['country']}\n"
        f"   🏙 *Город:* {d['city']}\n"
        f"   🏠 *Адрес:* {d['street']}, д.{d['house']}, кв.{d['flat']}\n\n"
        f"   📱 *Телефон:* `{d['phone']}`\n"
        f"   📡 *Оператор:* {CARRIER[d['carrier']]} {d['carrier']}\n"
        f"   📧 *Email:* `{d['email']}`\n"
        f"   👤 *Username:* @{d['user']}\n\n"
        f"   🌐 *IP:* `{d['ip']}`\n"
        f"   🔗 *MAC:* `{d['mac']}`\n"
        f"   🪪 *Паспорт:* `{d['passport']}`\n"
        f"   🔢 *ИНН:* `{d['inn']}`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Скачать HTML", callback_data="dl_save")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")]
    ])
    await chat.send_message(text, reply_markup=keyboard, parse_mode="Markdown")


# ─── PREMIUM ───────────────────────────────────────────

async def handle_premium(chat, title):
    msg = await send_gif(chat, "loading", f"🔄 *{title}*\n\n⚙️ Инициализация модуля...")
    for stage in ["🔄 Загрузка ядра...", "⚙️ Подключение к серверам...",
                   "📡 Установка соединения...", "🔐 Проверка прав...", "❌ Доступ запрещён!"]:
        await asyncio.sleep(1.0)
        try:
            await msg.edit_caption(caption=f"🔄 *{title}*\n\n{stage}", parse_mode="Markdown")
        except Exception:
            pass
    await asyncio.sleep(1.5)
    try:
        await msg.delete()
    except Exception:
        pass
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐ Купить VIP", callback_data="vip")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")]
    ])
    await send_gif(
        chat, "denied",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"       🔒 *{title}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"   Функция доступна только для *VIP!*\n\n"
        f"   💎 Приобрети VIP-подписку\n"
        f"   для полного доступа.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard
    )


async def handle_download(query, context):
    d = context.user_data.get("dox") or gen_data("unknown")
    html = make_html(d)
    f = io.BytesIO(html.encode("utf-8"))
    f.name = f"doxing_{d['target']}.html"
    await query.message.reply_document(document=f, caption="📥 Doxing Report")
    await query.answer("✅ Файл отправлен!")


# ─── VIP ───────────────────────────────────────────────

async def handle_vip(chat, user_id):
    active, remaining = get_user_vip(user_id)

    if active:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Назад", callback_data="back")]
        ])
        await send_gif(
            chat, "vip",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "       ⭐ *VIP — АКТИВЕН* ✅\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"   💎 *Осталось:* {remaining}\n\n"
            "   🎯 *Доступные функции:*\n"
            "   • ☠ Снос — полный доступ\n"
            "   • 🔍 Доксинг — расширенный\n"
            "   • ⚡ DDoS — все протоколы\n"
            "   • 📞 Бомбер — без лимитов\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=keyboard
        )
    else:
        buy_link = "https://t.me/qituh?text=" + quote("Здравствуйте хочу купить випку")
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Купить VIP", url=buy_link)],
            [InlineKeyboardButton("◀️ Назад", callback_data="back")]
        ])
        await send_gif(
            chat, "vip",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "       ⭐ *VIP ПОДПИСКА*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "   💎 *Получи полный доступ!*\n\n"
            "   🎯 *Что даёт VIP:*\n"
            "   • ☠ Снос — полный доступ\n"
            "   • 🔍 Доксинг — расширенный\n"
            "   • ⚡ DDoS — все протоколы\n"
            "   • 📞 Бомбер — без лимитов\n\n"
            "   ─────────────────────────\n\n"
            "   💰 *Тарифы:*\n\n"
            "   🥉 1 День ............. *15 ⭐*\n"
            "   🥈 7 Дней ............. *25 ⭐*\n"
            "   🥇 30 Дней ............ *35 ⭐*\n"
            "   💎 1 Год .............. *100 ⭐*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=keyboard
        )


async def handle_vip_buy(query, data):
    m = {"vipbuy_1": ("1 День", "15"), "vipbuy_7": ("7 Дней", "25"),
         "vipbuy_30": ("30 Дней", "35"), "vipbuy_365": ("1 Год", "100")}
    plan, price = m.get(data, ("?", "?"))
    owner_link = f"https://t.me/{OWNER}?text={quote('Привет! Хочу купить VIP')}"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💳 Оплатить {price} ⭐", url=owner_link)],
        [InlineKeyboardButton("◀️ Назад к тарифам", callback_data="vip")]
    ])
    await query.edit_message_text(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"       💳 *ОПЛАТА VIP*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"   📦 *Тариф:* {plan}\n"
        f"   💰 *Стоимость:* {price} ⭐\n\n"
        f"   Нажми кнопку ниже для перехода\n"
        f"   к администратору и оплаты.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard, parse_mode="Markdown"
    )


# ─── TEXT HANDLER ──────────────────────────────────────

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    if user.username:
        usernames = load_json(USERNAMES_FILE)
        usernames[user.username.lower()] = user_id
        save_json(USERNAMES_FILE, usernames)
    if not is_subscribed(context, user_id):
        await update.message.chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "      🔒 *ТРЕБУЕТСЯ ПОДПИСКА*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "   Подпишись на каналы,\n"
            "   чтобы продолжить.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=sub_keyboard(), parse_mode="Markdown"
        )
        return

    if context.user_data.get("awaiting_dox"):
        context.user_data["awaiting_dox"] = False
        await run_doxing(update.message.chat, update.message.text.strip(), context)
    elif context.user_data.get("awaiting_takedown"):
        context.user_data["awaiting_takedown"] = False
        await run_takedown(update.message.chat, update.message.text.strip(), context)


# ─── NO VIP ───────────────────────────────────────────

async def handle_no_vip(chat):
    buy_link = "https://t.me/qituh?text=" + quote("Здравствуйте хочу купить випку")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Купить VIP", url=buy_link)],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")]
    ])
    await send_gif(
        chat, "denied",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "       🔒 *ТРЕБУЕТСЯ VIP*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "   Эта функция доступна\n"
        "   только для VIP-пользователей.\n\n"
        "   💎 Купи VIP для полного доступа.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard
    )


# ─── ADMIN: /iaoplatil ────────────────────────────────

OWNER_ID = 8287486718

async def iaoplatil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Использование: /iaoplatil <user_id или @username> [дни]")
        return

    target_arg = context.args[0]
    days = 30
    if len(context.args) > 1:
        try:
            days = int(context.args[1])
        except ValueError:
            pass

    if target_arg.startswith("@"):
        username = target_arg[1:].lower()
        usernames = load_json(USERNAMES_FILE)
        target_id = usernames.get(username)
        if not target_id:
            await update.message.reply_text(f"Пользователь @{username} не найден. Он должен сначала написать /start боту.")
            return
    else:
        try:
            target_id = int(target_arg)
        except ValueError:
            await update.message.reply_text("Неверный user_id или username")
            return

    seconds = days * 86400
    set_user_vip(target_id, seconds)

    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  VIP ПОДПИСКА АКТИВИРОВАНА\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"  Тебе выдан VIP на {days} дней.\n\n"
                "  Доступные функции:\n"
                "  - Снос\n"
                "  - Доксинг\n"
                "  - DDoS\n"
                "  - Бомбер\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
        )
        sent_ok = True
    except Exception:
        sent_ok = False

    status = "и уведомлен" if sent_ok else "(не удалось уведомить)"
    await update.message.reply_text(f"VIP выдан пользователю {target_id} на {days} дней {status}")


# ─── MAIN ──────────────────────────────────────────────

def main():
    generate_promos()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iaoplatil", iaoplatil))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("☠ DARK DOKER BOT запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
