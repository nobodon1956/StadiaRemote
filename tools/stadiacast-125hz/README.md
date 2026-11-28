# tools/stadiacast-125hz/

Enables **125 Hz (8 ms)** Wi-Fi input polling and restores **Capture / Assistant** button functionality on official `stadiacast 1.4.0` (and `1.2.0`, `stadiacast.exe`, Windows x86_64) without flashing or modifying controller firmware.

## Why this is needed

Stock `stadiacast` sends `DisplayToController #8` (`StartGame`) when the controller connects, but never sends `DisplayToController #4` (`focus_game`). As a result, retail firmware `316382` stays in `FOCUS_MENU` (`YetiMenuPollMs = 50 ms`, 20 Hz over the display link) instead of switching to `FOCUS_GAME` (`game_input` UDP stream at 125 Hz / 8 ms).

Additionally, in `FOCUS_GAME` mode the controller sends redundant unacknowledged history samples inside `InputMessageSeries` and omits unchanged axes/buttons in `GamepadMessage_V2`, while XInput lacks Capture/Assistant buttons. The wrapper in `launcher_125hz.py` fixes all of these:

1. Sends `DisplayToController #4` (`focus_game`) as an `RpcRequest` after `StartGame` succeeds (`code == 0`).
2. Deduplicates incoming `GamepadMessage_V2` events by `(session_id, gamepad_id, t_us)` to prevent burst replay and stick time-travel.
3. Uses `HasField()` on `GamepadMessage_V2` fields so unchanged axes/buttons carry forward from `GamepadTracker` instead of resetting to `0`.
4. Preserves 125 Hz game-session input on ViGEm while retaining the Stadia (Xbox Guide) button from the display link.
5. Restores extra buttons on Windows:
   - **Capture**: short press (< 0.6 s) triggers `Win + PrtScn` (screenshot); long press (≥ 0.6 s) triggers `Win + Alt + R` (Xbox Game Bar recording toggle).
   - **Assistant**: long press (≥ 0.6 s) toggles controller microphone on/off when `--mic-device` is active (or triggers `Win + H` when no mic sink is enabled).

## Usage (no Python required)

1. Make sure `stadiacast.exe` is stopped.
2. Run `patch-stadiacast.bat` (or `powershell -ExecutionPolicy Bypass -File patch-stadiacast.ps1`).
   - Automatically saves `stadiacast.exe.orig` on the first run.
   - Auto-detects `stadiacast\stadiacast-1.4.0-windows-x86_64\stadiacast.exe` (or falls back to `1.2.0`).
3. To revert to stock `stadiacast.exe` at any time:
   ```cmd
   powershell -NoProfile -ExecutionPolicy Bypass -File patch-stadiacast.ps1 -Restore
   ```

## Files

- `launcher_125hz.py` — Auditable Python source for the wrapper logic.
- `patch-stadiacast.ps1` — Zero-dependency PowerShell patcher containing the compiled Python 3.13 `launcher.py` bytecode payload (verified by SHA-256).
- `patch-stadiacast.bat` — One-click Windows wrapper for `patch-stadiacast.ps1`.
