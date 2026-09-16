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
OWNER_ID = 8287486718

CHANNELS = [
    {"id": "@APKSOFTERA", "link": "https://t.me/APKSOFTERA"},
    {"id": "@jdkdkdoskcjfj", "link": "https://t.me/jdkdkdoskcjfj"},
]

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
USERNAMES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usernames.json")

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

USER_STATE = {}


def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user_vip(user_id):
    users = load_json(USERS_FILE)
    u = users.get(str(user_id), {})
    vip_until = u.get("vip_until", 0)
    if vip_until == 9999999999:
        return True, "навсегда"
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
    if seconds >= 315360000:
        users[uid]["vip_until"] = 9999999999
    else:
        current = users[uid].get("vip_until", 0)
        now = time.time()
        if current > now and current != 9999999999:
            users[uid]["vip_until"] = current + seconds
        else:
            users[uid]["vip_until"] = now + seconds
    save_json(USERS_FILE, users)


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
<html lang="ru"><head><meta charset="UTF-8"><title>Dox - {d['target']}</title>
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
<h1>DOX REPORT</h1>
<p class="sub">target: {d['target']}</p>
<div class="s"><h2>PERSONAL</h2>
<div class="r"><span class="l">Имя:</span><span class="v">{d['first']}</span></div>
<div class="r"><span class="l">Фамилия:</span><span class="v">{d['last']}</span></div>
<div class="r"><span class="l">ДР:</span><span class="v">{d['birthday']} ({d['age']} лет)</span></div>
<div class="r"><span class="l">Паспорт:</span><span class="v">{d['passport']}</span></div>
<div class="r"><span class="l">ИНН:</span><span class="v">{d['inn']}</span></div></div>
<div class="s"><h2>LOCATION</h2>
<div class="r"><span class="l">Страна:</span><span class="v">{d['country']}</span></div>
<div class="r"><span class="l">Город:</span><span class="v">{d['city']}</span></div>
<div class="r"><span class="l">Адрес:</span><span class="v">{d['street']}, д.{d['house']}, кв.{d['flat']}</span></div></div>
<div class="s"><h2>CONTACTS</h2>
<div class="r"><span class="l">Тел:</span><span class="v">{d['phone']}</span></div>
<div class="r"><span class="l">Оператор:</span><span class="v">{CARRIER[d['carrier']]} {d['carrier']}</span></div>
<div class="r"><span class="l">Email:</span><span class="v">{d['email']}</span></div>
<div class="r"><span class="l">Username:</span><span class="v">@{d['user']}</span></div></div>
<div class="s"><h2>NETWORK</h2>
<div class="r"><span class="l">IP:</span><span class="v">{d['ip']}</span></div>
<div class="r"><span class="l">MAC:</span><span class="v">{d['mac']}</span></div></div>
<div class="f">DARK DOXER</div>
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
        await update.message.chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "      ☠  D A R K  D O X E R  ☠\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "   Добро пожаловать в тёмную зону.\n"
            "   Выбери действие из меню ↓\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=main_menu_kb()
        )
    else:
        await update.message.chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "      ☠  D A R K  D O X E R  ☠\n"
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
        await query.message.chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "      ☠  D A R K  D O X E R  ☠\n"
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
            await query.answer(f"✅ {done}/{len(CHANNELS)} каналов подтверждено!", show_alert=True)
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

    user_id = user.id
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
        labels = {"takedown_users": "Пользователя", "takedown_group": "Группу",
                  "takedown_channel": "Канал", "takedown_bot": "Бота"}
        USER_STATE[user_id] = {"type": "awaiting_takedown", "takedown_type": labels[data]}
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Назад", callback_data="back_takedown")]
        ])
        await chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  СНОС {labels[data].upper()}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "  Введи юзернейм или ссылку:\n\n"
            "  Пример: @username\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=keyboard
        )
    elif data == "doxing":
        if not active:
            await handle_no_vip(chat)
            return
        USER_STATE[user_id] = "awaiting_dox"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Назад", callback_data="back")]
        ])
        await chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  DOXING MODULE\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "  Введи юзернейм или номер телефона:\n\n"
            "  Пример: @username или +79001234567\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=keyboard
        )
    elif data == "ddos":
        if not active:
            await handle_no_vip(chat)
            return
        USER_STATE[user_id] = "awaiting_ddos"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Назад", callback_data="back")]
        ])
        await chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  DDoS АТАКА\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "  Введи сайт для атаки:\n\n"
            "  Пример: example.com\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=keyboard
        )
    elif data == "bomber":
        if not active:
            await handle_no_vip(chat)
            return
        USER_STATE[user_id] = "awaiting_bomber"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Назад", callback_data="back")]
        ])
        await chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  БОМБЕР\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "  Введи номер телефона:\n\n"
            "  Пример: +79001234567\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=keyboard
        )
    elif data == "vip":
        await handle_vip(chat, user_id)
    elif data.startswith("dl_"):
        d = USER_STATE.get(f"dox_{user_id}") or gen_data("unknown")
        html = make_html(d)
        f = io.BytesIO(html.encode("utf-8"))
        f.name = f"doxing_{d['target']}.html"
        await query.message.reply_document(document=f, caption="Doxing Report")
        try:
            await query.answer("Файл отправлен!")
        except Exception:
            pass
    elif data == "back":
        try:
            await query.message.delete()
        except Exception:
            pass
        await chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "      ☠  D A R K  D O X E R  ☠\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "   Выбери действие из меню ↓\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=main_menu_kb()
        )
    elif data == "back_takedown":
        try:
            await query.message.delete()
        except Exception:
            pass
        await handle_takedown_menu(chat)


