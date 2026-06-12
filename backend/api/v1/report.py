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
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD，默认今天"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD，默认等于开始日期"),
    interval: int = Query(30, ge=1, description="时间间隔(分钟): 10/30/60/360/1440"),
    db: AsyncSession = Depends(get_db),
):
    """获取指定日期范围内的当前人数趋势数据（支持跨天）"""
    config = await get_activity_config(db)
    max_people = config.max_people or 500

    now = datetime.now()
    if not start_date:
        start_date = now.strftime("%Y-%m-%d")
    if not end_date:
        end_date = start_date

    # 解析日期范围（每天 00:00:00 起始）
    start_dt = datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(f"{end_date} 23:59:59", "%Y-%m-%d %H:%M:%S")
    # 今天截止到当前时刻，历史日期截止到当天结束
    query_end = min(now, end_dt) if now.date() <= end_dt.date() else end_dt

    # 查询范围内所有日志
    result = await db.execute(
        select(PeopleLog)
        .where(PeopleLog.created_at >= start_dt, PeopleLog.created_at <= end_dt)
        .order_by(PeopleLog.created_at)
    )
    logs = result.scalars().all()

    # 基线：start_date 之前的所有日志净增
    history_result = await db.execute(
        select(
            func.coalesce(func.sum(
                case(
                    (PeopleLog.operation_type == "entry", PeopleLog.count),
                    else_=-PeopleLog.count
                )
            ), 0)
        ).where(PeopleLog.created_at < start_dt)
    )
    base_count = int(history_result.scalar() or 0)

    trend = []

    # 按天和按 6h 间隔：展示每日峰值人数（而非午夜 0 点数据）
    if interval >= 360:
        # 按天聚合，计算每日峰值
        daily_peak = {}  # { "06/08": peak_count }
        daily_remaining = {}  # { "06/08": remaining }
        current_people = base_count

        for log in logs:
            log_day = log.created_at.strftime("%m/%d")
            if log.operation_type == OperationType.ENTRY:
                current_people += log.count
            else:
                current_people -= log.count

            prev_peak = daily_peak.get(log_day, 0)
            if current_people > prev_peak:
                daily_peak[log_day] = current_people
                daily_remaining[log_day] = max(0, max_people - current_people)

        for day_label, peak in daily_peak.items():
            trend.append({
                "time": day_label,
                "currentPeople": max(0, peak),
                "remainingCapacity": daily_remaining.get(day_label, max_people),
            })
    else:
        # 小间隔：时间点采样
        time_points = []
        current = start_dt
        while current <= query_end:
            time_points.append(current)
            current += timedelta(minutes=interval)

        current_people = base_count
        log_index = 0

        for tp_dt in time_points:
            while log_index < len(logs) and logs[log_index].created_at <= tp_dt:
                if logs[log_index].operation_type == OperationType.ENTRY:
                    current_people += logs[log_index].count
                else:
                    current_people -= logs[log_index].count
                log_index += 1

            days_span = (end_dt - start_dt).days
            if days_span >= 1:
                label = tp_dt.strftime("%m/%d %H:%M")
            else:
                label = tp_dt.strftime("%H:%M")

            trend.append({
                "time": label,
                "currentPeople": max(0, current_people),
                "remainingCapacity": max(0, max_people - current_people),
            })

    return {"time_points": trend}
