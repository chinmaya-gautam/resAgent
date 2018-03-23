import platform
import os


CURRENT_PLATFORM = platform.system().lower()


def ping(host):
    """Ping a host, return True if succeed."""

    # figure out the current running platform and adjust
    # parameter to ping command.
    if CURRENT_PLATFORM == "windows":
        ping_str = "ping -n 1 -w 2000 " + host
    else:
        ping_str = "ping -c 1 -t 1 " + host

    return os.system(ping_str) == 0
