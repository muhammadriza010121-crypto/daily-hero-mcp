"""Daily Hero MCP Server — Remote proxy for Daily Hero API."""

import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = os.environ.get("DAILY_HERO_BASE_URL", "https://daily-hero.vercel.app")
API_KEY = os.environ.get("DAILY_HERO_API_KEY", "")
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

mcp = FastMCP(
    "Daily Hero",
    stateless_http=True,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000)),
)


async def _get(path: str, params: dict | None = None) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}{path}", headers=HEADERS, params=params)
        return resp.text


async def _post(path: str, body: dict) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{BASE_URL}{path}", headers=HEADERS, json=body)
        return resp.text


async def _put(path: str, body: dict) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.put(f"{BASE_URL}{path}", headers=HEADERS, json=body)
        return resp.text


async def _delete(path: str, body: dict) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.request("DELETE", f"{BASE_URL}{path}", headers=HEADERS, json=body)
        return resp.text


# ============================================================
# ЗАДАЧИ
# ============================================================

@mcp.tool()
async def list_tasks(status: str = "", direction: str = "", focus: str = "") -> str:
    """Получить список задач. Фильтры: status (📥 Входящие / 🔄 В работе / ⏳ Ждёт / ✅ Готово), direction (👨‍👩‍👧 Личное / 🅿️ Паркинг / Мысли/Идеи / Эффективность / Daily Hero / ФЦП), focus (🔴 Срочно / 🟡 Важно)."""
    params = {}
    if status:
        params["status"] = status
    if direction:
        params["direction"] = direction
    if focus:
        params["focus"] = focus
    return await _get("/api/tasks", params or None)


@mcp.tool()
async def create_task(
    title: str,
    status: str = "📥 Входящие",
    direction: str = "",
    focus: str = "",
    energy: str = "",
    due_date: str = "",
    comment: str = "",
) -> str:
    """Создать задачу. title обязателен. direction: 👨‍👩‍👧 Личное / 🅿️ Паркинг / Мысли/Идеи / Эффективность / Daily Hero / ФЦП. focus: 🔴 Срочно / 🟡 Важно. energy: ⚡ Быстрая / 🧠 Думать / 💪 Тяжёлая. due_date: YYYY-MM-DD."""
    body: dict = {"title": title, "status": status}
    if direction:
        body["direction"] = direction
    if focus:
        body["focus"] = focus
    if energy:
        body["energy"] = energy
    if due_date:
        body["due_date"] = due_date
    if comment:
        body["comment"] = comment
    return await _post("/api/tasks", body)


@mcp.tool()
async def update_task(
    id: str,
    title: str = "",
    status: str = "",
    direction: str = "",
    focus: str = "",
    energy: str = "",
    due_date: str = "",
    comment: str = "",
) -> str:
    """Обновить задачу по id. Передай только поля которые нужно изменить."""
    body: dict = {"id": id}
    if title:
        body["title"] = title
    if status:
        body["status"] = status
    if direction:
        body["direction"] = direction
    if focus:
        body["focus"] = focus
    if energy:
        body["energy"] = energy
    if due_date:
        body["due_date"] = due_date
    if comment:
        body["comment"] = comment
    return await _put("/api/tasks", body)


@mcp.tool()
async def delete_task(id: str) -> str:
    """Удалить задачу по id."""
    return await _delete("/api/tasks", {"id": id})


# ============================================================
# ПРИВЫЧКИ
# ============================================================

@mcp.tool()
async def get_dashboard(date: str = "") -> str:
    """Получить данные дня: привычки, вода, сон, активность, score. date в формате YYYY-MM-DD (по умолчанию сегодня)."""
    params = {}
    if date:
        params["date"] = date
    return await _get("/api/dashboard", params or None)


@mcp.tool()
async def mark_habit(habit_id: str, date: str, status: str) -> str:
    """Отметить привычку. status: done / skip / miss / null (снять отметку). date: YYYY-MM-DD."""
    body: dict = {"habit_id": habit_id, "date": date, "status": status if status != "null" else None}
    return await _post("/api/habit", body)


@mcp.tool()
async def list_habits() -> str:
    """Получить список всех привычек с их id, названиями и порядком."""
    return await _get("/api/habits/manage")


@mcp.tool()
async def get_habit_stats(month: str = "") -> str:
    """Статистика привычек за месяц. month: YYYY-MM (по умолчанию текущий)."""
    params = {}
    if month:
        params["month"] = month
    return await _get("/api/habits/stats", params or None)


# ============================================================
# ВОДА
# ============================================================

@mcp.tool()
async def add_water(date: str, amount_ml: int, water_type: str = "manual") -> str:
    """Добавить запись воды. date: YYYY-MM-DD, amount_ml: количество мл (50/250/500), type: manual/morning/before_meal/before_sleep."""
    return await _post("/api/water", {"date": date, "amount_ml": amount_ml, "type": water_type})


@mcp.tool()
async def undo_water(date: str) -> str:
    """Отменить последнюю запись воды за день. date: YYYY-MM-DD."""
    return await _post("/api/water/undo", {"date": date})


# ============================================================
# СОН
# ============================================================

