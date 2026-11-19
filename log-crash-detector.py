#!/usr/bin/env python3
# Scan all ArduPilot logs in a folder and flag possible crashes:
#   - a message (MSG / STATUSTEXT) containing "Crash"
#   - attitude |roll| or |pitch| greater than ATTITUDE_LIMIT_DEG
# Supports DataFlash logs (.bin, .log) and telemetry logs (.tlog).
# Usage: log-crash-detector.py <folder>

import math
import os
import sys
from pymavlink import mavutil

ATTITUDE_LIMIT_DEG = 45.0
CRASH_SUBSTRING = "Crash"
LOG_EXTENSIONS = (".bin", ".log", ".tlog")


def check_log(path):
    """Return a list of human-readable findings for one log file."""
    findings = []
    first_att = None  # first attitude exceedance, reported once
    max_roll = 0.0
    max_pitch = 0.0

    mlog = mavutil.mavlink_connection(path, robust_parsing=True)
    is_tlog = path.lower().endswith(".tlog")
    types = ["STATUSTEXT", "ATTITUDE"] if is_tlog else ["MSG", "ATT"]

    while True:
        try:
            m = mlog.recv_match(type=types)
        except Exception as e:
            findings.append(f"parse error: {e}")
            break
        if m is None:
            break

        mtype = m.get_type()
        t = getattr(m, "_timestamp", 0.0)

        if mtype in ("MSG", "STATUSTEXT"):
            text = m.Message if mtype == "MSG" else m.text
            if CRASH_SUBSTRING in text:
                findings.append(f"t={t:.1f} message: {text.strip()}")
            continue

        if mtype == "ATT":
            roll, pitch = m.Roll, m.Pitch  # degrees
        else:
            roll, pitch = math.degrees(m.roll), math.degrees(m.pitch)  # radians

        max_roll = max(max_roll, abs(roll))
        max_pitch = max(max_pitch, abs(pitch))
        if first_att is None and (abs(roll) > ATTITUDE_LIMIT_DEG or abs(pitch) > ATTITUDE_LIMIT_DEG):
            first_att = f"t={t:.1f} attitude: roll={roll:.1f} pitch={pitch:.1f} (first exceedance)"

    if first_att:
        findings.append(first_att)
        findings.append(f"max |roll|={max_roll:.1f} max |pitch|={max_pitch:.1f}")
    return findings


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {os.path.basename(sys.argv[0])} <folder>")
        sys.exit(1)

    folder = sys.argv[1]
    if not os.path.isdir(folder):
        print(f"Error: '{folder}' is not a directory")
        sys.exit(1)

    logs = sorted(f for f in os.listdir(folder) if f.lower().endswith(LOG_EXTENSIONS))
    if not logs:
        print(f"No log files found in '{folder}'")
        return

    flagged = 0
    for name in logs:
        findings = check_log(os.path.join(folder, name))
        if findings:
            flagged += 1
            print(f"[CRASH?] {name}")
            for f in findings:
                print(f"    {f}")
        else:
            print(f"[OK]     {name}")

    print(f"\n{flagged}/{len(logs)} log(s) flagged")


if __name__ == "__main__":
    main()
