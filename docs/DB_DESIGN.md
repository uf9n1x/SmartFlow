# 数据库设计文档

## ER 关系

```
users (用户表)
  |
  |---> people_logs (操作日志表) [operator_id]

activity_config (活动配置表) [单例配置，仅一条记录]
```

## 表结构

### users（用户表）

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INT | 用户ID | PRIMARY KEY, AUTO_INCREMENT |
| username | VARCHAR(50) | 用户名 | UNIQUE, NOT NULL, INDEX |
| password_hash | VARCHAR(255) | 密码哈希(bcrypt) | NOT NULL |
| role | ENUM('admin','staff') | 角色 | NOT NULL, DEFAULT 'staff' |
| status | ENUM('active','disabled') | 状态 | NOT NULL, DEFAULT 'active' |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | 更新时间 | ON UPDATE CURRENT_TIMESTAMP |

### activity_config（活动配置表）

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INT | 配置ID | PRIMARY KEY, AUTO_INCREMENT |
| activity_name | VARCHAR(100) | 活动名称 | DEFAULT '默认活动' |
| max_people | INT | 最大人数上限 | DEFAULT 500 |
| current_people | INT | 当前人数快照 | DEFAULT 0 |
| single_submit_limit | INT | 单次提交最大人数 | DEFAULT 10 |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | 更新时间 | ON UPDATE CURRENT_TIMESTAMP |

### people_logs（操作日志表）

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INT | 日志ID | PRIMARY KEY, AUTO_INCREMENT |
| operation_type | ENUM('entry','exit') | 操作类型 | NOT NULL |
| source_type | ENUM('visitor','staff') | 来源类型 | NOT NULL |
| operator_id | INT | 操作员ID | NULLABLE |
| count | INT | 人数 | NOT NULL |
| ip | VARCHAR(45) | 客户端IP | NULLABLE |
| user_agent | VARCHAR(500) | User-Agent | NULLABLE |
| created_at | DATETIME | 操作时间 | DEFAULT CURRENT_TIMESTAMP |

## Redis Key 设计

| Key | 类型 | 说明 | 操作 |
|-----|------|------|------|
| activity:current_people | String | 当前区域人数 | INCRBY / DECRBY |
| activity:today_entry | String | 今日进场累计 | INCRBY |
| activity:today_exit | String | 今日出场累计 | INCRBY |
| rate_limit:{ip} | String | IP限频标记 | SETEX（TTL=10s） |

## 核心业务规则

### 人数计算
```
current_people = total_entry_people - total_exit_people
限制：current_people >= 0
```

### 进场限制
```
IF current_people >= max_people THEN
    拒绝进场请求
    返回 "当前活动区域人数已达到最大上限，请您等待"
END IF
```

### 出场限制
```
IF current_people < request_count THEN
    拒绝出场请求
    返回 "出场人数超过当前在区域人数"
END IF
```

### 防作弊规则
```
游客：单次 1~10 人，同IP 10秒内仅允许一次
工作人员：单次 1~50 人，需JWT认证
```