@mcp.tool()
async def log_sleep(
    date: str,
    bedtime: str,
    waketime: str,
    quality: int = 3,
    nap_start: str = "",
    nap_end: str = "",
) -> str:
    """Записать сон. date: YYYY-MM-DD, bedtime/waketime: HH:MM, quality: 1-5, nap_start/nap_end: HH:MM (опционально)."""
    body: dict = {"date": date, "bedtime": bedtime, "waketime": waketime, "quality": quality}
    if nap_start:
        body["nap_start"] = nap_start
    if nap_end:
        body["nap_end"] = nap_end
    return await _post("/api/sleep", body)


# ============================================================
# ПРОФИЛЬ
# ============================================================

@mcp.tool()
async def get_profile() -> str:
    """Получить профиль: имя, вес, норма воды, цели шагов и strain, уровень, XP, стрик."""
    return await _get("/api/profile")


@mcp.tool()
async def update_profile(
    display_name: str = "",
    weight_kg: float = 0,
    water_norm_ml: int = 0,
    steps_goal: int = 0,
    strain_goal: float = 0,
) -> str:
    """Обновить профиль. Передай только поля которые нужно изменить."""
    body: dict = {}
    if display_name:
        body["display_name"] = display_name
    if weight_kg > 0:
        body["weight_kg"] = weight_kg
    if water_norm_ml > 0:
        body["water_norm_ml"] = water_norm_ml
    if steps_goal > 0:
        body["steps_goal"] = steps_goal
    if strain_goal > 0:
        body["strain_goal"] = strain_goal
    return await _put("/api/profile", body)


# ============================================================
# АНАЛИТИКА
# ============================================================

@mcp.tool()
async def get_analytics(period: str = "week") -> str:
    """Аналитика за период. period: week / month."""
    return await _get("/api/analytics", {"period": period})


# ============================================================
# ROUTINE (TIMELINE)
# ============================================================

@mcp.tool()
async def routine_get_steps() -> str:
    """Get all routine timeline steps (morning/evening blocks, prayers, etc.)."""
    return await _get("/api/routine")


@mcp.tool()
async def routine_create_step(
    title: str,
    block: str,
    time_start: str,
    time_end: str,
    sort_order: int = 0,
    icon: str = "",
    is_active: bool = True,
) -> str:
    """Create a routine step. block: morning/evening/prayer. time_start/time_end: HH:MM."""
    body: dict = {
        "title": title,
        "block": block,
        "time_start": time_start,
        "time_end": time_end,
        "sort_order": sort_order,
        "is_active": is_active,
    }
    if icon:
        body["icon"] = icon
    return await _post("/api/routine", body)


@mcp.tool()
async def routine_update_step(
    id: str,
    title: str = "",
    block: str = "",
    time_start: str = "",
    time_end: str = "",
    sort_order: int = -1,
    icon: str = "",
    is_active: bool = True,
) -> str:
    """Update a routine step by id. Pass only fields to change."""
    body: dict = {"id": id}
    if title:
        body["title"] = title
    if block:
        body["block"] = block
    if time_start:
        body["time_start"] = time_start
    if time_end:
        body["time_end"] = time_end
    if sort_order >= 0:
        body["sort_order"] = sort_order
    if icon:
        body["icon"] = icon
    body["is_active"] = is_active
    return await _put("/api/routine", body)


@mcp.tool()
async def routine_delete_step(id: str) -> str:
    """Delete a routine step by id."""
    return await _delete("/api/routine", {"id": id})


@mcp.tool()
async def routine_get_entries(date: str) -> str:
    """Get routine entries (done/skip/miss) for a specific date. date: YYYY-MM-DD."""
    return await _get("/api/routine/entries", {"date": date})


@mcp.tool()
async def routine_mark_step(step_id: str, date: str, status: str) -> str:
    """Mark a routine step for a date. status: done / skip / miss / null (clear)."""
    body: dict = {
        "step_id": step_id,
        "date": date,
        "status": status if status != "null" else None,
    }
    return await _post("/api/routine/entries", body)


# ============================================================
# DAY MODE
# ============================================================

@mcp.tool()
async def get_day_mode(date: str) -> str:
    """Get day mode (work/rest/travel/sick) for a date. date: YYYY-MM-DD."""
    return await _get("/api/routine/day-mode", {"date": date})


@mcp.tool()
async def set_day_mode(date: str, mode: str) -> str:
    """Set day mode. date: YYYY-MM-DD, mode: work / rest / travel / sick."""
    return await _post("/api/routine/day-mode", {"date": date, "mode": mode})


# ============================================================
# PRAYER TIMES
# ============================================================

@mcp.tool()
async def get_prayer_times(date: str, city: str = "Almaty") -> str:
    """Get prayer times for a date and city. date: YYYY-MM-DD, city: default Almaty."""
    return await _get("/api/prayer-times", {"date": date, "city": city})


# ============================================================
# FEEDBACK
# ============================================================

@mcp.tool()
async def feedback_list() -> str:
    """Get all feedback entries (user notes, ideas, bug reports)."""
    return await _get("/api/feedback")


@mcp.tool()
async def feedback_create(
    text: str,
    category: str = "idea",
    priority: str = "normal",
) -> str:
    """Create a feedback entry. category: idea / bug / note. priority: low / normal / high."""
    return await _post("/api/feedback", {
        "text": text,
        "category": category,
        "priority": priority,
    })


@mcp.tool()
async def feedback_mark_read(id: str) -> str:
    """Mark a feedback entry as read by id."""
    return await _put("/api/feedback", {"id": id, "is_read": True})


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
