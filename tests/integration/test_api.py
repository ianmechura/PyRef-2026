from fastapi.testclient import TestClient

from taskflow_ref.api.main import create_app
from taskflow_ref.infrastructure.settings import Settings


def test_api_create_list_complete_task(tmp_path) -> None:
    app = create_app(Settings(data_file=tmp_path / "tasks.json"))
    client = TestClient(app)

    create_response = client.post("/tasks", json={"title": "Calibrate probe", "priority": "high"})
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    complete_response = client.post(f"/tasks/{task_id}/complete")
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "completed"
