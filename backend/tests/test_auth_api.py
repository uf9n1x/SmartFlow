# -*- coding: utf-8 -*-
"""认证 API 测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock

class TestAuthAPI:
    """登录 API 测试"""

    @pytest.fixture
    def mock_db_with_user(self):
        """Mock 数据库含管理员用户"""
        from models.user import User, UserRole, UserStatus
        from core.security import hash_password

        user = User(
            id=1,
            username="admin",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        return mock_db

    def test_login_success(self, mock_db_with_user):
        """测试登录成功"""
        from main import app
        from fastapi.testclient import TestClient
        from core.database import get_db
        from unittest.mock import patch

        async def override_get_db():
            yield mock_db_with_user

        app.dependency_overrides[get_db] = override_get_db

        # 模拟 lifespan 生命周期以规避真实 Redis/DB 连接
        with patch('core.redis.get_redis', new=AsyncMock()):
            with patch('core.redis.disconnect_redis', new=AsyncMock()):
                with patch('core.database.disconnect_database', new=AsyncMock()):
                    with patch('core.init_db.init_database', new=AsyncMock()):
                        with TestClient(app) as client:
                            response = client.post("/api/v1/auth/login", json={
                                "username": "admin",
                                "password": "admin123"
                            })

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "admin"

    def test_login_wrong_password(self, mock_db_with_user):
        """测试密码错误"""
        from main import app
        from fastapi.testclient import TestClient
        from core.database import get_db
        from unittest.mock import patch

        async def override_get_db():
            yield mock_db_with_user

        app.dependency_overrides[get_db] = override_get_db

        with patch('core.redis.get_redis', new=AsyncMock()):
            with patch('core.redis.disconnect_redis', new=AsyncMock()):
                with patch('core.database.disconnect_database', new=AsyncMock()):
                    with patch('core.init_db.init_database', new=AsyncMock()):
                        with TestClient(app) as client:
                            response = client.post("/api/v1/auth/login", json={
                                "username": "admin",
                                "password": "wrongpassword"
                            })

        app.dependency_overrides.clear()

        assert response.status_code == 401

    def test_protected_endpoint_no_token(self):
        """测试未认证访问受保护接口"""
        from main import app
        from fastapi.testclient import TestClient
        from unittest.mock import patch

        with patch('core.redis.get_redis', new=AsyncMock()):
            with patch('core.redis.disconnect_redis', new=AsyncMock()):
                with patch('core.database.disconnect_database', new=AsyncMock()):
                    with patch('core.init_db.init_database', new=AsyncMock()):
                        with TestClient(app) as client:
                            response = client.post("/api/v1/staff/entry", json={"count": 1})

        assert response.status_code == 403
