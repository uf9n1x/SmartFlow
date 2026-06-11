# -*- coding: utf-8 -*-
"""工作人员 API 测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock


class TestStaffEntryAPI:
    """工作人员进场 API 测试"""

    @pytest.fixture
    def mocks(self):
        """创建 Mock Redis 和数据库"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=b"50")
        mock_redis.incrby = AsyncMock(return_value=55)
        mock_redis.setex = AsyncMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        return mock_redis, mock_db

    def _get_client(self, mock_redis, mock_db, with_token=True):
        """创建测试客户端"""
        from main import app
        from fastapi.testclient import TestClient
        from core.database import get_db
        from core.redis import get_redis

        async def override_get_db():
            yield mock_db

        async def override_get_redis():
            return mock_redis

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_redis] = override_get_redis

        client = TestClient(app)
        headers = {}
        if with_token:
            # 生成一个有效 JWT token
            from core.security import create_access_token
            token = create_access_token(data={"sub": "1", "role": "staff"})
            headers["Authorization"] = f"Bearer {token}"

        return client, headers, app

    def test_staff_entry_success(self, mocks):
        """测试工作人员正常进场登记"""
        mock_redis, mock_db = mocks
        client, headers, app = self._get_client(mock_redis, mock_db)

        response = client.post("/api/v1/staff/entry", json={"count": 5}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["current_people"] == 55
        assert "登记成功" in data["message"]
        app.dependency_overrides.clear()

    def test_staff_entry_no_token(self, mocks):
        """测试无 token 访问工作人员接口"""
        mock_redis, mock_db = mocks
        client, headers, app = self._get_client(mock_redis, mock_db, with_token=False)

        response = client.post("/api/v1/staff/entry", json={"count": 1})
        assert response.status_code == 403
        app.dependency_overrides.clear()

    def test_staff_entry_exceed_limit(self, mocks):
        """测试工作人员进场数量超限（超过50）"""
        mock_redis, mock_db = mocks
        client, headers, app = self._get_client(mock_redis, mock_db)

        response = client.post("/api/v1/staff/entry", json={"count": 100}, headers=headers)
        assert response.status_code == 400
        app.dependency_overrides.clear()


class TestStaffExitAPI:
    """工作人员出场 API 测试"""

    @pytest.fixture
    def mocks(self):
        """创建 Mock Redis 和数据库"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=b"50")
        mock_redis.decrby = AsyncMock(return_value=45)
        mock_redis.incrby = AsyncMock(return_value=10)
        mock_redis.setex = AsyncMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        return mock_redis, mock_db

    def _get_client(self, mock_redis, mock_db, with_token=True):
        """创建测试客户端"""
        from main import app
        from fastapi.testclient import TestClient
        from core.database import get_db
        from core.redis import get_redis

        async def override_get_db():
            yield mock_db

        async def override_get_redis():
            return mock_redis

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_redis] = override_get_redis

        client = TestClient(app)
        headers = {}
        if with_token:
            from core.security import create_access_token
            token = create_access_token(data={"sub": "1", "role": "staff"})
            headers["Authorization"] = f"Bearer {token}"

        return client, headers, app

    def test_staff_exit_success(self, mocks):
        """测试工作人员正常出场登记"""
        mock_redis, mock_db = mocks
        client, headers, app = self._get_client(mock_redis, mock_db)

        response = client.post("/api/v1/staff/exit", json={"count": 5}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["current_people"] == 45
        assert "登记成功" in data["message"]
        app.dependency_overrides.clear()

    def test_staff_exit_no_token(self, mocks):
        """测试无 token 访问工作人员出场接口"""
        mock_redis, mock_db = mocks
        client, headers, app = self._get_client(mock_redis, mock_db, with_token=False)

        response = client.post("/api/v1/staff/exit", json={"count": 1})
        assert response.status_code == 403
        app.dependency_overrides.clear()

    def test_staff_exit_exceed_current(self, mocks):
        """测试工作人员出场人数超过当前人数"""
        mock_redis, mock_db = mocks
        mock_redis.get = AsyncMock(return_value=b"3")
        client, headers, app = self._get_client(mock_redis, mock_db)

        response = client.post("/api/v1/staff/exit", json={"count": 10}, headers=headers)
        assert response.status_code == 400
        app.dependency_overrides.clear()
