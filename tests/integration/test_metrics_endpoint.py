"""Интеграционные тесты /metrics: счётчик запросов, гистограмма задержки,
защита от взрыва кардинальности на несуществующих путях.
"""

from httpx import AsyncClient
from prometheus_client.parser import text_string_to_metric_families


def _sample_value(text: str, metric_name: str, **labels) -> float | None:
    """Находит значение конкретного сэмпла в prometheus-текстовом формате.

    Разбираем через text_string_to_metric_families — так же, как это делает
    настоящий Prometheus при scrape, а не руками ищем подстроки в тексте.
    """
    for family in text_string_to_metric_families(text):
        for sample in family.samples:
            if sample.name == metric_name and all(
                sample.labels.get(k) == v for k, v in labels.items()
            ):
                return sample.value
    return None


class TestMetricsEndpoint:
    async def test_content_type(self, client: AsyncClient):
        resp = await client.get("/metrics")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/plain")

    async def test_counter_increments_for_known_route(self, client: AsyncClient):
        before_text = (await client.get("/metrics")).text
        before = (
            _sample_value(
                before_text, "http_requests_total", method="GET", path="/health", status="200"
            )
            or 0
        )

        await client.get("/health")

        after_text = (await client.get("/metrics")).text
        after = _sample_value(
            after_text, "http_requests_total", method="GET", path="/health", status="200"
        )

        assert after == before + 1

    async def test_duration_histogram_recorded(self, client: AsyncClient):
        await client.get("/health")
        text = (await client.get("/metrics")).text

        count = _sample_value(
            text,
            "http_request_duration_seconds_count",
            method="GET",
            path="/health",
            status="200",
        )
        assert count is not None and count >= 1

    async def test_unmatched_route_does_not_leak_raw_path(self, client: AsyncClient):
        """Путь, не подходящий ни под один маршрут (несколько сегментов,
        которые не совпадают ни с /{short_code}, ни с /links/*, ни с /auth/*),
        должен лечь под метку "unmatched", а не под свой собственный сырой путь.
        """
        garbage_path = "/a/b/c/d/does-not-exist"
        resp = await client.get(garbage_path)
        assert resp.status_code == 404

        text = (await client.get("/metrics")).text

        assert (
            _sample_value(text, "http_requests_total", method="GET", path="unmatched", status="404")
            is not None
        )
        # Сырой мусорный путь НЕ должен появиться как отдельная метка
        assert garbage_path not in text
