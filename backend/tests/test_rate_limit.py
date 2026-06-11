# -*- coding: utf-8 -*-
"""IP 限频测试"""
import pytest
import asyncio
from unittest.mock import AsyncMock

class TestRateLimit:
    """IP 限频测试"""

    def test_first_request_passes(self):
        """测试首次请求不触发限频"""
        from services.visitor_service import check_rate_limit

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=False)
        mock_redis.setex = AsyncMock()

        result = asyncio.run(check_rate_limit(mock_redis, "192.168.1.1"))
        assert result is True
        mock_redis.setex.assert_called_once()

    def test_repeated_request_blocked(self):
        """测试重复请求被限频"""
        from services.visitor_service import check_rate_limit

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=True)

        result = asyncio.run(check_rate_limit(mock_redis, "192.168.1.1"))
        assert result is False
        mock_redis.setex.assert_not_called()

    def test_different_ip_not_blocked(self):
        """测试不同 IP 互不影响"""
        from services.visitor_service import check_rate_limit

        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock()

        # 第一个 IP
        mock_redis.exists = AsyncMock(return_value=False)
        result1 = asyncio.run(check_rate_limit(mock_redis, "192.168.1.1"))
        assert result1 is True

        # 第二个 IP
        mock_redis.exists = AsyncMock(return_value=False)
        result2 = asyncio.run(check_rate_limit(mock_redis, "192.168.1.2"))
        assert result2 is True

    def test_rate_limit_uses_correct_key(self):
        """测试限频使用正确的 Redis Key"""
        from services.visitor_service import check_rate_limit

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=False)
        mock_redis.setex = AsyncMock()

        ip = "10.0.0.1"
        asyncio.run(check_rate_limit(mock_redis, ip))

        # 验证使用正确的 key
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == f"rate_limit:{ip}"
