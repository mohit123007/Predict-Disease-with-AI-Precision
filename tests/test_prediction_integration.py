from fastapi.testclient import TestClient
import backend.main as main

client = TestClient(main.app)


def test_image_endpoint_requires_auth():
    resp = client.post('/predict/image')
    assert resp.status_code in (401, 422)
