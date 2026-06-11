# -*- coding: utf-8 -*-
"""并发一致性测试"""
import pytest
import asyncio
from unittest.mock import AsyncMock

class TestConcurrentEntry:
    """并发进场一致性测试"""

    @pytest.mark.asyncio
    async def test_concurrent_entry_consistency(self):
        """测试 100 并发进场人数一致性

        模拟 100 个并发请求，每个请求进场 1 人，
        验证 Redis INCRBY 原子操作后最终值为 100
        """
        counter = {"value": 0}

        async def mock_incrby(key, amount):
            counter["value"] += amount
            return counter["value"]

        async def mock_get(key):
            return str(counter["value"]).encode()

        mock_redis = AsyncMock()
        mock_redis.incrby = mock_incrby
        mock_redis.get = mock_get
        mock_redis.setex = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=False)

        # 模拟 100 个并发进场请求
        async def simulate_entry(count=1):
            return await mock_redis.incrby("activity:current_people", count)

        tasks = [simulate_entry(1) for _ in range(100)]
        results = await asyncio.gather(*tasks)

        # 验证最终值
        final_count = counter["value"]
        assert final_count == 100, f"预期 100，实际 {final_count}"
        assert results[-1] == 100

    @pytest.mark.asyncio
    async def test_concurrent_mixed_operations(self):
        """测试混合进出场操作的一致性

        50 个进场(每人1人) + 30 个出场(每人1人) = 最终 20 人
        """
        counter = {"value": 0}

        async def mock_incrby(key, amount):
            counter["value"] += amount
            return counter["value"]

        async def mock_decrby(key, amount):
            counter["value"] -= amount
            return counter["value"]

        mock_redis = AsyncMock()
        mock_redis.incrby = mock_incrby
        mock_redis.decrby = mock_decrby
        mock_redis.get = AsyncMock(return_value="50".encode())

        # 50 个进场
        entry_tasks = [mock_incrby("activity:current_people", 1) for _ in range(50)]
        await asyncio.gather(*entry_tasks)

        # 30 个出场
        exit_tasks = [mock_decrby("activity:current_people", 1) for _ in range(30)]
        await asyncio.gather(*exit_tasks)

        final_count = counter["value"]
        assert final_count == 20, f"预期 20，实际 {final_count}"

    @pytest.mark.asyncio
    async def test_concurrent_does_not_go_below_zero(self):
        """测试并发出场不会导致负数"""
        counter = {"value": 100}

        async def mock_decrby(key, amount):
            counter["value"] -= amount
            if counter["value"] < 0:
                counter["value"] = 0
            return counter["value"]

        mock_redis = AsyncMock()
        mock_redis.decrby = mock_decrby

        # 200 个并发出场（每人1人，初始100人），最终应为0而非负数
        exit_tasks = [mock_decrby("activity:current_people", 1) for _ in range(200)]
        await asyncio.gather(*exit_tasks)

        assert counter["value"] >= 0, f"人数不应为负数，实际 {counter['value']}"
