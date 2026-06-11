"""报表导出 API"""
from datetime import datetime, timedelta
from urllib.parse import quote

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.people_log import PeopleLog, OperationType
from services.activity_service import get_activity_config
from services.report_service import export_to_csv, export_to_excel, generate_report_data

router = APIRouter(prefix="/report", tags=["报表"])


@router.get("/export")
async def export_report(
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD"),
    granularity: str = Query("day", description="统计粒度: day/week/month"),
    format: str = Query("xlsx", description="导出格式: xlsx/csv"),
    db: AsyncSession = Depends(get_db)
):
    """导出报表数据，支持 xlsx/csv 格式，按 day/week/month 粒度聚合"""
    # 生成报表数据
    data = await generate_report_data(db, start_date, end_date, granularity)

    # 按指定格式导出文件
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    if format == "csv":
        file = await export_to_csv(data)
        filename = f"report_{timestamp}.csv"
        media_type = "text/csv; charset=utf-8"
    else:
        file = await export_to_excel(data)
        filename = f"report_{timestamp}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return StreamingResponse(
        file,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"}
    )


@router.get("/trend")
async def get_trend_data(
    date: str = Query(None, description="日期 YYYY-MM-DD，默认今天"),
    interval: int = Query(30, ge=1, description="时间间隔(分钟): 10/30/60/360/1440"),
    db: AsyncSession = Depends(get_db),
):
    """获取当日每半小时当前人数趋势数据"""
    # 获取活动配置中的最大人数上限
    config = await get_activity_config(db)
    max_people = config.max_people or 500

    now = datetime.now()
    today_start = datetime.strptime(f"{date} 08:00:00", "%Y-%m-%d %H:%M:%S") if date else datetime.combine(now.date(), datetime.strptime("08:00:00", "%H:%M:%S").time())
    if not date:
        date = now.strftime("%Y-%m-%d")

    # 生成时间点列表（按指定间隔）
    time_points = []
    current = today_start
    while current <= now:
        time_points.append(current)
        current += timedelta(minutes=interval)

    # 查询当日所有日志
    day_end = datetime.strptime(f"{date} 23:59:59", "%Y-%m-%d %H:%M:%S")
    result = await db.execute(
        select(PeopleLog)
        .where(PeopleLog.created_at >= today_start, PeopleLog.created_at <= day_end)
        .order_by(PeopleLog.created_at)
    )
    logs = result.scalars().all()

    # 计算当日初始基线：截止昨天结束时的累计净增
    # 查询 TodayStart 之前的所有日志，计算净增作为趋势起点
    history_result = await db.execute(
        select(
            func.coalesce(func.sum(
                case(
                    (PeopleLog.operation_type == "entry", PeopleLog.count),
                    else_=-PeopleLog.count
                )
            ), 0)
        ).where(PeopleLog.created_at < today_start)
    )
    base_count = int(history_result.scalar() or 0)

    # 计算每个时间点的当前人数
    trend = []
    current_people = base_count
    log_index = 0

    for tp_dt in time_points:
        # 累计到该时间点的日志
        while log_index < len(logs) and logs[log_index].created_at <= tp_dt:
            if logs[log_index].operation_type == OperationType.ENTRY:
                current_people += logs[log_index].count
            else:
                current_people -= logs[log_index].count
            log_index += 1

        # 格式化显示标签：小间隔显示时间，大间隔显示日期+时间
        if interval >= 60:
            label = tp_dt.strftime("%m/%d %H:%M")
        else:
            label = tp_dt.strftime("%H:%M")

        trend.append({
            "time": label,
            "currentPeople": max(0, current_people),
            "remainingCapacity": max(0, max_people - current_people),
        })

    return {"time_points": trend}
