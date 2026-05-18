import json
import unittest
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1"
SERVICE_PORTS = {
    "api-gateway": 8000,
    "listing-service": 8001,
    "advantage-engine": 8002,
    "logistics-service": 8003,
    "user-service": 8005,
    "verification-service": 8006,
    "payment-service": 8007,
}


class HealthEndpointTests(unittest.TestCase):
    def assert_healthy(self, service_name: str):
        port = SERVICE_PORTS[service_name]
        url = f"{BASE_URL}:{port}/health"

        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                self.assertEqual(response.status, 200, f"{service_name} returned {response.status}")
                payload = json.load(response)
        except urllib.error.URLError as exc:
            self.fail(f"Unable to reach {service_name} at {url}: {exc}")

        self.assertEqual(
            payload.get("status"),
            "healthy",
            f"{service_name} health response did not contain status=healthy: {payload}",
        )

    def test_api_gateway_health(self):
        self.assert_healthy("api-gateway")

    def test_listing_service_health(self):
        self.assert_healthy("listing-service")

    def test_advantage_engine_health(self):
        self.assert_healthy("advantage-engine")

    def test_logistics_service_health(self):
        self.assert_healthy("logistics-service")

    def test_user_service_health(self):
        self.assert_healthy("user-service")

    def test_verification_service_health(self):
        self.assert_healthy("verification-service")

    def test_payment_service_health(self):
        self.assert_healthy("payment-service")


if __name__ == "__main__":
    unittest.main()
