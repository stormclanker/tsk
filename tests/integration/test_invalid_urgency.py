import os
import textwrap

import pytest

from tsk import Notification


@pytest.fixture
def fake_notify_send(tmp_path):
    """Create a fake notify-send that rejects invalid urgency values."""
    script = tmp_path / "notify-send"
    script.write_text(textwrap.dedent("""\
            #!/usr/bin/env bash
            for arg in "$@"; do
                if [[ "$arg" =~ ^--urgency= ]]; then
                    urgency="${arg#--urgency=}"
                    if [[ "$urgency" != "low" && "$urgency" != "normal" && "$urgency" != "critical" ]]; then
                        echo "Error: Invalid urgency '$urgency'" >&2
                        exit 1
                    fi
                fi
            done
            exit 0
            """))
    script.chmod(0o755)
    return tmp_path


def test_invalid_urgency_handled_gracefully(fake_notify_send, capsys, monkeypatch):
    """Test invalid urgency.

    When Notification.send() is called with an invalid urgency, notify-send
    rejects it. The program should handle the CalledProcessError gracefully
    (printing a bell) rather than raising an exception.
    """
    old_path = os.environ.get("PATH", "")
    monkeypatch.setenv("PATH", f"{fake_notify_send}:{old_path}")
    notif = Notification("Summary", "Body", urgency="invalid")
    notif.send()
    # The error handler prints a bell character to stdout
    captured = capsys.readouterr()
    assert "\x07" in captured.out
