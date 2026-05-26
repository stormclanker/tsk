#!/usr/bin/env python3

import contextlib
import dataclasses
import argparse
import os
import shlex
import subprocess
import sys
from typing import Literal

COMMAND_DESCRIPTION = """
Notify the user when a process has completed.

This can either be used after a command or as a wrapper around a command. For example:
    tsk echo hi
will run `echo hi` in a shell and then notify you of its success or failure. However:
    echo hi && tsk -s || tsk -e
will notify you of the success or failure of the echo command once it completes.
    tsk $?
will notify you of the exit code of the last command. This is mostly useful for adding to a long-running command while it's running, but only works if the command doesn't read from stdin. Finally,
    tsk
will simply notify you when it runs, allowing you to know when the previous command exits.
"""

@dataclasses.dataclass(frozen=True)
class Notification:
    """A notification to send."""

    summary: str
    body: str
    icon: str = "dialog-information"
    urgency: Literal["low", "normal", "critical"] = "normal"
    expire_time: int = 5000

    def send(self) -> None:
        """Send this notification."""
        try:
            subprocess.run(
                ["notify-send", "--app-name=tsk", f"--urgency={self.urgency}", f"--icon={self.icon}", f"--expire-time={self.expire_time}", self.summary, self.body],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            print("\a")


def get_command(command_parts: list[str]) -> tuple[str, str]:
    """Get the command - first the command itself then the full command string."""
    if len(command_parts) == 1:
        command_string = command_parts[0]
        command = shlex.split(command_string)[0]
    else:
        command_string = shlex.join(command_parts)
        command = command_parts[0]
    return (command, command_string)

def main():
    parser = argparse.ArgumentParser(
        description=COMMAND_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-e", "--error",
        action="store_true",
        help="Notify an error and exit.",
    )
    group.add_argument(
        "-s", "--success",
        action="store_true",
        help="Notify success and exit.",
    )
    group.add_argument(
        "command",
        nargs="*",
        default=[],
    )
    args = parser.parse_args()

    exit_code = None
    if len(args.command) == 1:
        with contextlib.suppress(ValueError):
            exit_code = int(args.command[0])

    if exit_code is not None or not args.command:
        if args.success or exit_code == 0:
            Notification(
                "Success",
                "The command has completed successfully.",
            ).send()
        elif args.error or exit_code:
            Notification(
                "Failure",
                "The command has failed.",
                icon="dialog-error",
            ).send()
        else:
            Notification(
                "Completed",
                "The command has completed."
            ).send()
        print("\a", end="")
        return

    app, command = get_command(args.command)

    process = subprocess.run(
        [os.getenv("SHELL", "/bin/sh"), '-c', command],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        check=False,
    )
    if process.returncode == 0:
        notification = Notification(
            f"Success: {app}",
            f"Success running {command}",
            icon="dialog-information",
        )
    else:
        notification = Notification(
            f"Error: {app}",
            f"Exit code {process.returncode}",
            icon="dialog-error",
        )

    notification.send()

    sys.exit(process.returncode)


if __name__ == '__main__':
    main()
