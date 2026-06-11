# -*- coding: utf-8 -*-
"""游客进场/出场 API 测试

测试游客登记接口的各种场景：
- 正常进场 / 人数超限 / 负数人数
- 正常出场 / 出场人数超过当前人数
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


# ==================== 辅助函数 ====================

def _create_visitor_test_client(mock_redis, mock_db, app):
    """为游客测试创建 TestClient，处理依赖覆盖和副作用 mock

    Args:
        mock_redis: Mock Redis 客户端
        mock_db: Mock 数据库会话
        app: FastAPI 应用实例

    Returns:
        TestClient 实例（需要在 with 语句中使用并在 finally 中清理）
    """
    from core.database import get_db
    from core.redis import get_redis

    async def override_get_db():
        yield mock_db

    async def override_get_redis():
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis


def _cleanup_client(app):
    """清理 TestClient 的依赖覆盖副作用"""
    from core.database import get_db
    from core.redis import get_redis
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_redis, None)


# ==================== 游客进场测试 ====================

class TestVisitorEntry:
    """游客进场 API 测试"""

    @pytest.fixture
    def mock_deps(self):
        """创建进场测试用的 Mock 数据库和 Redis

        Redis 模拟：
        - 当前人数 100（< MAX_PEOPLE=500，不触发人数上限）
        - 无频率限制
        - incrby 返回 105
        """
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=b"100")
        mock_redis.exists = AsyncMock(return_value=False)
        mock_redis.incrby = AsyncMock(return_value=105)
        mock_redis.setex = AsyncMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        return mock_redis, mock_db

    def test_entry_success(self, mock_deps):
        """测试正常进场登记：5人进场，期望返回当前人数105"""
        mock_redis, mock_db = mock_deps

        from main import app
        from api.v1.visitor import router as visitor_router

        # 确保 visitor 路由已注册
        self._ensure_visitor_router(app, visitor_router)

        _create_visitor_test_client(mock_redis, mock_db, app)

        # Mock 广播副作用
        dashboard_mock = {"current_people": 105, "max_people": 500}
        with patch('api.v1.visitor.get_dashboard_data', new=AsyncMock(return_value=dashboard_mock)):
            with patch('api.v1.visitor.manager.broadcast', new=AsyncMock()):
                # Mock lifespan 避免真实连接
                with patch('core.redis.get_redis', new=AsyncMock(return_value=mock_redis)):
                    with patch('core.redis.disconnect_redis', new=AsyncMock()):
                        with patch('core.database.disconnect_database', new=AsyncMock()):
                            with patch('core.init_db.init_database', new=AsyncMock()):
                                with TestClient(app) as client:
                                    response = client.post(
                                        "/api/v1/visitor/entry",
                                        json={"count": 5}
                                    )

        _cleanup_client(app)

        assert response.status_code == 200
        data = response.json()
        assert data["current_people"] == 105
        assert "登记成功" in data["message"]
        assert data["operation_type"] == "entry"

    def test_entry_exceed_limit(self, mock_deps):
        """测试游客数量超限：count=15 超过 MAX_VISITOR_COUNT=10，期望返回 400"""
        mock_redis, mock_db = mock_deps
        mock_redis.get = AsyncMock(return_value=b"100")

        from main import app
        from api.v1.visitor import router as visitor_router

        self._ensure_visitor_router(app, visitor_router)
        _create_visitor_test_client(mock_redis, mock_db, app)

        with patch('core.redis.get_redis', new=AsyncMock(return_value=mock_redis)):
            with patch('core.redis.disconnect_redis', new=AsyncMock()):
                with patch('core.database.disconnect_database', new=AsyncMock()):
                    with patch('core.init_db.init_database', new=AsyncMock()):
                        with TestClient(app) as client:
                            response = client.post(
                                "/api/v1/visitor/entry",
                                json={"count": 15}
                            )

        _cleanup_client(app)

        # count=15 > MAX_VISITOR_COUNT=10，visitor_service 抛出 ValueError
        # visitor.py 捕获 ValueError 后转为 HTTP 400
        assert response.status_code == 400

    def test_entry_capacity_full(self, mock_deps):
        """测试当前人数已达上限：当前人数500 >= MAX_PEOPLE=500，期望返回 403"""
        mock_redis, mock_db = mock_deps
        # 当前人数达到上限
        mock_redis.get = AsyncMock(return_value=b"500")

        from main import app
        from api.v1.visitor import router as visitor_router

        self._ensure_visitor_router(app, visitor_router)
        _create_visitor_test_client(mock_redis, mock_db, app)

        with patch('core.redis.get_redis', new=AsyncMock(return_value=mock_redis)):
            with patch('core.redis.disconnect_redis', new=AsyncMock()):
                with patch('core.database.disconnect_database', new=AsyncMock()):
                    with patch('core.init_db.init_database', new=AsyncMock()):
                        with TestClient(app) as client:
                            response = client.post(
                                "/api/v1/visitor/entry",
                                json={"count": 1}
                            )

        _cleanup_client(app)

        # CapacityFullError → HTTP 403
        assert response.status_code == 403

    def test_entry_negative_count(self, mock_deps):
        """测试负数人数：count=-1，Pydantic 校验失败，期望返回 422"""
        mock_redis, mock_db = mock_deps

        from main import app
        from api.v1.visitor import router as visitor_router

        self._ensure_visitor_router(app, visitor_router)
        _create_visitor_test_client(mock_redis, mock_db, app)

        with patch('core.redis.get_redis', new=AsyncMock(return_value=mock_redis)):
            with patch('core.redis.disconnect_redis', new=AsyncMock()):
                with patch('core.database.disconnect_database', new=AsyncMock()):
                    with patch('core.init_db.init_database', new=AsyncMock()):
                        with TestClient(app) as client:
                            response = client.post(
                                "/api/v1/visitor/entry",
                                json={"count": -1}
                            )

        _cleanup_client(app)

        # count < 1，Pydantic Field(ge=1) 验证失败
        assert response.status_code == 422

    def test_entry_zero_count(self, mock_deps):
        """测试0人数：count=0，Pydantic 校验失败，期望返回 422"""
        mock_redis, mock_db = mock_deps

        from main import app
        from api.v1.visitor import router as visitor_router

        self._ensure_visitor_router(app, visitor_router)
        _create_visitor_test_client(mock_redis, mock_db, app)

        with patch('core.redis.get_redis', new=AsyncMock(return_value=mock_redis)):
            with patch('core.redis.disconnect_redis', new=AsyncMock()):
                with patch('core.database.disconnect_database', new=AsyncMock()):
                    with patch('core.init_db.init_database', new=AsyncMock()):
                        with TestClient(app) as client:
                            response = client.post(
                                "/api/v1/visitor/entry",
                                json={"count": 0}
                            )

        _cleanup_client(app)

        # count < 1，Pydantic Field(ge=1) 验证失败
        assert response.status_code == 422

    @staticmethod
    def _ensure_visitor_router(app, visitor_router):
        """确保 visitor 路由已注册到 app 中"""
        existing_paths = [route.path for route in app.routes]
        if not any("visitor" in p for p in existing_paths):
            app.include_router(visitor_router, prefix="/api/v1")


# ==================== 游客出场测试 ====================

class TestVisitorExit:
    """游客出场 API 测试"""

    @pytest.fixture
    def mock_deps(self):
        """创建出场测试用的 Mock 数据库和 Redis

        Redis 模拟：
        - 当前人数 100（足够出场 5 人）
        - 无频率限制
        - decrby 返回 95
        """
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=b"100")
        mock_redis.exists = AsyncMock(return_value=False)
        mock_redis.decrby = AsyncMock(return_value=95)
        mock_redis.incrby = AsyncMock(return_value=10)
        mock_redis.setex = AsyncMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        return mock_redis, mock_db

    def test_exit_success(self, mock_deps):
        """测试正常出场登记：5人出场，期望返回当前人数95"""
        mock_redis, mock_db = mock_deps

        from main import app
        from api.v1.visitor import router as visitor_router

        self._ensure_visitor_router(app, visitor_router)
        _create_visitor_test_client(mock_redis, mock_db, app)

        dashboard_mock = {"current_people": 95, "max_people": 500}
        with patch('api.v1.visitor.get_dashboard_data', new=AsyncMock(return_value=dashboard_mock)):
            with patch('api.v1.visitor.manager.broadcast', new=AsyncMock()):
                with patch('core.redis.get_redis', new=AsyncMock(return_value=mock_redis)):
                    with patch('core.redis.disconnect_redis', new=AsyncMock()):
                        with patch('core.database.disconnect_database', new=AsyncMock()):
                            with patch('core.init_db.init_database', new=AsyncMock()):
                                with TestClient(app) as client:
                                    response = client.post(
                                        "/api/v1/visitor/exit",
                                        json={"count": 5}
                                    )

        _cleanup_client(app)

        assert response.status_code == 200
        data = response.json()
        assert data["current_people"] == 95
        assert "登记成功" in data["message"]
        assert data["operation_type"] == "exit"

    def test_exit_exceed_current(self, mock_deps):
        """测试出场人数超过当前人数：当前3人、出场5人，期望返回 400"""
        mock_redis, mock_db = mock_deps
        # 当前只有 3 人
        mock_redis.get = AsyncMock(return_value=b"3")

        from main import app
        from api.v1.visitor import router as visitor_router

        self._ensure_visitor_router(app, visitor_router)
        _create_visitor_test_client(mock_redis, mock_db, app)

        with patch('core.redis.get_redis', new=AsyncMock(return_value=mock_redis)):
            with patch('core.redis.disconnect_redis', new=AsyncMock()):
                with patch('core.database.disconnect_database', new=AsyncMock()):
                    with patch('core.init_db.init_database', new=AsyncMock()):
                        with TestClient(app) as client:
                            response = client.post(
                                "/api/v1/visitor/exit",
                                json={"count": 5}
                            )

        _cleanup_client(app)

        # InsufficientPeopleError → HTTP 400
        assert response.status_code == 400

    @staticmethod
    def _ensure_visitor_router(app, visitor_router):
        """确保 visitor 路由已注册到 app 中"""
        existing_paths = [route.path for route in app.routes]
        if not any("visitor" in p for p in existing_paths):
            app.include_router(visitor_router, prefix="/api/v1")
