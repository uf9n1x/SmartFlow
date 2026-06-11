# API 接口文档

## 基础信息
- 基础路径：`/api/v1`
- 认证方式：Bearer Token（JWT），在 Header 中携带 `Authorization: Bearer <token>`
- 响应格式：JSON

**接口权限说明：**

| 接口 | 是否需要 JWT | 说明 |
|------|-------------|------|
| 游客进场/出场 | 否 | 公开接口，IP 限频 10 秒 |
| 工作人员进场/出场 | 是 | 需先登录获取 Token |
| Dashboard 数据 | 否 | 公开接口，任何人都可查看 |
| 活动配置查看 | 否 | 公开接口 |
| 活动配置修改 | 是（管理员） | 需管理员角色 |
| 日志查询 | 是（管理员） | 需管理员角色 |
| 报表导出 | 是（管理员） | 需管理员角色 |

## 接口列表

### 1. 游客进场
POST /api/v1/visitor/entry

请求体：
```json
{
  "count": 3
}
```

成功响应 200：
```json
{
  "message": "进场3人登记成功",
  "current_people": 103,
  "operation_type": "entry",
  "count": 3
}
```

错误 403（人数已满）：
```json
{ "detail": "当前活动区域人数已达到最大上限，请您等待" }
```

错误 429（频率限制）：
```json
{ "detail": "操作过于频繁，请稍后再试" }
```

错误 400（数量超限）：
```json
{ "detail": "单次人数范围为 1~10" }
```

### 2. 游客出场
POST /api/v1/visitor/exit

请求体：
```json
{ "count": 2 }
```

成功响应 200：
```json
{
  "message": "出场2人登记成功",
  "current_people": 98,
  "operation_type": "exit",
  "count": 2
}
```

错误 400（人数不足）：
```json
{ "detail": "出场人数(5)超过当前在区域人数(3)" }
```

### 3. 工作人员登录
POST /api/v1/auth/login

请求体：
```json
{
  "username": "admin",
  "password": "admin123"
}
```

成功响应 200：
```json
{
  "access_token": "eyJhbGciOiJI...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "admin",
  "role": "admin"
}
```

错误 401：
```json
{ "detail": "用户名或密码错误" }
```

### 4. 工作人员进场
POST /api/v1/staff/entry
Header: Authorization: Bearer `<token>`

请求体：
```json
{ "count": 5 }
```

成功响应 200：
```json
{
  "message": "进场5人登记成功",
  "current_people": 55,
  "operation_type": "entry",
  "count": 5
}
```

### 5. 工作人员出场
POST /api/v1/staff/exit
Header: Authorization: Bearer `<token>`

请求体：
```json
{ "count": 3 }
```

成功响应 200：
```json
{ "message": "出场3人登记成功", "current_people": 52, "operation_type": "exit", "count": 3 }
```

### 6. Dashboard 数据
GET /api/v1/dashboard

成功响应 200：
```json
{
  "current_people": 50,
  "max_people": 500,
  "remaining_capacity": 450,
  "usage_rate": 10.0,
  "today_entry": 120,
  "today_exit": 70,
  "total_entry": 1520,
  "total_exit": 1470,
  "is_full": false
}
```

### 7. 日志查询
GET /api/v1/logs?page=1&page_size=20&operation_type=entry&source_type=visitor&start_date=2026-06-01&end_date=2026-06-10

成功响应 200：
```json
{
  "items": [{
    "id": 1,
    "operation_type": "entry",
    "source_type": "visitor",
    "operator_id": null,
    "count": 3,
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "created_at": "2026-06-10T10:30:00"
  }],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### 8. 报表导出
GET /api/v1/report/export?granularity=day&format=xlsx&start_date=2026-06-01&end_date=2026-06-10

返回：文件下载（xlsx 或 csv 格式）

### 9. 活动配置查看
GET /api/v1/activity/config

成功响应 200：
```json
{
  "id": 1,
  "activity_name": "默认活动",
  "max_people": 500,
  "current_people": 50,
  "single_submit_limit": 10
}
```

### 10. 活动配置更新
PUT /api/v1/activity/config
Header: Authorization: Bearer `<token>`（需管理员）

请求体：
```json
{
  "max_people": 800,
  "single_submit_limit": 15
}
```

成功响应 200：
```json
{ "id": 1, "activity_name": "默认活动", "max_people": 800, "current_people": 50, "single_submit_limit": 15 }
```

错误 403：
```json
{ "detail": "需要管理员权限" }
```

### 11. WebSocket 实时推送

**手动部署 / 开发环境：**
```
ws://localhost:8000/api/v1/ws/dashboard
```

**Docker / Nginx 部署（通过 Nginx 反向代理 /ws/ 路径）：**
```
ws://你的域名/ws/dashboard            # HTTP
wss://你的域名/ws/dashboard           # HTTPS（推荐）
```

连接后自动推送 Dashboard 数据：
```json
{
  "current_people": 50,
  "max_people": 500,
  "remaining_capacity": 450,
  "usage_rate": 10.0,
  "today_entry": 120,
  "today_exit": 70,
  "total_entry": 1520,
  "total_exit": 1470,
  "is_full": false,
  "connection_count": 3
}
```

发送 `"ping"` 可收到 `"pong"` 心跳响应。
