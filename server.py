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
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
