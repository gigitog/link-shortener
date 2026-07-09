"""Юнит-тесты app.metrics.route_label — метка path для метрик."""

from app.metrics import route_label


class _FakeRoute:
    def __init__(self, path: str):
        self.path = path


class _FakeRequest:
    def __init__(self, scope: dict):
        self.scope = scope


class TestRouteLabel:
    def test_returns_route_template_when_matched(self):
        request = _FakeRequest({"route": _FakeRoute("/links/{short_code}")})
        assert route_label(request) == "/links/{short_code}"

    def test_returns_placeholder_when_no_route_matched(self):
        """404 на уровне роутинга (ни один маршрут не подошёл) — фиксированная метка,
        а не сырой путь, иначе кардинальность метрик росла бы от мусорных запросов.
        """
        request = _FakeRequest({})
        assert route_label(request) == "unmatched"
