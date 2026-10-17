import httpx
import pytest

pytestmark = pytest.mark.integration


def test_browser_http_available(settings):
    with httpx.Client(base_url=f"http://127.0.0.1:{settings.browser_port}", follow_redirects=True, timeout=10) as client:
        result = client.get("/")
        assert result.status_code == 200
        assert "FalkorDB" in result.text
