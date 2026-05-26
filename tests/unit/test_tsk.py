from unittest.mock import patch

import pytest

from tsk import Notification


def test_urgency_passed_to_notify_send():
    with patch("tsk.subprocess.run") as mock_run:
        Notification("Summary", "Body", urgency="critical").send()
        args = mock_run.call_args[0][0]
        assert "--urgency=critical" in args


def test_default_urgency_is_normal():
    with patch("tsk.subprocess.run") as mock_run:
        Notification("Summary", "Body").send()
        args = mock_run.call_args[0][0]
        assert "--urgency=normal" in args


@pytest.mark.parametrize("urgency", ["low", "normal", "critical"])
def test_all_urgency_levels(urgency):
    with patch("tsk.subprocess.run") as mock_run:
        Notification("Summary", "Body", urgency=urgency).send()
        args = mock_run.call_args[0][0]
        assert f"--urgency={urgency}" in args
