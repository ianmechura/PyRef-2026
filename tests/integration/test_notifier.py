import httpx
import respx

from taskflow_ref.domain.models import Task
from taskflow_ref.infrastructure.notifier import WebhookTaskNotifier


@respx.mock
def test_webhook_notifier_posts_task_created_event() -> None:
    route = respx.post("https://example.test/hooks/tasks").mock(
        return_value=httpx.Response(204)
    )
    notifier = WebhookTaskNotifier("https://example.test/hooks/tasks")

    notifier.task_created(Task.create("Notify me"))

    assert route.called
    payload = route.calls.last.request.content.decode("utf-8")
    assert "task.created" in payload
    assert "Notify me" in payload
