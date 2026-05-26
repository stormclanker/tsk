from unittest.mock import patch

import pytest

from tsk import Notification


@pytest.mark.parametrize("urgency", ["low", "normal", "critical"])
def test_urgency_passed_to_notify_send(urgency):
    with patch("tsk.subprocess.run") as mock_run:
        Notification("Summary", "Body", urgency=urgency).send()
        args = mock_run.call_args[0][0]
        assert f"--urgency={urgency}" in args
