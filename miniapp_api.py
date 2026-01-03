from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from loader import week_lectures, year_lectures, db
from utils.utilities import type_format

app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/app", response_class=HTMLResponse)
async def miniapp():
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    return FileResponse("static/index.html", headers={"Cache-Control": "public, max-age=3600"})


@app.get("/api/week")
def get_week(user_id: int = Query(...)):
    group = db.get_group(user_id)
    result = {}

    if not group:
        raise HTTPException(status_code=404, detail="User group not found")

    # Используем year_lectures вместо week_lectures
    if group not in year_lectures:
        return result

    days = year_lectures[group]
    for date_str, lectures in days.items():
        if not lectures:
            continue

        day_name = lectures[0]  # Например, "Середа"

        # Структура: [Дата, День недели, {Лекция1}, {Лекция2}, ...]
        result[date_str] = [date_str, day_name]

        for lec in lectures[1:]:
            formatted_info = []
            for item in lec.info:
                subject = item[0]
                short_type = item[1]
                full_type = type_format(short_type)
                formatted_info.append([subject, short_type, full_type])

            # Исправляем формат времени (добавляем ведущие нули)
            try:
                start_t = f"{int(lec.start_hours):02}:{int(lec.start_minutes):02}"
                end_t = f"{int(lec.end_hours):02}:{int(lec.end_minutes):02}"
            except (ValueError, TypeError):
                # Если уже строки или другой формат
                start_t = lec.startTime()
                end_t = lec.endTime()

            result[date_str].append({
                "start": start_t,
                "end": end_t,
                "info": formatted_info
            })
    return result