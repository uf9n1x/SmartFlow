"""报表统计服务"""
import csv
import io
from datetime import datetime, timedelta
from typing import Optional

import openpyxl
from sqlalchemy import select, func, case, text
from sqlalchemy.ext.asyncio import AsyncSession

from models.people_log import PeopleLog


async def generate_report_data(
    db: AsyncSession,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    granularity: str = "day"
) -> list[dict]:
    """按指定粒度生成报表数据，返回按周期聚合的进场/出场/净增人数列表"""
    # 根据粒度选择时间分组函数
    if granularity == "day":
        group_by = func.date(PeopleLog.created_at)
    elif granularity == "week":
        group_by = func.date_format(PeopleLog.created_at, "%Y-W%u")
    elif granularity == "month":
        group_by = func.date_format(PeopleLog.created_at, "%Y-%m")
    else:
        group_by = func.date(PeopleLog.created_at)

    # 构建聚合查询：按周期分组，统计进场/出场/净增人数
    base_query = select(
        group_by.label("period"),
        func.sum(
            case(
                (PeopleLog.operation_type == "entry", PeopleLog.count),
                else_=0
            )
        ).label("entry_count"),
        func.sum(
            case(
                (PeopleLog.operation_type == "exit", PeopleLog.count),
                else_=0
            )
        ).label("exit_count"),
        func.sum(
            case(
                (PeopleLog.operation_type == "entry", PeopleLog.count),
                else_=-PeopleLog.count
            )
        ).label("net_count")
    ).group_by(group_by).order_by(group_by)

    # 时间范围筛选
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        base_query = base_query.where(PeopleLog.created_at >= start)
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d")
        end = end + timedelta(days=1)  # 包含结束日期当天
        base_query = base_query.where(PeopleLog.created_at < end)

    result = await db.execute(base_query)
    rows = result.all()

    data: list[dict] = []
    for row in rows:
        period_str = str(row.period) if row.period else ""
        data.append({
            "period": period_str,
            "entry_count": int(row.entry_count or 0),
            "exit_count": int(row.exit_count or 0),
            "net_count": int(row.net_count or 0)
        })
    return data


async def export_to_excel(data: list[dict]) -> io.BytesIO:
    """将报表数据导出为 Excel 格式的 BytesIO 流"""
    from openpyxl.styles import Alignment, Border, Font, Side

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "SmartFlow 客流统计报表"

    # 表头
    ws.append(["日期/周期", "进场人数", "出场人数", "净增人数"])

    # 数据行
    for item in data:
        ws.append([item["period"], item["entry_count"], item["exit_count"], item["net_count"]])

    # 表头样式
    header_font = Font(bold=True, size=12)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        cell.border = thin_border

    # 调整列宽
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


async def export_to_csv(data: list[dict]) -> io.BytesIO:
    """将报表数据导出为 CSV 格式的 BytesIO 流（UTF-8 BOM）"""
    output = io.StringIO()
    writer = csv.writer(output)

    # 表头
    writer.writerow(["日期/周期", "进场人数", "出场人数", "净增人数"])
    for item in data:
        writer.writerow([item["period"], item["entry_count"], item["exit_count"], item["net_count"]])

    # 转为 BytesIO，添加 BOM 以确保 Excel 正确识别中文编码
    bio = io.BytesIO()
    bio.write(output.getvalue().encode('utf-8-sig'))
    bio.seek(0)
    return bio