# ─── NO VIP ───────────────────────────────────────────

async def handle_no_vip(chat):
    buy_link = "https://t.me/qituh?text=" + quote("Здравствуйте хочу купить випку")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Купить VIP", url=buy_link)],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")]
    ])
    await chat.send_message(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  ТРЕБУЕТСЯ VIP\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "  Эта функция доступна\n"
        "  только для VIP-пользователей.\n\n"
        "  Купи VIP для полного доступа.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard
    )


# ─── TAKEDOWN ──────────────────────────────────────────

async def handle_takedown_menu(chat):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Пользователь", callback_data="takedown_users")],
        [InlineKeyboardButton("👥 Группа", callback_data="takedown_group")],
        [InlineKeyboardButton("📢 Канал", callback_data="takedown_channel")],
        [InlineKeyboardButton("🤖 Бот", callback_data="takedown_bot")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")]
    ])
    await chat.send_message(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  СНОС\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "  Выбери цель для сноса:\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard
    )


async def run_takedown(chat, target, user_id):
    state = USER_STATE.get(user_id, {})
    takedown_type = state.get("takedown_type", "Цель") if isinstance(state, dict) else "Цель"

    total = random.randint(500, 700)
    failed = random.randint(30, 80)
    sent = total - failed

    msg = await chat.send_message(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  СНОС {takedown_type.upper()}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Цель: {target}\n\n"
        f"  Отправка жалоб...\n\n"
        f"  [■□□□□□□□□□] 10%\n"
        f"  Жалоба #1 из {total}..."
    )

    bars = [
        ("[■■□□□□□□□□] 15%", f"Жалоба #{int(total*0.15)} — Спам"),
        ("[■■■■□□□□□□] 30%", f"Жалоба #{int(total*0.30)} — Нарушение правил"),
        ("[■■■■■■□□□□] 45%", f"Жалоба #{int(total*0.45)} — Мошенничество"),
        ("[■■■■■■■■□□] 60%", f"Жалоба #{int(total*0.60)} — Преследование"),
        ("[■■■■■■■■■□] 75%", f"Жалоба #{int(total*0.75)} — Угрозы"),
        ("[■■■■■■■■■■] 90%", f"Жалоба #{int(total*0.90)} — Финал..."),
        ("[■■■■■■■■■■] 100%", f"Отправлено {sent} жалоб из {total}!"),
    ]

    for bar, stage in bars:
        await asyncio.sleep(random.uniform(1.0, 2.0))
        try:
            await msg.edit_text(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  СНОС {takedown_type.upper()}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"  Цель: {target}\n\n"
                f"  Отправка жалоб...\n\n"
                f"  {bar}\n"
                f"  {stage}"
            )
        except Exception:
            pass

    await asyncio.sleep(1.5)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Меню", callback_data="back")]
    ])
    await chat.send_message(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  СНОС ЗАВЕРШЁН\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Цель: {target}\n"
        f"  Тип: {takedown_type}\n\n"
        f"  Статус: Успешно\n"
        f"  Жалоб: {sent}/{total}\n"
        f"  Ошибок: {failed}\n"
        f"  Время: {random.randint(30,120)}с\n\n"
        "  Результат будет рассмотрен\n"
        "  в течение 24-72 часов.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard
    )


