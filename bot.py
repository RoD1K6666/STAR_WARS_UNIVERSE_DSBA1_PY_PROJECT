"""
Star Wars dataset - Telegram bot.

A menu-driven companion to the Streamlit project. From the inline menu you can
pull any part of the analysis: descriptive statistics, plots, a character
lookup, and an "add a character" form that writes a new row into the dataset
(the bot's equivalent of the FastAPI POST endpoint).

Run:
    export BOT_TOKEN="<token from @BotFather>"
    python bot.py
"""

import asyncio
import io
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters,
)

# ── Data ──────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archive", "csv")


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, f"{name}.csv"))


# ── Star Wars plot styling ────────────────────────────────────────────────────
YELLOW, BLUE, PANEL = "#FFE81F", "#4BD5EE", "#0e0e0e"
plt.style.use("dark_background")
plt.rcParams.update({
    "figure.facecolor": PANEL, "axes.facecolor": PANEL,
    "axes.edgecolor": "#333", "axes.labelcolor": "#d6d6d6",
    "xtick.color": "#d6d6d6", "ytick.color": "#d6d6d6",
    "text.color": "#d6d6d6", "grid.color": "#222", "grid.alpha": 0.5,
    "axes.titlecolor": YELLOW,
})


def fig_to_bytes(fig) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor=PANEL)
    plt.close(fig)
    buf.seek(0)
    return buf


# ── Keyboards ─────────────────────────────────────────────────────────────────
def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Statistics", callback_data="stats"),
         InlineKeyboardButton("📈 Plots", callback_data="plots")],
        [InlineKeyboardButton("🔍 Find a character", callback_data="search"),
         InlineKeyboardButton("➕ Add a character", callback_data="add")],
        [InlineKeyboardButton("ℹ️ About the project", callback_data="about")],
    ])


def plots_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Height distribution", callback_data="plot_hist")],
        [InlineKeyboardButton("Height vs weight", callback_data="plot_scatter")],
        [InlineKeyboardButton("Tallest species", callback_data="plot_species")],
        [InlineKeyboardButton("Ship length vs crew", callback_data="plot_ships")],
        [InlineKeyboardButton("« Back", callback_data="home")],
    ])


def back_home() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("« Menu", callback_data="home")]])


INTRO = (
    "*STAR WARS UNIVERSE*\n"
    "Dataset analytics for the DSBA1 Python project.\n\n"
    "By Tiniakov Rodion and Belousov Zakhar.\n\n"
    "Pick a section below to pull any part of the analysis."
)


# ── Command / menu handlers ───────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(INTRO, parse_mode="Markdown", reply_markup=main_menu())


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "home":
        context.user_data.clear()
        await q.edit_message_text(INTRO, parse_mode="Markdown", reply_markup=main_menu())

    elif data == "stats":
        await q.edit_message_text(stats_text(), parse_mode="Markdown", reply_markup=back_home())

    elif data == "about":
        await q.edit_message_text(about_text(), parse_mode="Markdown",
                                  reply_markup=back_home(), disable_web_page_preview=True)

    elif data == "plots":
        await q.edit_message_text("Choose a plot:", reply_markup=plots_menu())

    elif data.startswith("plot_"):
        await send_plot(q, context, data)

    elif data == "search":
        context.user_data["mode"] = "search"
        await q.edit_message_text(
            "🔍 Send me a *name* or *species* to look up.\n_e.g. Luke, Yoda, Wookiee_",
            parse_mode="Markdown", reply_markup=back_home())

    elif data == "add":
        context.user_data["mode"] = "add_name"
        context.user_data["new"] = {}
        await q.edit_message_text(
            "➕ *New character* - step 1 of 4\n\nSend the character's *name*:",
            parse_mode="Markdown", reply_markup=back_home())


# ── Plots ─────────────────────────────────────────────────────────────────────
async def send_plot(q, context, which: str):
    chars = load("characters").dropna(subset=["height", "weight"])
    ships = load("starships").dropna(subset=["length", "crew"])

    if which == "plot_hist":
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(chars["height"], bins=15, color=BLUE, edgecolor=PANEL)
        ax.set_title("Character height distribution")
        ax.set_xlabel("Height (m)"); ax.set_ylabel("Count")
        caption = "Heights cluster around ~1.80 m - roughly bell-shaped."

    elif which == "plot_scatter":
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.scatter(chars["height"], chars["weight"], color=YELLOW, s=28, edgecolor=PANEL)
        ax.set_title("Height vs weight")
        ax.set_xlabel("Height (m)"); ax.set_ylabel("Weight (kg)")
        caption = "Taller characters tend to weigh more - with loud exceptions."

    elif which == "plot_species":
        top = chars["species"].value_counts().head(6).index
        avg = (chars[chars["species"].isin(top)]
               .groupby("species")["height"].mean().sort_values())
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.barh(avg.index, avg.values, color=YELLOW)
        ax.set_title("Average height by species")
        ax.set_xlabel("Height (m)")
        caption = "Wookiees stand tallest; humans sit near the mean."

    else:  # plot_ships
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.scatter(ships["length"], ships["crew"], color=BLUE, s=30, edgecolor=PANEL)
        ax.set_yscale("log")
        ax.set_title("Starship length vs crew")
        ax.set_xlabel("Length (m)"); ax.set_ylabel("Crew (log)")
        caption = "Bigger hulls need bigger crews - the Executor is off the chart."

    await q.message.reply_photo(fig_to_bytes(fig), caption=caption)
    await q.message.reply_text("More plots or back to the menu?", reply_markup=plots_menu())


