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
# БАЗА ЗНАНИЙ (KNOWLEDGE)
# ============================================================

@mcp.tool()
async def knowledge_list(category: str = "") -> str:
    """Получить все записи базы знаний. Категории: strategies / principles / notes / wisdom. Без параметра — все записи."""
    params = {}
    if category:
        params["category"] = category
    return await _get("/api/knowledge", params or None)


@mcp.tool()
async def knowledge_search(q: str) -> str:
    """Поиск по базе знаний (title + content). Возвращает до 20 записей с превью контента."""
    return await _get("/api/knowledge/search", {"q": q})


@mcp.tool()
async def knowledge_create(
    title: str,
    content: str,
    category: str = "notes",
    tags: str = "",
    pinned: bool = False,
) -> str:
    """Создать запись в базе знаний. category: strategies / principles / notes / wisdom. tags: через запятую."""
    body: dict = {
        "title": title,
        "content": content,
        "category": category,
        "pinned": pinned,
    }
    if tags:
        body["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
    return await _post("/api/knowledge", body)


@mcp.tool()
async def knowledge_update(
    id: str,
    title: str = "",
    content: str = "",
    category: str = "",
    tags: str = "",
    pinned: bool = False,
) -> str:
    """Обновить запись базы знаний по id. Передай только поля которые нужно изменить."""
    body: dict = {"id": id}
    if title:
        body["title"] = title
    if content:
        body["content"] = content
    if category:
        body["category"] = category
    if tags:
        body["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
    body["pinned"] = pinned
    return await _put("/api/knowledge", body)


@mcp.tool()
async def knowledge_delete(id: str) -> str:
    """Удалить запись из базы знаний по id."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.delete(f"{BASE_URL}/api/knowledge", headers=HEADERS, params={"id": id})
        return resp.text


@mcp.tool()
async def knowledge_get(id: str) -> str:
    """Получить полную запись базы знаний по id (с полным контентом)."""
    # Получаем все и фильтруем — API не поддерживает GET by id
    result = await _get("/api/knowledge")
    import json as _json
    try:
        data = _json.loads(result)
        if data.get("ok") and data.get("data"):
            entry = next((e for e in data["data"] if e["id"] == id), None)
            if entry:
                return _json.dumps({"ok": True, "data": entry}, ensure_ascii=False)
            return _json.dumps({"ok": False, "error": "Entry not found"})
    except Exception:
        pass
    return result


# ============================================================
# АКТИВНОСТЬ
# ============================================================

@mcp.tool()
async def add_activity(
    date: str,
    activity_type: str,
    duration_min: int,
    intensity: str = "medium",
    calories: int = 0,
    notes: str = "",
) -> str:
    """Добавить активность. date: YYYY-MM-DD, activity_type: бег/ходьба/тренажёрка/плавание/йога/другое, duration_min: минуты, intensity: low/medium/high, calories: опционально."""
    body: dict = {"date": date, "activity_type": activity_type, "duration_min": duration_min, "intensity": intensity}
    if calories > 0:
        body["calories"] = calories
    if notes:
        body["notes"] = notes
    return await _post("/api/activity", body)


@mcp.tool()
async def delete_activity(id: str, date: str) -> str:
    """Удалить запись активности. id: ID записи, date: YYYY-MM-DD."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.delete(f"{BASE_URL}/api/activity", headers=HEADERS, params={"id": id, "date": date})
        return resp.text


# ============================================================
# ДОСКИ (BOARDS)
# ============================================================

@mcp.tool()
async def boards_list() -> str:
    """Получить список всех досок с их статусами и настройками полей."""
    return await _get("/api/boards")


@mcp.tool()
async def boards_get_items(board_id: str, status: str = "") -> str:
    """Получить элементы доски. board_id: ID доски, status: фильтр по статусу (опционально)."""
    params: dict = {"board_id": board_id}
    if status:
        params["status"] = status
    return await _get("/api/boards/items", params)


@mcp.tool()
async def boards_create_item(
    board_id: str,
    title: str,
    status: str = "",
    description: str = "",
    extra_fields: str = "",
) -> str:
    """Создать элемент доски. board_id: ID доски, title: название, status: статус (по умолчанию первый), extra_fields: JSON строка с дополнительными полями (priority, amount, deadline, comment, assignee)."""
    body: dict = {"board_id": board_id, "title": title}
    if status:
        body["status"] = status
    if description:
        body["description"] = description
    if extra_fields:
        body["extra_fields"] = json.loads(extra_fields)
    return await _post("/api/boards/items", body)


@mcp.tool()
async def boards_update_item(
    id: str,
    title: str = "",
    status: str = "",
    description: str = "",
    extra_fields: str = "",
) -> str:
    """Обновить элемент доски по id. Передай только поля которые нужно изменить. extra_fields: JSON строка."""
    body: dict = {"id": id}
    if title:
        body["title"] = title
    if status:
        body["status"] = status
    if description:
        body["description"] = description
    if extra_fields:
        body["extra_fields"] = json.loads(extra_fields)
    return await _put("/api/boards/items", body)


@mcp.tool()
async def boards_delete_item(id: str) -> str:
    """Удалить элемент доски по id."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.delete(f"{BASE_URL}/api/boards/items", headers=HEADERS, params={"id": id})
        return resp.text


@mcp.tool()
async def boards_urgent_items() -> str:
    """Получить срочные элементы из всех досок + срочные задачи для WorkScreen."""
    return await _get("/api/boards/urgent-items")


# ============================================================
# ЦЕЛИ (GOALS)
# ============================================================

@mcp.tool()
async def goals_list() -> str:
    """Получить все цели пользователя."""
    return await _get("/api/goals")


@mcp.tool()
async def goals_create(
    title: str,
    target_value: float,
    frequency: str = "daily",
    metric_type: str = "count",
    deadline: str = "",
) -> str:
    """Создать цель. title: название, target_value: целевое значение, frequency: daily/weekly/monthly, metric_type: count/percent/minutes, deadline: YYYY-MM-DD."""
    body: dict = {"title": title, "target_value": target_value, "frequency": frequency, "metric_type": metric_type}
    if deadline:
        body["deadline"] = deadline
    return await _post("/api/goals", body)


@mcp.tool()
async def goals_update(id: str, current_value: float = -1, status: str = "", title: str = "") -> str:
    """Обновить цель. current_value: текущее значение, status: active/completed/paused."""
    body: dict = {"id": id}
    if current_value >= 0:
        body["current_value"] = current_value
    if status:
        body["status"] = status
    if title:
        body["title"] = title
    return await _put("/api/goals", body)


# ============================================================
# КАЙДЗЕН
# ============================================================

@mcp.tool()
async def kaizen_get(date: str = "") -> str:
    """Получить записи Кайдзен за дату (утро/вечер/суббота). date: YYYY-MM-DD."""
    params = {}
    if date:
        params["date"] = date
    return await _get("/api/kaizen", params or None)


@mcp.tool()
async def kaizen_create(
    date: str,
    entry_type: str,
    focus: str = "",
    focus_done: bool = False,
    loss_area: str = "",
    kaizen_action: str = "",
    yesterday_kaizen_done: bool = False,
) -> str:
    """Создать запись Кайдзен. date: YYYY-MM-DD, entry_type: morning/evening/saturday. focus: фокус дня (утро), loss_area: область потери (вечер), kaizen_action: действие (вечер)."""
    body: dict = {"date": date, "type": entry_type}
    if focus:
        body["focus"] = focus
    body["focus_done"] = focus_done
    if loss_area:
        body["loss_area"] = loss_area
    if kaizen_action:
        body["kaizen_action"] = kaizen_action
    body["yesterday_kaizen_done"] = yesterday_kaizen_done
    return await _post("/api/kaizen", body)


# ============================================================
# ЖУРНАЛ
# ============================================================

@mcp.tool()
async def journal_list(date: str = "") -> str:
    """Получить записи журнала за дату. date: YYYY-MM-DD."""
    params = {}
    if date:
        params["date"] = date
    return await _get("/api/journal", params or None)


@mcp.tool()
async def journal_create(date: str, content: str, entry_type: str = "reflection") -> str:
    """Создать запись в журнале. date: YYYY-MM-DD, entry_type: reflection/gratitude/idea/note, content: текст."""
    return await _post("/api/journal", {"date": date, "type": entry_type, "content": content})


# ============================================================
# НАСТРОЕНИЕ
# ============================================================

@mcp.tool()
async def mood_get(date: str = "") -> str:
    """Получить записи настроения за дату. date: YYYY-MM-DD."""
    params = {}
    if date:
        params["date"] = date
    return await _get("/api/mood", params or None)


@mcp.tool()
async def mood_create(date: str, score: int, time_of_day: str = "morning", notes: str = "") -> str:
    """Записать настроение. date: YYYY-MM-DD, score: 1-5, time_of_day: morning/evening, notes: заметка."""
    body: dict = {"date": date, "score": score, "time_of_day": time_of_day}
    if notes:
        body["notes"] = notes
    return await _post("/api/mood", body)


# ============================================================
# ISSUES
# ============================================================

@mcp.tool()
async def issues_list(status: str = "open") -> str:
    """Получить список issues (баги, фичи). status: open/resolved/all."""
    params = {}
    if status and status != "all":
        params["status"] = status
    return await _get("/api/issues", params or None)


@mcp.tool()
async def issues_create(title: str, category: str = "bug", priority: str = "medium", description: str = "") -> str:
    """Создать issue. category: bug/feature/improvement, priority: low/medium/high."""
    body: dict = {"title": title, "category": category, "priority": priority}
    if description:
        body["description"] = description
    return await _post("/api/issues", body)


# ============================================================
# WHOOP
# ============================================================

@mcp.tool()
async def whoop_sync(date: str = "") -> str:
    """Синхронизировать данные Whoop за дату. date: YYYY-MM-DD (по умолчанию сегодня)."""
    params = {}
    if date:
        params["date"] = date
    return await _get("/api/whoop/sync", params or None)


@mcp.tool()
async def whoop_trends(days: int = 7) -> str:
    """Тренды Whoop за N дней: HRV, пульс покоя, strain, качество сна. days: 1-30."""
    return await _get("/api/whoop/trends", {"days": str(days)})


# ============================================================
# ЧЕКИН
# ============================================================

@mcp.tool()
async def checkin_get(date: str = "") -> str:
    """Получить чекин за дату. date: YYYY-MM-DD."""
    params = {}
    if date:
        params["date"] = date
    return await _get("/api/checkin", params or None)


@mcp.tool()
async def checkin_create(date: str, answers: str) -> str:
    """Создать чекин. date: YYYY-MM-DD, answers: JSON строка с ответами."""
    return await _post("/api/checkin", {"date": date, "answers": json.loads(answers)})


# ============================================================
# XP
# ============================================================

@mcp.tool()
async def get_xp(date: str = "") -> str:
    """Получить XP breakdown за дату. date: YYYY-MM-DD."""
    params = {}
    if date:
        params["date"] = date
    return await _get("/api/xp", params or None)


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