# ─── DOXING ────────────────────────────────────────────

async def run_doxing(chat, target, user_id):
    msg = await chat.send_message(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  DOXING MODULE\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Цель: {target}\n\n"
        f"  [■□□□□□□□□□] 10%\n"
        f"  Сканирование баз данных..."
    )
    progress = [
        ("[■■■□□□□□□□] 30%", "Перехват пакетов..."),
        ("[■■■■■□□□□□] 50%", "Трассировка IP..."),
        ("[■■■■■■■□□□] 70%", "Дешифровка данных..."),
        ("[■■■■■■■■■□] 90%", "Формирование отчёта..."),
        ("[■■■■■■■■■■] 100%", "Данные собраны!"),
    ]
    for bar, stage in progress:
        await asyncio.sleep(1.2)
        try:
            await msg.edit_text(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  DOXING MODULE\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"  Цель: {target}\n\n"
                f"  {bar}\n"
                f"  {stage}"
            )
        except Exception:
            pass
    await asyncio.sleep(1.5)
    d = gen_data(target)
    USER_STATE[f"dox_{user_id}"] = d
    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  DOX RESULT\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Цель: {target}\n\n"
        f"  Имя: {d['first']} {d['last']}\n"
        f"  ДР: {d['birthday']} ({d['age']} лет)\n"
        f"  Страна: {d['country']}\n"
        f"  Город: {d['city']}\n"
        f"  Адрес: {d['street']}, д.{d['house']}, кв.{d['flat']}\n\n"
        f"  Телефон: {d['phone']}\n"
        f"  Оператор: {CARRIER[d['carrier']]} {d['carrier']}\n"
        f"  Email: {d['email']}\n"
        f"  Username: @{d['user']}\n\n"
        f"  IP: {d['ip']}\n"
        f"  MAC: {d['mac']}\n"
        f"  Паспорт: {d['passport']}\n"
        f"  ИНН: {d['inn']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Скачать HTML", callback_data="dl_save")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")]
    ])
    await chat.send_message(text, reply_markup=keyboard)


# ─── DDoS ──────────────────────────────────────────────

async def run_ddos(chat, target, user_id):
    msg = await chat.send_message(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  DDoS АТАКА\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Цель: {target}\n\n"
        f"  [■□□□□□□□□□] 10%\n"
        f"  Инициализация атаки..."
    )
    attacks = [
        ("[■■□□□□□□□□] 15%", "Подключение к ботнету..."),
        ("[■■■■□□□□□□] 30%", "SYN Flood — отправка пакетов..."),
        ("[■■■■■■□□□□] 45%", "UDP Flood — массовая отправка..."),
        ("[■■■■■■■■□□] 60%", "HTTP Flood — запросы к серверу..."),
        ("[■■■■■■■■■□] 75%", "Slowloris — удержание соединений..."),
        ("[■■■■■■■■■■] 90%", "Проверка доступности цели..."),
        ("[■■■■■■■■■■] 100%", "Цель недоступна!"),
    ]
    for bar, stage in attacks:
        await asyncio.sleep(random.uniform(1.0, 2.5))
        try:
            await msg.edit_text(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  DDoS АТАКА\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"  Цель: {target}\n\n"
                f"  {bar}\n"
                f"  {stage}"
            )
        except Exception:
            pass
    await asyncio.sleep(1.5)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Меню", callback_data="back")]
    ])
    pps = random.randint(50000, 200000)
    duration = random.randint(60, 300)
    await chat.send_message(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  DDoS АТАКА ЗАВЕРШЕНА\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Цель: {target}\n\n"
        f"  Статус: Успешно\n"
        f"  PPS: {pps:,}\n"
        f"  Длительность: {duration}с\n"
        f"  Потоков: {random.randint(100, 500)}\n\n"
        "  Цель недоступна.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard
    )