# ── Text routing (search + add form) ──────────────────────────────────────────
async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    text = update.message.text.strip()

    if mode == "search":
        await do_search(update, text)

    elif mode == "add_name":
        context.user_data["new"]["name"] = text
        context.user_data["mode"] = "add_species"
        await update.message.reply_text("Step 2 of 4 - *species*? (or send `-` to skip)",
                                        parse_mode="Markdown")

    elif mode == "add_species":
        context.user_data["new"]["species"] = None if text == "-" else text
        context.user_data["mode"] = "add_height"
        await update.message.reply_text("Step 3 of 4 - *height in metres*? _e.g. 1.83_",
                                        parse_mode="Markdown")

    elif mode == "add_height":
        val = parse_float(text)
        if val is None:
            await update.message.reply_text("Please send a number, e.g. `1.83`.", parse_mode="Markdown")
            return
        context.user_data["new"]["height"] = val
        context.user_data["mode"] = "add_weight"
        await update.message.reply_text("Step 4 of 4 - *weight in kg*? _e.g. 77_",
                                        parse_mode="Markdown")

    elif mode == "add_weight":
        val = parse_float(text)
        if val is None:
            await update.message.reply_text("Please send a number, e.g. `77`.", parse_mode="Markdown")
            return
        context.user_data["new"]["weight"] = val
        await save_character(update, context)

    else:
        await update.message.reply_text("Use the menu - send /start.", reply_markup=main_menu())


async def do_search(update: Update, text: str):
    df = load("characters")
    res = df[df["name"].str.contains(text, case=False, na=False) |
             df["species"].str.contains(text, case=False, na=False)]
    if res.empty:
        await update.message.reply_text(f"Nothing found for “{text}”. Try again or « Menu.",
                                        reply_markup=back_home())
        return
    lines = [f"*{len(res)} found:*\n"]
    for _, r in res.head(10).iterrows():
        h = f"{r['height']:.2f} m" if pd.notna(r.get("height")) else "-"
        w = f"{r['weight']:.0f} kg" if pd.notna(r.get("weight")) else "-"
        sp = r.get("species") if pd.notna(r.get("species")) else "-"
        lines.append(f"⚔️ *{r['name']}* - {sp}\n    {h}, {w}")
    if len(res) > 10:
        lines.append(f"\n…and {len(res) - 10} more.")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown", reply_markup=back_home())


async def save_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new = context.user_data["new"]
    df = load("characters")
    new_id = int(df["id"].max()) + 1 if "id" in df.columns else len(df) + 1
    row = {"id": new_id, "name": new["name"], "species": new.get("species"),
           "height": new["height"], "weight": new["weight"]}
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(os.path.join(DATA_DIR, "characters.csv"), index=False)
    context.user_data.clear()
    await update.message.reply_text(
        f"✅ *Added to the dataset!*\n\n"
        f"⚔️ *{row['name']}* (id {new_id})\n"
        f"Species: {row['species'] or '-'}\n"
        f"{row['height']:.2f} m, {row['weight']:.0f} kg",
        parse_mode="Markdown", reply_markup=main_menu())


# ── Text builders ─────────────────────────────────────────────────────────────
def stats_text() -> str:
    c = load("characters"); s = load("starships"); p = load("planets")
    h, w = c["height"].dropna(), c["weight"].dropna()
    ln = s["length"].dropna()
    return (
        "📊 *Descriptive statistics*\n\n"
        "*Characters*\n"
        f"  height - mean {h.mean():.2f} m, median {h.median():.2f}, std {h.std():.2f}\n"
        f"  weight - mean {w.mean():.0f} kg, median {w.median():.0f}, std {w.std():.0f}\n\n"
        "*Starships*\n"
        f"  length - median {ln.median():.0f} m, mean {ln.mean():.0f} m\n\n"
        f"Tables on file: characters {len(c)}, starships {len(s)}, planets {len(p)}."
    )


def about_text() -> str:
    return (
        "ℹ️ *Project description*\n\n"
        "Analytics across Star Wars universe data set across five main tables "
        "(characters, starships, planets, species, weapons).\n\n"
        "By *Tiniakov Rodion* & *Belousov Zakhar* (group 256-1)\n\n"
        "Full notebook & interactive site are built in Streamlit.\n"
        "This bot mirrors the key pieces."
    )


def parse_float(text: str):
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit("Set the BOT_TOKEN environment variable (token from @BotFather).")

    # Python 3.12+ no longer auto-creates an event loop in the main thread;
    # PTB's run_webhook/run_polling helpers expect one to exist.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    external_url = os.environ.get("RENDER_EXTERNAL_URL")
    port = int(os.environ.get("PORT", "0"))
    if external_url and port:
        # Hosted (e.g. Render): run as a web service via webhook
        print(f"Bot running via webhook at {external_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token,
            webhook_url=f"{external_url}/{token}",
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        # Local: long polling
        print("Bot is running (polling). Press Ctrl+C to stop.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
