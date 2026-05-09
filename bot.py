#!/usr/bin/env python3
"""Shop Telegram Bot"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import uuid
from pathlib import Path

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
    PicklePersistence
)
from telegram.error import Conflict, NetworkError, TimedOut

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
BOT_TOKEN        = os.environ.get("BOT_TOKEN", "8360784420:AAEMED2E-2RRHh2Gd8db4ukltCWxI6f_7GQ")
ADMIN_IDS        = [8503115617, 6761125512, 6617032248]
VERIFY_CHANNEL   = -1005456140674028019486
DATA_FILE        = "bot_data.json"
SUPPORT_CONTACTS = "@Mar1xff @Bhavisss @Pssysmglr"
CERT_BOT         = "@one_ibot"
BINANCE_ID       = "1016392717"

UPI_QR_PATHS     = ["upi_qr.jpg", "upi_qr.png", "qr.jpg", "qr.png", "qr.img"]
BINANCE_QR_PATHS = ["binance_qr.jpg", "binance_qr.png", "binance.jpg", "binance.png"]

def find_image(paths: list) -> str | None:
    for p in paths:
        if Path(p).exists():
            return p
    return None

# ═══════════════════════════════════════════════════════════════════════════════
#  CUSTOM EMOJI
# ═══════════════════════════════════════════════════════════════════════════════
def ce(eid: str, fb: str) -> str:
    return f'<tg-emoji emoji-id="{eid}">{fb}</tg-emoji>'

CE_ANIM  = ce("5456140674028019486", "⏳")

CE_FF    = ce("6228904568747465283", "🎮")
CE_8B    = ce("5960777057607625616", "🎱")
CE_CERT  = ce("5965079210383907241", "📜")
CE_ML    = ce("5965324474491348850", "⚔️")
CE_PUBG  = ce("6228782651805800965", "🔫")

CE_FLUOR   = ce("5801188682912243172", "💎")
CE_MIGUL   = ce("6233248412771295068", "⭐")
CE_DRIP    = ce("6212942266957310140", "💧")
CE_HG      = ce("6210499577322151683", "🔥")
CE_PATO    = ce("6210656322153618819", "🦆")
CE_FFH4X   = ce("6213189420850356650", "⚡")
CE_CERT2   = ce("5332823031859389246", "🏅")
CE_8BPROD  = ce("5418138833457793454", "🎱")
CE_FLUORM  = ce("5292158397465005457", "💎")

CE_ACCT    = ce("5954175920506933873", "👤")
CE_CART    = ce("5440841102871517055", "🛒")
CE_WALLET  = ce("5767197779155754253", "💰")
CE_ADMIN   = ce("5765087343895649564", "🔧")
CE_STATUS  = ce("6059653892025618055", "✅")
CE_AVAIL   = ce("5445195276291693508", "🟢")
CE_UNAVAIL = ce("5445102217235292298", "🔴")
CE_KEY     = ce("5229355359811096717", "🔑")
CE_STATS   = ce("5877332341331857066", "📊")

# Purchase / approval emojis (from user spec)
CE_DENY    = ce("5462989862669920629", "❌")
CE_SUCCESS = ce("5953810354365538566", "🎉")
CE_PROD_LBL = ce("5323289282499064033", "📦")
CE_DUR_LBL  = ce("5472026645659401564", "⏱️")
CE_KEY_LBL  = ce("6147915796375935782", "🔑")

CAT_CE = {
    "ff_ios":   CE_FF,   "ff_and":   CE_FF,
    "8b_ios":   CE_8B,   "8b_and":   CE_8B,
    "cert_ios": CE_CERT,
    "ml_ios":   CE_ML,
    "pubg_ios": CE_PUBG, "pubg_and": CE_PUBG,
}

# ═══════════════════════════════════════════════════════════════════════════════
#  MENU DATA
# ═══════════════════════════════════════════════════════════════════════════════
MENU = {
    "ff_ios": {
        "label": "Free Fire (iOS)",
        "products": [
            {"name": "Fluorite",    "ce": CE_FLUOR,  "prices": [("31 Days","23.00"),("7 Days","15.00"),("1 Day","5.00")]},
            {"name": "Migul [PRO]", "ce": CE_MIGUL,  "prices": [("31 Days","20.00"),("7 Days","10.00"),("1 Day","3.00")]},
            {"name": "FFH4X",       "ce": CE_FFH4X,  "prices": [("31 Days","25.00"),("7 Days","15.00"),("1 Day","5.00")]},
            {"name": "iMAZING",     "ce": CE_FF,     "prices": [("31 Days","9.00")]},
        ],
    },
    "ff_and": {
        "label": "Free Fire (Android)",
        "products": [
            {"name": "HG-Cheats (Root)",       "ce": CE_HG,   "prices": [("31 Days","13.00"),("10 Days","6.50"),("7 Days","5.50"),("1 Day","4.00")]},
            {"name": "HG-Cheats (Non-Root)",   "ce": CE_HG,   "prices": [("31 Days","13.00"),("10 Days","8.00"),("7 Days","5.50"),("1 Day","4.00")]},
            {"name": "PatoTeam (Non-Root)",    "ce": CE_PATO, "prices": [("31 Days","12.50"),("15 Days","8.50"),("7 Days","6.00"),("1 Day","2.50")]},
            {"name": "Drip-Client (Root)",     "ce": CE_DRIP, "prices": [("31 Days","12.00"),("15 Days","8.00"),("7 Days","4.50"),("1 Day","2.00")]},
            {"name": "Drip-Client (Non-Root)", "ce": CE_DRIP, "prices": [("31 Days","12.00"),("15 Days","8.00"),("7 Days","4.50"),("1 Day","2.00")]},
        ],
    },
    "8b_ios": {
        "label": "8 Ball Pool (iOS)",
        "products": [
            {"name": "Wizard iOS",          "ce": CE_8BPROD, "prices": [("30 Days","18.00"),("7 Days","8.00"),("1 Day","2.00")]},
            {"name": "Star Wolf GBD Pixel", "ce": CE_8BPROD, "prices": [("30 Days","12.00"),("7 Days","5.50"),("1 Day","2.00")]},
            {"name": "iOS-Viet",            "ce": CE_8BPROD, "prices": [("30 Days","20.00"),("7 Days","10.00"),("1 Day","4.00")]},
            {"name": "Potassium iOS",       "ce": CE_8BPROD, "prices": [("30 Days","14.00"),("7 Days","8.00"),("1 Day","4.00")]},
        ],
    },
    "8b_and": {
        "label": "8 Ball Pool (Android)",
        "out_of_stock": True,
        "products": [],
    },
    "cert_ios": {
        "label": "Certificate (iOS)",
        "is_cert": True,
        "products": [
            {"name": "iPhone Certificate", "ce": CE_CERT2, "prices": [("300 Days","10.00")]},
            {"name": "iPad Certificate",   "ce": CE_CERT2, "prices": [("300 Days","10.00")]},
        ],
    },
    "ml_ios": {
        "label": "Mobile Legends (iOS)",
        "products": [
            {"name": "Fluorite MLBB", "ce": CE_FLUORM, "prices": [("30 Days","23.00"),("7 Days","15.00"),("1 Day","5.00")]},
        ],
    },
    "pubg_ios": {
        "label": "PUBG Mobile (iOS)",
        "products": [
            {"name": "Dolphin iOS",  "ce": CE_PUBG, "prices": [("30 Days","14.00"),("7 Days","8.00"),("1 Day","3.50")]},
            {"name": "Star Win iOS", "ce": CE_PUBG, "prices": [("30 Days","15.00"),("7 Days","8.00"),("1 Day","3.50")]},
            {"name": "GroX iOS",     "ce": CE_PUBG, "prices": [("30 Days","18.00"),("7 Days","12.00"),("1 Day","6.00")]},
        ],
    },
    "pubg_and": {
        "label": "PUBG Mobile (Android)",
        "products": [
            {"name": "Zolo (Non-Root)", "ce": CE_PUBG, "prices": [("30 Days","15.00"),("7 Days","6.00"),("1 Day","2.00")]},
            {"name": "aXel PM",         "ce": CE_PUBG, "prices": [("30 Days","20.00"),("7 Days","12.00"),("1 Day","6.00")]},
            {"name": "Fluxo SRS",       "ce": CE_PUBG, "prices": [("30 Days","20.00"),("7 Days","12.00"),("1 Day","6.00")]},
        ],
    },
}
CAT_ORDER = ["ff_ios","ff_and","8b_ios","8b_and","cert_ios","ml_ios","pubg_ios","pubg_and"]


# ═══════════════════════════════════════════════════════════════════════════════
#  DATA HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
_MEM_DATA: dict  = {}
_MEM_STATE: dict = {}

def load() -> dict:
    global _MEM_DATA
    d = None
    if Path(DATA_FILE).exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            pass
    if d is None:
        d = dict(_MEM_DATA) if _MEM_DATA else {}
    d.setdefault("verified", [])
    d.setdefault("admin_ids", [])
    d.setdefault("keys", {})
    d.setdefault("files", {})
    d.setdefault("pending_orders", {})
    d.setdefault("_state", {})
    return d

def save(d: dict):
    global _MEM_DATA
    _MEM_DATA = d
    tmp = DATA_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        os.replace(tmp, DATA_FILE)
    except Exception:
        pass

def get_state(d: dict, uid: int):
    key = str(uid)
    return d.get("_state", {}).get(key) or _MEM_STATE.get(key)

def set_state(d: dict, uid: int, state):
    key = str(uid)
    _MEM_STATE[key] = state
    d.setdefault("_state", {})[key] = state
    save(d)

def clear_state(d: dict, uid: int):
    key = str(uid)
    _MEM_STATE.pop(key, None)
    d.setdefault("_state", {}).pop(key, None)
    save(d)

def is_admin(uid: int, d: dict) -> bool:
    return uid in ADMIN_IDS or uid in d.get("admin_ids", [])

def is_verified(uid: int, d: dict) -> bool:
    return is_admin(uid, d) or uid in d.get("verified", [])

def key_slot(cat: str, idx: int, dur: str) -> str:
    return f"{cat}_{idx}_{dur}"

def keys_count(cat: str, idx: int, dur: str, d: dict) -> int:
    return len(d.get("keys", {}).get(key_slot(cat, idx, dur), []))

def files_count(cat: str, idx: int, dur: str, d: dict) -> int:
    return len(d.get("files", {}).get(key_slot(cat, idx, dur), []))

def slot_stock(cat: str, idx: int, dur: str, d: dict) -> int:
    return keys_count(cat, idx, dur, d) + files_count(cat, idx, dur, d)

def total_product_stock(k: str, i: int, d: dict) -> int:
    cat = MENU[k]
    if i >= len(cat["products"]):
        return 0
    prod = cat["products"][i]
    return sum(slot_stock(k, i, dur, d) for dur, _ in prod["prices"])

def pop_key(cat: str, idx: int, dur: str, d: dict):
    slot = key_slot(cat, idx, dur)
    lst  = d.get("keys", {}).get(slot, [])
    if not lst:
        return None
    k = lst.pop(0)
    d["keys"][slot] = lst
    save(d)
    return k

def pop_file(cat: str, idx: int, dur: str, d: dict):
    slot = key_slot(cat, idx, dur)
    lst  = d.get("files", {}).get(slot, [])
    if not lst:
        return None
    f = lst.pop(0)
    d["files"][slot] = lst
    save(d)
    return f

def esc(t) -> str:
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ═══════════════════════════════════════════════════════════════════════════════
#  KEYBOARDS
# ═══════════════════════════════════════════════════════════════════════════════
def kb_main(uid: int, d: dict) -> ReplyKeyboardMarkup:
    rows = [["🛒 Shop"], ["👤 Account", "📊 Stock"]]
    if is_admin(uid, d):
        rows.append(["🔧 Admin Panel"])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def kb_verify() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅  Verify Access", callback_data="verify")
    ]])

def kb_cats() -> InlineKeyboardMarkup:
    rows = []
    for k in CAT_ORDER:
        cat   = MENU[k]
        label = cat["label"]
        if cat.get("out_of_stock"):
            label += "  [Out of Stock]"
        rows.append([InlineKeyboardButton(label, callback_data=f"cat|{k}")])
    return InlineKeyboardMarkup(rows)

def kb_cat(k: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(p["name"], callback_data=f"prod|{k}|{i}")]
        for i, p in enumerate(MENU[k]["products"])
    ]
    rows.append([InlineKeyboardButton("⬅️  Back", callback_data="cats")])
    return InlineKeyboardMarkup(rows)

def kb_durations(k: str, idx: int, prod: dict, d: dict) -> InlineKeyboardMarkup:
    rows = []
    for dur, price in prod["prices"]:
        qty   = slot_stock(k, idx, dur, d)
        label = f"{dur}  —  ${price}  [{qty} in stock]"
        rows.append([InlineKeyboardButton(label, callback_data=f"dur|{k}|{idx}|{dur}|{price}")])
    rows.append([InlineKeyboardButton("⬅️  Back", callback_data=f"cat|{k}")])
    return InlineKeyboardMarkup(rows)

def kb_payment(k: str, idx: int, dur: str, price: str) -> InlineKeyboardMarkup:
    base = f"{k}|{idx}|{dur}|{price}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳  Pay via UPI",     callback_data=f"pay|upi|{base}")],
        [InlineKeyboardButton("🔶  Pay via Binance", callback_data=f"pay|bnb|{base}")],
        [InlineKeyboardButton("💬  Other Method",    callback_data=f"pay|other|{base}")],
        [InlineKeyboardButton("⬅️  Back",            callback_data=f"prod|{k}|{idx}")],
    ])

def kb_paid(k: str, idx: int, dur: str, price: str, method: str) -> InlineKeyboardMarkup:
    base = f"{k}|{idx}|{dur}|{price}|{method}"
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅  I've Sent Payment", callback_data=f"paid|{base}")
    ]])

def kb_admin_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑  Add Keys",         callback_data="adm|add_keys")],
        [InlineKeyboardButton("📁  Add Files",         callback_data="adm|add_files")],
        [InlineKeyboardButton("📊  View Stock",        callback_data="adm|view_keys")],
        [InlineKeyboardButton("💰  Add Balance",       callback_data="adm|add_bal")],
        [InlineKeyboardButton("💰  Deduct Balance",    callback_data="adm|ded_bal")],
        [InlineKeyboardButton("💰  Check Balance",     callback_data="adm|chk_bal")],
        [InlineKeyboardButton("👑  Add Admin",         callback_data="adm|add_admin")],
        [InlineKeyboardButton("📢  Broadcast",         callback_data="adm|broadcast")],
        [InlineKeyboardButton("🗑️  Clear All Keys",    callback_data="adm|clear")],
        [InlineKeyboardButton("🗑️  Clear All Files",   callback_data="adm|clear_files")],
    ])

def kb_approve_deny(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅  Approve", callback_data=f"approve|{order_id}"),
        InlineKeyboardButton("❌  Deny",    callback_data=f"deny|{order_id}"),
    ]])

def kb_adm_cats(mode: str) -> InlineKeyboardMarkup:
    rows = []
    for k in CAT_ORDER:
        cat = MENU[k]
        if not cat["products"]: continue
        rows.append([InlineKeyboardButton(cat["label"], callback_data=f"a{mode}c|{k}")])
    rows.append([InlineKeyboardButton("❌  Cancel", callback_data="adm|cancel")])
    return InlineKeyboardMarkup(rows)

def kb_adm_prods(mode: str, cat_key: str) -> InlineKeyboardMarkup:
    cat = MENU[cat_key]
    rows = []
    for i, p in enumerate(cat["products"]):
        rows.append([InlineKeyboardButton(p["name"], callback_data=f"a{mode}p|{cat_key}|{i}")])
    back_action = "add_files" if mode == "f" else "add_keys"
    rows.append([InlineKeyboardButton("⬅️  Back", callback_data=f"adm|{back_action}")])
    return InlineKeyboardMarkup(rows)

def kb_adm_durs(mode: str, cat_key: str, idx: int) -> InlineKeyboardMarkup:
    prod = MENU[cat_key]["products"][idx]
    rows = []
    for dur, _ in prod["prices"]:
        dur_enc = dur.replace(" ", "~")
        rows.append([InlineKeyboardButton(dur, callback_data=f"a{mode}d|{cat_key}|{idx}|{dur_enc}")])
    rows.append([InlineKeyboardButton("⬅️  Back", callback_data=f"a{mode}c|{cat_key}")])
    return InlineKeyboardMarkup(rows)


# ═══════════════════════════════════════════════════════════════════════════════
#  DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def cat_msg(k: str) -> str:
    cat = MENU[k]
    cce = CAT_CE[k]
    if cat.get("out_of_stock"):
        return (f"{cce} <b>{esc(cat['label'])}</b>\n\n"
                f"⚠️ <b>Out of Stock</b>\n\nThis category is currently unavailable. Check back later!")
    lines = [f"{cce} <b>{esc(cat['label'])}</b>\n"]
    for p in cat["products"]:
        lines.append(f"{p['ce']} <b>{esc(p['name'])}</b>")
        for dur, pr in p["prices"]:
            lines.append(f"   ‣ {esc(dur)}  —  <b>${esc(pr)}</b>")
        lines.append("")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
#  VERIFY ANIMATION
# ═══════════════════════════════════════════════════════════════════════════════
async def run_verify(query, uid: int, ctx: ContextTypes.DEFAULT_TYPE):
    frames = [
        f"{CE_ANIM} <b>Verifying your access...</b>",
        f"{CE_ANIM} <b>Checking membership .</b>",
        f"{CE_ANIM} <b>Checking membership ..</b>",
        f"{CE_ANIM} <b>Checking membership ...</b>",
        f"{CE_ANIM} <b>Almost done ...</b>",
        f"{CE_ANIM} <b>Confirming identity ...</b>",
    ]
    msg = await query.message.reply_text(frames[0], parse_mode="HTML")
    for frame in frames[1:]:
        await asyncio.sleep(0.65)
        try:
            await msg.edit_text(frame, parse_mode="HTML")
        except Exception:
            pass

    verified = False
    try:
        member = await ctx.bot.get_chat_member(chat_id=VERIFY_CHANNEL, user_id=uid)
        if member.status in ("member", "administrator", "creator", "restricted"):
            verified = True
    except Exception:
        verified = True

    return msg, verified


# ═══════════════════════════════════════════════════════════════════════════════
#  PAYMENT DETAILS
# ═══════════════════════════════════════════════════════════════════════════════
async def send_payment_details(message, k: str, idx: int, dur: str, price: str, method: str, ctx):
    prod = MENU[k]["products"][idx]
    order_text = (
        f"<b>Order:</b> {esc(prod['name'])}\n"
        f"<b>Duration:</b> {esc(dur)}\n"
        f"<b>Amount:</b> <b>${esc(price)}</b>"
    )
    paid_kb = kb_paid(k, idx, dur, price, method)

    if method == "upi":
        img = find_image(UPI_QR_PATHS)
        caption = (
            f"💳 <b>Pay via UPI</b>\n\n{order_text}\n\n"
            f"Scan the QR and pay <b>${esc(price)}</b>.\n\n"
            f"After paying, click the button below."
        )
        if img:
            await message.reply_photo(photo=open(img, "rb"), caption=caption,
                                      parse_mode="HTML", reply_markup=paid_kb)
        else:
            await message.reply_text(
                caption + f"\n\n<i>QR image not set yet — contact admin</i>\nSupport: {SUPPORT_CONTACTS}",
                parse_mode="HTML", reply_markup=paid_kb)

    elif method == "bnb":
        img = find_image(BINANCE_QR_PATHS)
        caption = (
            f"🔶 <b>Pay via Binance</b>\n\n{order_text}\n\n"
            f"Send <b>${esc(price)} USDT</b> to:\n"
            f"<b>Binance ID:</b> <code>{BINANCE_ID}</code>\n\n"
            f"After sending, click the button below."
        )
        if img:
            await message.reply_photo(photo=open(img, "rb"), caption=caption,
                                      parse_mode="HTML", reply_markup=paid_kb)
        else:
            await message.reply_text(caption, parse_mode="HTML", reply_markup=paid_kb)

    else:
        await message.reply_text(
            f"💬 <b>Other Payment Method</b>\n\n{order_text}\n\n"
            f"Contact our support team:\n{SUPPORT_CONTACTS}",
            parse_mode="HTML"
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  DELIVER PRODUCT TO USER
# ═══════════════════════════════════════════════════════════════════════════════
async def deliver_product(user_id: int, order: dict, ctx: ContextTypes.DEFAULT_TYPE):
    k      = order["k"]
    i      = order["i"]
    dur    = order["dur"]
    price  = order["price"]
    method = order["method"]

    d    = load()
    cat  = MENU.get(k)
    if not cat or i >= len(cat["products"]):
        return False

    p = cat["products"][i]

    # Try key first, then file
    key_val  = None
    file_val = None

    if keys_count(k, i, dur, d) > 0:
        key_val = pop_key(k, i, dur, d)
    elif files_count(k, i, dur, d) > 0:
        file_val = pop_file(k, i, dur, d)
    else:
        return False

    method_label = {"upi": "UPI", "bnb": "Binance", "other": "Other"}.get(method, method)

    if key_val:
        success_msg = (
            f"{CE_SUCCESS} <b>PURCHASE SUCCESSFUL</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{CE_PROD_LBL} <b>Product:</b> {esc(p['name'])}\n"
            f"{CE_DUR_LBL} <b>Duration:</b> {esc(dur)}\n"
            f"{CE_KEY_LBL} <b>Key:</b> <code>{esc(key_val)}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"Support: {SUPPORT_CONTACTS}"
        )
        await ctx.bot.send_message(chat_id=user_id, text=success_msg, parse_mode="HTML")

    elif file_val:
        file_type  = file_val.get("type", "link")
        file_value = file_val.get("value", "")
        file_name  = file_val.get("name", "file")

        header_msg = (
            f"{CE_SUCCESS} <b>PURCHASE SUCCESSFUL</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{CE_PROD_LBL} <b>Product:</b> {esc(p['name'])}\n"
            f"{CE_DUR_LBL} <b>Duration:</b> {esc(dur)}\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"Your file is below. Support: {SUPPORT_CONTACTS}"
        )
        await ctx.bot.send_message(chat_id=user_id, text=header_msg, parse_mode="HTML")

        if file_type == "document":
            await ctx.bot.send_document(chat_id=user_id, document=file_value,
                                        caption=f"📁 {esc(file_name)}", parse_mode="HTML")
        elif file_type == "photo":
            await ctx.bot.send_photo(chat_id=user_id, photo=file_value,
                                     caption=f"🖼 {esc(file_name)}", parse_mode="HTML")
        else:
            await ctx.bot.send_message(chat_id=user_id,
                text=f"📁 <b>{esc(file_name)}</b>\n\n{esc(file_value)}", parse_mode="HTML")

    # Notify admins
    d2 = load()
    all_admins = list(set(ADMIN_IDS + d2.get("admin_ids", [])))
    for aid in all_admins:
        try:
            delivered = f"key: <code>{esc(key_val)}</code>" if key_val else f"file: <b>{esc(file_val.get('name','?'))}</b>"
            await ctx.bot.send_message(chat_id=aid,
                text=f"{CE_CART} <b>Purchase Approved &amp; Delivered</b>\n\n"
                     f"User: <code>{user_id}</code>\n"
                     f"Product: {esc(p['name'])}\nDuration: {esc(dur)}\n"
                     f"Price: ${esc(price)}\nMethod: {method_label}\n"
                     f"Delivered {delivered}", parse_mode="HTML")
        except Exception:
            pass

    return True


# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    d    = load()
    uid  = update.effective_user.id
    name = esc(update.effective_user.first_name or "there")
    if is_verified(uid, d):
        await update.message.reply_text(
            f"<b>Welcome back, {name}!</b>\n\nTap <b>Shop</b> to browse products.",
            parse_mode="HTML", reply_markup=kb_main(uid, d))
    else:
        await update.message.reply_text(
            f"<b>Welcome to the Shop Bot!</b>\n\nHello, <b>{name}</b>!\n\n"
            f"Press the button below to verify your access and start shopping.",
            parse_mode="HTML", reply_markup=kb_verify())

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Commands</b>\n\n/start — Main menu\n/help — This message\n\n"
        f"Support: {SUPPORT_CONTACTS}", parse_mode="HTML")


# ═══════════════════════════════════════════════════════════════════════════════
#  PHOTO / DOCUMENT HANDLER
# ═══════════════════════════════════════════════════════════════════════════════
async def handle_media(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    d   = load()
    uid = update.effective_user.id

    if not is_verified(uid, d):
        await update.message.reply_text("Please verify your access first. Use /start",
                                        reply_markup=kb_verify())
        return

    state = get_state(d, uid)

    # ── Admin adding a file to stock ──────────────────────────────────────────
    if state and state.startswith("add_files_item|") and is_admin(uid, d):
        parts = state.split("|", 3)
        if len(parts) != 4:
            await update.message.reply_text("Error in state. Use /start to reset."); return
        _, cat, idx_str, dur = parts
        idx = int(idx_str)

        slot = key_slot(cat, idx, dur)
        d.setdefault("files", {}).setdefault(slot, [])

        if update.message.document:
            fobj = update.message.document
            file_item = {"type": "document", "value": fobj.file_id, "name": fobj.file_name or "file"}
        elif update.message.photo:
            fobj = update.message.photo[-1]
            file_item = {"type": "photo", "value": fobj.file_id, "name": "image"}
        else:
            await update.message.reply_text("Unsupported file type. Send a document or photo."); return

        d["files"][slot].append(file_item)
        clear_state(d, uid)
        save(d)
        count = len(d["files"][slot])
        prod_name = MENU[cat]["products"][idx]["name"] if idx < len(MENU[cat]["products"]) else f"#{idx}"
        await update.message.reply_text(
            f"✅ <b>File Added!</b>\n\n"
            f"Product: <b>{esc(prod_name)}</b>\nDuration: <b>{esc(dur)}</b>\n"
            f"File: <b>{esc(file_item['name'])}</b>\n"
            f"Total in slot: <b>{count}</b>",
            parse_mode="HTML")
        return

    # ── User sending payment screenshot ──────────────────────────────────────
    if state and state.startswith("waiting_ss|"):
        parts = state.split("|", 5)
        if len(parts) != 6:
            await update.message.reply_text("Error in state. Please try again."); return
        _, k, si, dur, price, method = parts
        i = int(si)

        if not (update.message.photo or update.message.document):
            await update.message.reply_text(
                "📸 Please send a <b>screenshot</b> (photo) of your payment.",
                parse_mode="HTML"); return

        cat = MENU.get(k)
        if not cat or i >= len(cat["products"]):
            await update.message.reply_text("Invalid order. Please start over."); return
        p = cat["products"][i]

        # Store pending order
        order_id = uuid.uuid4().hex[:12]
        d["pending_orders"][order_id] = {
            "user_id": uid,
            "k": k, "i": i,
            "dur": dur, "price": price, "method": method
        }
        save(d)
        clear_state(d, uid)

        method_label = {"upi": "UPI", "bnb": "Binance", "other": "Other"}.get(method, method)
        user_info = (
            f"👤 User: <code>{uid}</code>\n"
            f"📦 Product: <b>{esc(p['name'])}</b>\n"
            f"⏱ Duration: <b>{esc(dur)}</b>\n"
            f"💰 Price: <b>${esc(price)}</b>\n"
            f"💳 Method: <b>{method_label}</b>\n"
            f"🆔 Order ID: <code>{order_id}</code>"
        )

        approve_kb = kb_approve_deny(order_id)

        all_admins = list(set(ADMIN_IDS + d.get("admin_ids", [])))
        for aid in all_admins:
            try:
                if update.message.photo:
                    await ctx.bot.send_photo(
                        chat_id=aid,
                        photo=update.message.photo[-1].file_id,
                        caption=f"📸 <b>Payment Screenshot</b>\n\n{user_info}",
                        parse_mode="HTML",
                        reply_markup=approve_kb
                    )
                else:
                    await ctx.bot.send_document(
                        chat_id=aid,
                        document=update.message.document.file_id,
                        caption=f"📸 <b>Payment Screenshot</b>\n\n{user_info}",
                        parse_mode="HTML",
                        reply_markup=approve_kb
                    )
            except Exception as e:
                logger.warning(f"Could not notify admin {aid}: {e}")

        await update.message.reply_text(
            "✅ <b>Screenshot received!</b>\n\n"
            "Your payment is being reviewed by an admin.\n"
            "You will receive your product shortly after approval.",
            parse_mode="HTML")
        return

    # Default: nothing to do with this media
    state_text = get_state(d, uid)
    if not state_text:
        await update.message.reply_text(
            "Use /start to open the main menu.", parse_mode="HTML")


# ═══════════════════════════════════════════════════════════════════════════════
#  TEXT HANDLER
# ═══════════════════════════════════════════════════════════════════════════════
async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    d    = load()
    uid  = update.effective_user.id
    text = (update.message.text or "").strip()

    if not is_verified(uid, d):
        await update.message.reply_text(
            "Please verify your access first. Use /start",
            reply_markup=kb_verify())
        return

    state = get_state(d, uid)

    # ── Admin: add files — receiving a text/link ──────────────────────────────
    if state and state.startswith("add_files_item|") and is_admin(uid, d):
        parts = state.split("|", 3)
        if len(parts) != 4:
            await update.message.reply_text("Error in state. Use /start to reset."); return
        _, cat, idx_str, dur = parts
        idx = int(idx_str)
        slot = key_slot(cat, idx, dur)
        d.setdefault("files", {}).setdefault(slot, [])
        file_item = {"type": "link", "value": text, "name": text[:50]}
        d["files"][slot].append(file_item)
        clear_state(d, uid)
        save(d)
        count = len(d["files"][slot])
        prod_name = MENU[cat]["products"][idx]["name"] if idx < len(MENU[cat]["products"]) else f"#{idx}"
        await update.message.reply_text(
            f"✅ <b>Link Added!</b>\n\n"
            f"Product: <b>{esc(prod_name)}</b>\nDuration: <b>{esc(dur)}</b>\n"
            f"Link: <code>{esc(text[:80])}</code>\n"
            f"Total in slot: <b>{count}</b>",
            parse_mode="HTML")
        return

    # ── Admin: add keys — receiving keys after button selection ───────────────
    if state and state.startswith("add_keys_item|") and is_admin(uid, d):
        parts = state.split("|", 3)
        if len(parts) != 4:
            await update.message.reply_text("Error in state. Use /start to reset."); return
        _, cat, idx_str, dur = parts
        idx = int(idx_str)
        new_keys = [l.strip() for l in text.strip().splitlines() if l.strip()]
        if not new_keys:
            await update.message.reply_text("No keys found. Send at least one key."); return
        slot = key_slot(cat, idx, dur)
        d.setdefault("keys", {}).setdefault(slot, []).extend(new_keys)
        clear_state(d, uid)
        save(d)
        prod_name = MENU[cat]["products"][idx]["name"] if idx < len(MENU[cat]["products"]) else f"#{idx}"
        await update.message.reply_text(
            f"{CE_KEY} <b>Keys Added!</b>\n\nProduct: <b>{esc(prod_name)}</b>\n"
            f"Duration: <b>{esc(dur)}</b>\nAdded: <b>{len(new_keys)}</b> keys\n"
            f"Total in slot: <b>{len(d['keys'][slot])}</b>", parse_mode="HTML")
        return

    if state == "admin_id" and is_admin(uid, d):
        try:
            new_id = int(text)
        except ValueError:
            await update.message.reply_text("Send a valid numeric Telegram User ID."); return
        d.setdefault("admin_ids", [])
        if new_id not in d["admin_ids"]:
            d["admin_ids"].append(new_id)
        clear_state(d, uid)
        await update.message.reply_text(f"Admin added: <code>{new_id}</code>", parse_mode="HTML")
        return

    if state == "broadcast" and is_admin(uid, d):
        sent = 0
        for u_id in d.get("verified", []):
            try:
                await ctx.bot.send_message(chat_id=u_id,
                    text=f"<b>Announcement</b>\n\n{esc(text)}", parse_mode="HTML")
                sent += 1
            except Exception:
                pass
        clear_state(d, uid)
        await update.message.reply_text(f"Broadcast sent to <b>{sent}</b> users.", parse_mode="HTML")
        return

    if state == "add_bal" and is_admin(uid, d):
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("Format: <code>USER_ID AMOUNT</code>", parse_mode="HTML"); return
        try:
            tid = int(parts[0]); amt = float(parts[1])
            if amt <= 0: raise ValueError
        except ValueError:
            await update.message.reply_text("Invalid input."); return
        d.setdefault("balances", {})
        cur = float(d["balances"].get(str(tid), 0.0))
        d["balances"][str(tid)] = round(cur + amt, 2)
        clear_state(d, uid)
        await update.message.reply_text(
            f"Balance updated.\nUser: <code>{tid}</code>\n"
            f"Added: <b>+${amt:.2f}</b>\nNew balance: <b>${cur+amt:.2f}</b>", parse_mode="HTML")
        try:
            await ctx.bot.send_message(chat_id=tid,
                text=f"{CE_WALLET} <b>Balance Added</b>\n\n+${amt:.2f} credited.\n"
                     f"New balance: <b>${cur+amt:.2f}</b>", parse_mode="HTML")
        except Exception:
            pass
        return

    if state == "ded_bal" and is_admin(uid, d):
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("Format: <code>USER_ID AMOUNT</code>", parse_mode="HTML"); return
        try:
            tid = int(parts[0]); amt = float(parts[1])
            if amt <= 0: raise ValueError
        except ValueError:
            await update.message.reply_text("Invalid input."); return
        d.setdefault("balances", {})
        cur = float(d["balances"].get(str(tid), 0.0))
        new = max(0.0, cur - amt)
        d["balances"][str(tid)] = round(new, 2)
        clear_state(d, uid)
        await update.message.reply_text(
            f"Balance updated.\nUser: <code>{tid}</code>\n"
            f"Deducted: <b>-${amt:.2f}</b>\nNew balance: <b>${new:.2f}</b>", parse_mode="HTML")
        return

    if state == "chk_bal" and is_admin(uid, d):
        try:
            tid = int(text)
        except ValueError:
            await update.message.reply_text("Send a valid numeric Telegram User ID."); return
        bal = float(d.get("balances", {}).get(str(tid), 0.0))
        clear_state(d, uid)
        await update.message.reply_text(
            f"User: <code>{tid}</code>\nBalance: <b>${bal:.2f}</b>", parse_mode="HTML")
        return

    # ── User is waiting to send screenshot — remind them ─────────────────────
    if state and state.startswith("waiting_ss|"):
        await update.message.reply_text(
            "📸 Please send a <b>screenshot</b> (photo) of your payment to proceed.",
            parse_mode="HTML")
        return

    # ── Menu buttons ──────────────────────────────────────────────────────────
    if text == "🛒 Shop":
        await update.message.reply_text(f"{CE_CART} <b>Select a category:</b>",
            parse_mode="HTML", reply_markup=kb_cats()); return

    if text == "👤 Account":
        bal   = float(d.get("balances", {}).get(str(uid), 0.0))
        role  = "Admin" if is_admin(uid, d) else "User"
        uname = update.effective_user.username or "N/A"
        await update.message.reply_text(
            f"{CE_ACCT} <b>Account Info</b>\n\n"
            f"Name: {esc(update.effective_user.full_name or 'N/A')}\n"
            f"Username: @{esc(uname)}\nID: <code>{uid}</code>\n"
            f"Role: <b>{role}</b>\n{CE_WALLET} Balance: <b>${bal:.2f}</b>\n"
            f"Status: <b>Verified</b>", parse_mode="HTML"); return

    if text == "📊 Stock":
        lines = [f"{CE_STATS} <b>Stock Status</b>\n"]
        for k in CAT_ORDER:
            cat = MENU[k]
            lines.append(f"{CAT_CE[k]} <b>{esc(cat['label'])}</b>")
            if cat.get("out_of_stock"):
                lines.append(f"  {CE_UNAVAIL} Out of Stock")
            else:
                for i, p in enumerate(cat["products"]):
                    keys_total  = sum(keys_count(k, i, dur, d) for dur, _ in p["prices"])
                    files_total = sum(files_count(k, i, dur, d) for dur, _ in p["prices"])
                    total = keys_total + files_total
                    dot   = CE_AVAIL if total > 0 else CE_UNAVAIL
                    if files_total > 0 and keys_total == 0:
                        stock_label = f"{total} files"
                    elif keys_total > 0 and files_total == 0:
                        stock_label = f"{total} items"
                    else:
                        stock_label = f"{total} items"
                    lines.append(f"  {dot} {p['ce']} {esc(p['name'])} [{stock_label}]")
            lines.append("")
        await update.message.reply_text("\n".join(lines), parse_mode="HTML"); return

    if text == "🔧 Admin Panel":
        if not is_admin(uid, d):
            await update.message.reply_text("Admins only."); return
        await update.message.reply_text(f"{CE_ADMIN} <b>Admin Panel</b>\n\nChoose an action:",
            parse_mode="HTML", reply_markup=kb_admin_panel()); return


# ═══════════════════════════════════════════════════════════════════════════════
#  CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════════════════════════
async def handle_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q   = update.callback_query
    await q.answer()
    d   = load()
    uid = q.from_user.id
    cb  = q.data

    # ── Verify ────────────────────────────────────────────────────────────────
    if cb == "verify":
        msg, ok = await run_verify(q, uid, ctx)
        if ok:
            if uid not in d.get("verified", []):
                d.setdefault("verified", []).append(uid)
                save(d)
            name = esc(q.from_user.first_name or "there")
            try:
                await msg.edit_text(
                    f"<b>Access Granted!</b>\n\nWelcome, <b>{name}</b>! You are verified.\n"
                    f"Use the menu below to shop.", parse_mode="HTML")
            except Exception:
                pass
            await q.message.reply_text("<b>Main Menu</b>", parse_mode="HTML",
                                       reply_markup=kb_main(uid, d))
        else:
            try:
                await msg.edit_text(
                    "<b>Verification Failed</b>\n\nYou must join our channel to use this bot.\n"
                    "After joining, press /start again.")
            except Exception:
                pass
        return

    if not is_verified(uid, d):
        await q.answer("Please verify first. Use /start", show_alert=True); return

    # ── Approve order (admin action) ──────────────────────────────────────────
    if cb.startswith("approve|"):
        if not is_admin(uid, d):
            await q.answer("Admins only.", show_alert=True); return
        order_id = cb[8:]
        order    = d.get("pending_orders", {}).get(order_id)
        if not order:
            await q.answer("Order not found or already processed.", show_alert=True)
            try:
                await q.edit_message_reply_markup(reply_markup=None)
            except Exception:
                pass
            return
        user_id = order["user_id"]
        success = await deliver_product(user_id, order, ctx)
        d2 = load()
        d2.get("pending_orders", {}).pop(order_id, None)
        save(d2)
        if success:
            await q.answer("✅ Approved! Product delivered.", show_alert=False)
            try:
                await q.edit_message_caption(
                    caption=(q.message.caption or "") + "\n\n✅ <b>APPROVED</b> by admin",
                    parse_mode="HTML", reply_markup=None)
            except Exception:
                pass
        else:
            await q.answer("❌ No stock available to deliver!", show_alert=True)
            try:
                await q.edit_message_caption(
                    caption=(q.message.caption or "") + "\n\n⚠️ <b>APPROVED but NO STOCK</b>",
                    parse_mode="HTML", reply_markup=None)
            except Exception:
                pass
            try:
                await ctx.bot.send_message(chat_id=user_id,
                    text=f"⚠️ <b>Payment approved but product is out of stock.</b>\n\n"
                         f"Please contact admin: {SUPPORT_CONTACTS}", parse_mode="HTML")
            except Exception:
                pass
        return

    # ── Deny order (admin action) ─────────────────────────────────────────────
    if cb.startswith("deny|"):
        if not is_admin(uid, d):
            await q.answer("Admins only.", show_alert=True); return
        order_id = cb[5:]
        order    = d.get("pending_orders", {}).get(order_id)
        if not order:
            await q.answer("Order not found or already processed.", show_alert=True)
            try:
                await q.edit_message_reply_markup(reply_markup=None)
            except Exception:
                pass
            return
        user_id = order["user_id"]
        d.get("pending_orders", {}).pop(order_id, None)
        save(d)
        await q.answer("❌ Denied.", show_alert=False)
        try:
            await q.edit_message_caption(
                caption=(q.message.caption or "") + "\n\n❌ <b>DENIED</b> by admin",
                parse_mode="HTML", reply_markup=None)
        except Exception:
            pass
        try:
            await ctx.bot.send_message(chat_id=user_id,
                text=f"{CE_DENY} <b>Approval Denied</b> please contact admin",
                parse_mode="HTML")
        except Exception:
            pass
        return

    # ── Category browsing ─────────────────────────────────────────────────────
    if cb == "cats":
        try:
            await q.edit_message_text(f"{CE_CART} <b>Select a category:</b>",
                parse_mode="HTML", reply_markup=kb_cats())
        except Exception:
            await q.message.reply_text(f"{CE_CART} <b>Select a category:</b>",
                parse_mode="HTML", reply_markup=kb_cats())
        return

    if cb.startswith("cat|"):
        k   = cb[4:]
        cat = MENU.get(k)
        if not cat: return
        text = cat_msg(k)
        kb   = (InlineKeyboardMarkup([[InlineKeyboardButton("⬅️  Back", callback_data="cats")]])
                if cat.get("out_of_stock") else kb_cat(k))
        try:
            await q.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            await q.message.reply_text(text, parse_mode="HTML", reply_markup=kb)
        return

    if cb.startswith("prod|"):
        _, k, si = cb.split("|"); i = int(si)
        cat = MENU.get(k)
        if not cat or i >= len(cat["products"]): return
        p     = cat["products"][i]
        total = total_product_stock(k, i, d)
        txt   = (f"{p['ce']} <b>{esc(p['name'])}</b>\n\n"
                 f"{CE_STATUS} Status: Good &amp; Safe\n"
                 f"📦 In stock: <b>{total}</b>\n\n"
                 f"<b>Select a duration:</b>")
        try:
            await q.edit_message_text(txt, parse_mode="HTML", reply_markup=kb_durations(k, i, p, d))
        except Exception:
            await q.message.reply_text(txt, parse_mode="HTML", reply_markup=kb_durations(k, i, p, d))
        return

    if cb.startswith("dur|"):
        _, k, si, dur, price = cb.split("|", 4); i = int(si)
        cat = MENU.get(k)
        if not cat or i >= len(cat["products"]): return
        p   = cat["products"][i]
        qty = slot_stock(k, i, dur, d)
        txt = (f"{p['ce']} <b>{esc(p['name'])}</b>\n"
               f"Duration: <b>{esc(dur)}</b>  |  Price: <b>${esc(price)}</b>\n"
               f"📦 In stock: <b>{qty}</b>\n\n"
               f"<b>Choose your payment method:</b>")
        try:
            await q.edit_message_text(txt, parse_mode="HTML", reply_markup=kb_payment(k, i, dur, price))
        except Exception:
            await q.message.reply_text(txt, parse_mode="HTML", reply_markup=kb_payment(k, i, dur, price))
        return

    if cb.startswith("pay|"):
        parts  = cb.split("|", 6)
        method = parts[1]
        k, si, dur, price = parts[2], parts[3], parts[4], parts[5]; i = int(si)
        cat = MENU.get(k)
        if not cat or i >= len(cat["products"]): return
        await send_payment_details(q.message, k, i, dur, price, method, ctx)
        return

    # ── User confirms payment sent → ask for screenshot ───────────────────────
    if cb.startswith("paid|"):
        parts  = cb.split("|", 6)
        k, si, dur, price, method = parts[1], parts[2], parts[3], parts[4], parts[5]; i = int(si)
        cat = MENU.get(k)
        if not cat or i >= len(cat["products"]): return
        p = cat["products"][i]

        if slot_stock(k, i, dur, d) == 0:
            await q.answer("No stock available! Contact admin.", show_alert=True)
            all_admins = list(set(ADMIN_IDS + d.get("admin_ids", [])))
            for aid in all_admins:
                try:
                    await ctx.bot.send_message(chat_id=aid,
                        text=f"⚠️ <b>Out of Stock</b>\n\nUser: <code>{uid}</code>\n"
                             f"Product: {esc(p['name'])}\nDuration: {esc(dur)}\n"
                             f"Please add stock!", parse_mode="HTML")
                except Exception:
                    pass
            return

        set_state(d, uid, f"waiting_ss|{k}|{i}|{dur}|{price}|{method}")
        await q.message.reply_text(
            "📸 <b>Send Payment Screenshot</b>\n\n"
            "Please send a <b>screenshot</b> of your payment as a photo.\n"
            "An admin will review and approve your order.",
            parse_mode="HTML")
        return

    # ── Admin: Add Files button navigation ────────────────────────────────────
    if cb.startswith("afc|"):
        if not is_admin(uid, d): await q.answer("Admins only.", show_alert=True); return
        cat_key = cb[4:]
        cat = MENU.get(cat_key)
        if not cat: await q.answer("Unknown category."); return
        await q.edit_message_text(
            f"📁 <b>Add Files</b> — <b>{esc(cat['label'])}</b>\n\nSelect a product:",
            parse_mode="HTML", reply_markup=kb_adm_prods("f", cat_key))
        return

    if cb.startswith("afp|"):
        if not is_admin(uid, d): await q.answer("Admins only.", show_alert=True); return
        _, cat_key, idx_str = cb.split("|", 2)
        idx = int(idx_str)
        cat = MENU.get(cat_key)
        if not cat or idx >= len(cat["products"]): await q.answer("Not found."); return
        prod = cat["products"][idx]
        await q.edit_message_text(
            f"📁 <b>Add Files</b> — <b>{esc(prod['name'])}</b>\n\nSelect a duration:",
            parse_mode="HTML", reply_markup=kb_adm_durs("f", cat_key, idx))
        return

    if cb.startswith("afd|"):
        if not is_admin(uid, d): await q.answer("Admins only.", show_alert=True); return
        parts = cb.split("|")
        cat_key, idx_str, dur_enc = parts[1], parts[2], parts[3]
        idx = int(idx_str)
        dur = dur_enc.replace("~", " ")
        cat = MENU.get(cat_key)
        if not cat or idx >= len(cat["products"]): await q.answer("Not found."); return
        prod = cat["products"][idx]
        set_state(d, uid, f"add_files_item|{cat_key}|{idx}|{dur}")
        await q.edit_message_text(
            f"📁 <b>Add Files</b>\n\n"
            f"Product: <b>{esc(prod['name'])}</b>\n"
            f"Duration: <b>{esc(dur)}</b>\n\n"
            f"Now send the file:\n"
            f"• IPA / APK / ZIP → send as <b>document</b>\n"
            f"• Image → send as <b>photo</b>\n"
            f"• Download link → send as <b>text message</b>",
            parse_mode="HTML")
        return

    # ── Admin: Add Keys button navigation ─────────────────────────────────────
    if cb.startswith("akc|"):
        if not is_admin(uid, d): await q.answer("Admins only.", show_alert=True); return
        cat_key = cb[4:]
        cat = MENU.get(cat_key)
        if not cat: await q.answer("Unknown category."); return
        await q.edit_message_text(
            f"🔑 <b>Add Keys</b> — <b>{esc(cat['label'])}</b>\n\nSelect a product:",
            parse_mode="HTML", reply_markup=kb_adm_prods("k", cat_key))
        return

    if cb.startswith("akp|"):
        if not is_admin(uid, d): await q.answer("Admins only.", show_alert=True); return
        _, cat_key, idx_str = cb.split("|", 2)
        idx = int(idx_str)
        cat = MENU.get(cat_key)
        if not cat or idx >= len(cat["products"]): await q.answer("Not found."); return
        prod = cat["products"][idx]
        await q.edit_message_text(
            f"🔑 <b>Add Keys</b> — <b>{esc(prod['name'])}</b>\n\nSelect a duration:",
            parse_mode="HTML", reply_markup=kb_adm_durs("k", cat_key, idx))
        return

    if cb.startswith("akd|"):
        if not is_admin(uid, d): await q.answer("Admins only.", show_alert=True); return
        parts = cb.split("|")
        cat_key, idx_str, dur_enc = parts[1], parts[2], parts[3]
        idx = int(idx_str)
        dur = dur_enc.replace("~", " ")
        cat = MENU.get(cat_key)
        if not cat or idx >= len(cat["products"]): await q.answer("Not found."); return
        prod = cat["products"][idx]
        set_state(d, uid, f"add_keys_item|{cat_key}|{idx}|{dur}")
        await q.edit_message_text(
            f"🔑 <b>Add Keys</b>\n\n"
            f"Product: <b>{esc(prod['name'])}</b>\n"
            f"Duration: <b>{esc(dur)}</b>\n\n"
            f"Send your keys — one key per line:",
            parse_mode="HTML")
        return

    # ── Admin panel ────────────────────────────────────────────────────────────
    if cb.startswith("adm|"):
        if not is_admin(uid, d):
            await q.answer("Admins only.", show_alert=True); return
        action = cb[4:]

        if action == "add_keys":
            clear_state(d, uid)
            await q.message.reply_text(
                "🔑 <b>Add Keys</b>\n\nSelect a category:",
                parse_mode="HTML", reply_markup=kb_adm_cats("k"))

        elif action == "add_files":
            clear_state(d, uid)
            await q.message.reply_text(
                "📁 <b>Add Files</b>\n\nSelect a category:",
                parse_mode="HTML", reply_markup=kb_adm_cats("f"))

        elif action == "view_keys":
            lines = [f"{CE_KEY} <b>Stock (Keys + Files)</b>\n"]
            for k in CAT_ORDER:
                cat = MENU[k]
                if cat.get("out_of_stock") or not cat["products"]: continue
                lines.append(f"{CAT_CE[k]} <b>{esc(cat['label'])}</b>")
                for i, p in enumerate(cat["products"]):
                    for dur, _ in p["prices"]:
                        kqty = keys_count(k, i, dur, d)
                        fqty = files_count(k, i, dur, d)
                        total = kqty + fqty
                        dot = CE_AVAIL if total > 0 else CE_UNAVAIL
                        detail = f"{kqty}k/{fqty}f" if (kqty or fqty) else "0"
                        lines.append(f"  {dot} {esc(p['name'])} — {esc(dur)}: <b>{total}</b> [{detail}]")
                lines.append("")
            await q.message.reply_text("\n".join(lines), parse_mode="HTML")

        elif action == "add_bal":
            set_state(d, uid, "add_bal")
            await q.message.reply_text("<b>Add Balance</b>\n\nSend: <code>USER_ID AMOUNT</code>", parse_mode="HTML")
        elif action == "ded_bal":
            set_state(d, uid, "ded_bal")
            await q.message.reply_text("<b>Deduct Balance</b>\n\nSend: <code>USER_ID AMOUNT</code>", parse_mode="HTML")
        elif action == "chk_bal":
            set_state(d, uid, "chk_bal")
            await q.message.reply_text("Send the User ID to check balance:")
        elif action == "add_admin":
            set_state(d, uid, "admin_id")
            await q.message.reply_text("Send the Telegram User ID of the new admin:")
        elif action == "broadcast":
            set_state(d, uid, "broadcast")
            await q.message.reply_text("Type your broadcast message:")

        elif action == "clear":
            await q.message.reply_text("<b>Clear ALL keys?</b> This cannot be undone.", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Yes, clear all", callback_data="adm|confirm_clear"),
                    InlineKeyboardButton("Cancel",         callback_data="adm|cancel"),
                ]]))
        elif action == "confirm_clear":
            d["keys"] = {}; save(d)
            await q.edit_message_text("All keys cleared.")

        elif action == "clear_files":
            await q.message.reply_text("<b>Clear ALL files?</b> This cannot be undone.", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Yes, clear all files", callback_data="adm|confirm_clear_files"),
                    InlineKeyboardButton("Cancel",               callback_data="adm|cancel"),
                ]]))
        elif action == "confirm_clear_files":
            d["files"] = {}; save(d)
            await q.edit_message_text("All files cleared.")

        elif action == "cancel":
            await q.edit_message_text("Cancelled.")
        return


# ═══════════════════════════════════════════════════════════════════════════════
#  ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════════════════
async def on_error(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    err = ctx.error
    if isinstance(err, (Conflict, NetworkError, TimedOut)):
        logger.warning(f"Transient: {err}"); return
    logger.error(f"Error: {err}", exc_info=err)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    try:
        result = subprocess.run(["pgrep", "-f", "python3 bot.py"], capture_output=True, text=True)
        for pid_str in result.stdout.strip().splitlines():
            pid = int(pid_str.strip())
            if pid != os.getpid():
                try:
                    os.kill(pid, signal.SIGTERM)
                except Exception:
                    pass
    except Exception:
        pass

    for _f in [DATA_FILE, DATA_FILE + ".tmp", "bot_persistence"]:
        if Path(_f).exists():
            try: os.chmod(_f, 0o666)
            except Exception: pass

    persistence = PicklePersistence(filepath="bot_persistence")
    app = (ApplicationBuilder().token(BOT_TOKEN).persistence(persistence)
           .read_timeout(30).write_timeout(30).connect_timeout(30).build())

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_help))
    app.add_handler(CallbackQueryHandler(handle_cb))

    # Media handler: photos and documents (screenshots + admin file uploads)
    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.Document.ALL) & filters.ChatType.PRIVATE,
        handle_media))

    # Text handler
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_text))

    app.add_error_handler(on_error)

    print("=" * 50)
    print("  Shop Bot started!")
    print(f"  Admins: {ADMIN_IDS}")
    print("=" * 50)
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    main()