# ─── BOMBER ────────────────────────────────────────────

async def run_bomber(chat, target, user_id):
    services = [
        "Telegram", "WhatsApp", "Viber", "VK", "Яндекс",
        "Google", "Amazon", "OZON", "Wildberries", "Сбербанк",
        "Тинькофф", "Альфа-Банк", "МТС", "Билайн", "МегаФон",
    ]
    total = random.randint(50, 150)
    failed = random.randint(5, 20)
    sent = total - failed

    msg = await chat.send_message(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  БОМБЕР\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Цель: {target}\n\n"
        f"  [■□□□□□□□□□] 10%\n"
        f"  Отправка SMS на {services[0]}..."
    )
    bars = [
        ("[■■□□□□□□□□] 15%", 15),
        ("[■■■■□□□□□□] 30%", 30),
        ("[■■■■■■□□□□] 45%", 45),
        ("[■■■■■■■■□□] 60%", 60),
        ("[■■■■■■■■■□] 75%", 75),
        ("[■■■■■■■■■■] 90%", 90),
        ("[■■■■■■■■■■] 100%", 100),
    ]
    for bar, pct in bars:
        svc = random.choice(services)
        count = int(total * pct / 100)
        await asyncio.sleep(random.uniform(1.0, 2.0))
        try:
            await msg.edit_text(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  БОМБЕР\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"  Цель: {target}\n\n"
                f"  {bar}\n"
                f"  SMS #{count} → {svc}..."
            )
        except Exception:
            pass
    await asyncio.sleep(1.5)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Меню", callback_data="back")]
    ])
    await chat.send_message(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  БОМБЕР ЗАВЕРШЁН\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Цель: {target}\n\n"
        f"  Статус: Успешно\n"
        f"  Отправлено: {sent}/{total}\n"
        f"  Ошибок: {failed}\n"
        f"  Сервисов: {len(services)}\n\n"
        "  Номер забомблен.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard
    )


# ─── VIP ───────────────────────────────────────────────

async def handle_vip(chat, user_id):
    active, remaining = get_user_vip(user_id)
    if active:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Назад", callback_data="back")]
        ])
        await chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  VIP — АКТИВЕН\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"  Осталось: {remaining}\n\n"
            "  Доступные функции:\n"
            "  - Снос — полный доступ\n"
            "  - Доксинг — расширенный\n"
            "  - DDoS — все протоколы\n"
            "  - Бомбер — без лимитов\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=keyboard
        )
    else:
        buy_link = "https://t.me/qituh?text=" + quote("Здравствуйте хочу купить випку")
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Купить VIP", url=buy_link)],
            [InlineKeyboardButton("◀️ Назад", callback_data="back")]
        ])
        await chat.send_message(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  VIP ПОДПИСКА\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "  Получи полный доступ!\n\n"
            "  Что даёт VIP:\n"
            "  - Снос — полный доступ\n"
            "  - Доксинг — расширенный\n"
            "  - DDoS — все протоколы\n"
            "  - Бомбер — без лимитов\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=keyboard
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
            "  ТРЕБУЕТСЯ ПОДПИСКА\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "  Подпишись на каналы,\n"
            "  чтобы продолжить.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=sub_keyboard()
        )
        return

    state = USER_STATE.get(user_id)

    if state == "awaiting_dox":
        USER_STATE.pop(user_id, None)
        await run_doxing(update.message.chat, update.message.text.strip(), user_id)

    elif state == "awaiting_takedown":
        USER_STATE.pop(user_id, None)
        await run_takedown(update.message.chat, update.message.text.strip(), user_id)

    elif state == "awaiting_ddos":
        USER_STATE.pop(user_id, None)
        await run_ddos(update.message.chat, update.message.text.strip(), user_id)

    elif state == "awaiting_bomber":
        USER_STATE.pop(user_id, None)
        await run_bomber(update.message.chat, update.message.text.strip(), user_id)


# ─── ADMIN: /iaoplatil ────────────────────────────────

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
            await update.message.reply_text(f"@{username} не найден. Он должен сначала написать /start боту.")
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
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iaoplatil", iaoplatil))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("BOT STARTED OK")
    app.run_polling()


if __name__ == "__main__":
    main()
