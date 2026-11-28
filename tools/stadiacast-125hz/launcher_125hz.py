"""Patched entry point for stadiacast (1.2.0 / 1.4.0+) enabling 125 Hz Wi-Fi mode
and restoring Capture / Assistant button functionality on Windows.

Stock stadiacast sends DisplayToController #8 (StartGame) but never sends
DisplayToController #4 (focus_game), leaving the Stadia controller firmware in
FOCUS_MENU (YetiMenuPollMs = 50 ms / 20 Hz) over the display link instead of
switching to FOCUS_GAME (game session UDP input at 125 Hz / 8 ms).

This wrapper applies runtime patches before invoking stadiacast.cli.main():
1. Send DisplayToController #4 (focus_game) once StartGame succeeds (code == 0).
2. Deduplicate redundant historical events in InputMessageSeries by
   (session_id, gamepad_id, t_us) and reset tracking cleanly on session reset.
3. Preserve omitted sparse-delta fields in GamepadMessage_V2 via HasField(),
   preventing constant stick axes from snapping to 0 when only another axis moves.
4. While the 125 Hz game session is active, prevent display-link rpc_input
   reports from overwriting sticks/triggers/buttons on ViGEm while preserving
   the Stadia (Xbox Guide) button bit.
5. On Windows, restore Capture and Assistant buttons (which have no XInput bits):
   - Capture short press (< 0.6 s): Win + PrtScn (save screenshot)
   - Capture long press (>= 0.6 s): Win + Alt + R (toggle Game Bar recording)
   - Assistant: native Push-to-Talk in --mic ptt mode; Mic Mute/Unmute toggle
     when mic is configured in --mic on/off mode; Win + H (voice typing) when
     no mic output is enabled.
"""

import asyncio
import contextlib
import ctypes
from ctypes import wintypes
import dataclasses
import sys


# ---- Windows SendInput helper for Capture / Assistant hotkeys --------------------
_VK_LWIN = 0x5B
_VK_MENU = 0x12
_VK_SNAPSHOT = 0x2C
_VK_H = 0x48
_VK_R = 0x52
_EXTENDED_VKS = frozenset({_VK_LWIN, _VK_SNAPSHOT})


def _send_win_hotkey(*vks):
    """Send a simultaneous key chord (press all in order, release in reverse) on Windows."""
    if sys.platform != "win32" or not vks:
        return False

    class _MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.c_size_t),
        ]

    class _KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.c_size_t),
        ]

    class _HARDWAREINPUT(ctypes.Structure):
        _fields_ = [
            ("uMsg", wintypes.DWORD),
            ("wParamL", wintypes.WORD),
            ("wParamH", wintypes.WORD),
        ]

    class _INPUT_UNION(ctypes.Union):
        _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT), ("hi", _HARDWAREINPUT)]

    class _INPUT(ctypes.Structure):
        _fields_ = [("type", wintypes.DWORD), ("union", _INPUT_UNION)]

    user32 = ctypes.windll.user32
    sequence = [(vk, False) for vk in vks] + [(vk, True) for vk in reversed(vks)]
    arr = (_INPUT * len(sequence))()
    for i, (vk, is_up) in enumerate(sequence):
        flags = 0x0001 if vk in _EXTENDED_VKS else 0
        if is_up:
            flags |= 0x0002
        scan = user32.MapVirtualKeyW(vk, 0) & 0xFF
        arr[i].type = 1  # INPUT_KEYBOARD
        arr[i].union.ki = _KEYBDINPUT(wVk=vk, wScan=scan, dwFlags=flags, time=0, dwExtraInfo=0)
    sent = user32.SendInput(len(arr), arr, ctypes.sizeof(_INPUT))
    return sent == len(arr)


def _install_125hz_patch():
    import stadiacast.controller as _cs
    import stadiacast.game_session as _gs
    import stadiacast.gamepad as _gp
    import stadiacast.input_protocol as _ip
    import stadiacast.virtual_gamepad as _vg

    # 1. Request focus_game once StartGame succeeds (code == 0)
    _orig_start = _gs.GameSession.on_start_game_response

    def _on_start_game_response(self, ticket, rpc):
        _orig_start(self, ticket, rpc)
        if (rpc.get("code") or 0) == 0:
            msg = self.protos.DisplayToController()
            msg.focus_game.SetInParent()
            ft = self.ctl.send_rpc("request", msg, purpose="focus_game")
            self.log("game_focus_requested", key=self.state.get("key"), ticket=ft)

    _orig_gs_reset = _gs.GameSession.reset

    def _gs_reset(self):
        _orig_gs_reset(self)
        dedup = getattr(self.input, "_dedup_t_us", None)
        if dedup is not None:
            dedup.clear()

    _gs.GameSession.on_start_game_response = _on_start_game_response
    _gs.GameSession.reset = _gs_reset

    # 2 & 3. Deduplicate replayed history frames and preserve sparse-delta fields
    _orig_slim = _ip.InputDecoder._slim

    def _dedup_slim(self, slim, series):
        if slim.HasField("gamepad_message_v2"):
            key = (series.session_id, slim.gamepad_message_v2.id)
            t_us = series.base_timestamp_us + slim.relative_time_us
            seen = getattr(self, "_dedup_t_us", None)
            if seen is None:
                seen = {}
                self._dedup_t_us = seen
            prev_t = seen.get(key)
            if prev_t is not None and t_us <= prev_t:
                return None
            seen[key] = t_us
        return _orig_slim(self, slim, series)

    def _sparse_gamepad_v2(self, g, base):
        ev = dict(base)
        st = self.gamepads.setdefault(g.id, _ip.GamepadTracker())
        buttons = g.buttons if g.HasField("buttons") else st.buttons
        axes = {
            "lx": g.axis_left_x if g.HasField("axis_left_x") else st.lx,
            "ly": g.axis_left_y if g.HasField("axis_left_y") else st.ly,
            "rx": g.axis_right_x if g.HasField("axis_right_x") else st.rx,
            "ry": g.axis_right_y if g.HasField("axis_right_y") else st.ry,
            "lt": g.trigger_left if g.HasField("trigger_left") else st.lt,
            "rt": g.trigger_right if g.HasField("trigger_right") else st.rt,
        }
        ev.update(type="gamepad", version=2, id=g.id, buttons=f"0x{buttons:08x}")
        if g.HasField("device_presence"):
            ev["device_presence"] = g.device_presence
        if g.HasField("device_type"):
            ev["device_type"] = self.protos.enum_name(
                f"{_ip.PKG_STREAMING}.GamepadMessage_V2.Type", g.device_type
            )
        if g.HasField("registration_info"):
            ev["registration_info"] = self.protos.to_dict(g.registration_info)
        self._diff(st, buttons, axes, ev)
        return ev

    _ip.InputDecoder._slim = _dedup_slim
    _ip.InputDecoder._gamepad_v2 = _sparse_gamepad_v2

    # 4. Prevent rpc_input from clobbering active 125 Hz game session input on ViGEm
    _orig_vg_on_event = _vg.VirtualGamepads.on_event
    _orig_vg_release = _vg.VirtualGamepads.release
    _orig_vg_close = _vg.VirtualGamepads.close
    stadia_mask = int(_gp.Button.STADIA)

    def _merged_vg_on_event(self, ev):
        label = str(ev.get("controller") or "")
        if self.kind == "vigem" and not self._closed and label and label not in self._failed and "axes" in ev:
            game_states = getattr(self, "_last_game_states", None)
            if game_states is None:
                game_states = {}
                self._last_game_states = game_states
            stadia_map = getattr(self, "_stadia_held", None)
            if stadia_map is None:
                stadia_map = {}
                self._stadia_held = stadia_map
            if ev.get("via") == "game":
                gs = _gp.GamepadState.from_event(ev)
                game_states[label] = gs
                if stadia_map.get(label, False) and not (gs.buttons & stadia_mask):
                    ev = dict(ev)
                    ev["buttons"] = f"0x{(gs.buttons | stadia_mask):08x}"
            elif label in game_states:
                rpc_state = _gp.GamepadState.from_event(ev)
                stadia_held = bool(rpc_state.buttons & stadia_mask)
                stadia_map[label] = stadia_held
                gs = game_states[label]
                merged_btn = (gs.buttons & ~stadia_mask) | (stadia_mask if stadia_held else 0)
                merged = dataclasses.replace(gs, buttons=merged_btn)
                ev = {
                    "controller": label,
                    "buttons": merged.buttons,
                    "axes": {"lx": merged.lx, "ly": merged.ly, "rx": merged.rx, "ry": merged.ry},
                    "triggers": {"l": merged.l2, "r": merged.r2},
                }
        return _orig_vg_on_event(self, ev)

    def _merged_vg_release(self, label):
        getattr(self, "_last_game_states", {}).pop(label, None)
        getattr(self, "_stadia_held", {}).pop(label, None)
        return _orig_vg_release(self, label)

    def _merged_vg_close(self):
        getattr(self, "_last_game_states", {}).clear()
        getattr(self, "_stadia_held", {}).clear()
        return _orig_vg_close(self)

    _vg.VirtualGamepads.on_event = _merged_vg_on_event
    _vg.VirtualGamepads.release = _merged_vg_release
    _vg.VirtualGamepads.close = _merged_vg_close

    # 5. Restore Capture & Assistant buttons on Windows via ControllerToDisplay #3
    if sys.platform == "win32":
        _orig_on_input_rpc = _cs.ControllerSession._on_input_rpc
        _orig_cs_stop = _cs.ControllerSession.stop
        _orig_cs_reset_boot = _cs.ControllerSession.reset_boot_state
        cap_mask = int(_gp.Button.CAPTURE)
        ast_mask = int(_gp.Button.ASSISTANT)

        def _cancel_capture_timer(self):
            timer = getattr(self, "_capture_timer", None)
            if timer is not None:
                timer.cancel()
                self._capture_timer = None

        def _cancel_assistant_timer(self):
            timer = getattr(self, "_assistant_timer", None)
            if timer is not None:
                timer.cancel()
                self._assistant_timer = None

        def _on_capture_long_press(self):
            self._capture_timer = None
            self._capture_long_fired = True
            ok = _send_win_hotkey(_VK_LWIN, _VK_MENU, _VK_R)
            self.log("capture_button", action="record_toggle", hotkey="Win+Alt+R", ok=ok)

        def _on_assistant_long_press(self):
            self._assistant_timer = None
            self._assistant_long_fired = True
            has_mic_sink = bool(
                getattr(self, "mic_record", False)
                or (getattr(self, "rx", None) is not None and self.rx.mic_device is not None)
            )
            if has_mic_sink and hasattr(self, "mic_start") and hasattr(self, "mic_stop"):
                if getattr(self, "mic_on", False):
                    self.mic_stop(reason="assistant")
                else:
                    self.mic_start(reason="assistant")
                self.log("assistant_button", action="mic_toggle", trigger="long_press", on=bool(self.mic_on))
            else:
                ok = _send_win_hotkey(_VK_LWIN, _VK_H)
                self.log("assistant_button", action="voice_typing", hotkey="Win+H", ok=ok)

        def _handle_extra_buttons(self, state):
            cap_now = bool(state.buttons & cap_mask)
            cap_prev = getattr(self, "_capture_held", False)
            if cap_now and not cap_prev:
                self._capture_held = True
                self._capture_long_fired = False
                _cancel_capture_timer(self)
                with contextlib.suppress(RuntimeError):
                    self._capture_timer = asyncio.get_running_loop().call_later(
                        0.6, _on_capture_long_press, self
                    )
            elif not cap_now and cap_prev:
                self._capture_held = False
                _cancel_capture_timer(self)
                if not getattr(self, "_capture_long_fired", False):
                    ok = _send_win_hotkey(_VK_LWIN, _VK_SNAPSHOT)
                    self.log("capture_button", action="screenshot", hotkey="Win+PrtScn", ok=ok)

            ast_now = bool(state.buttons & ast_mask)
            ast_prev = getattr(self, "_assistant_held", False)
            if not getattr(self, "mic_ptt", False):
                if ast_now and not ast_prev:
                    self._assistant_held = True
                    self._assistant_long_fired = False
                    _cancel_assistant_timer(self)
                    with contextlib.suppress(RuntimeError):
                        self._assistant_timer = asyncio.get_running_loop().call_later(
                            0.6, _on_assistant_long_press, self
                        )
                elif not ast_now and ast_prev:
                    self._assistant_held = False
                    _cancel_assistant_timer(self)

        def _patched_on_input_rpc(self, m):
            _orig_on_input_rpc(self, m)
            state = _gp.GamepadState.from_message3(m)
            _handle_extra_buttons(self, state)

        def _patched_cs_stop(self):
            _cancel_capture_timer(self)
            _cancel_assistant_timer(self)
            self._capture_held = False
            self._assistant_held = False
            return _orig_cs_stop(self)

        def _patched_cs_reset_boot(self, reason="new offer"):
            _cancel_capture_timer(self)
            _cancel_assistant_timer(self)
            self._capture_held = False
            self._assistant_held = False
            return _orig_cs_reset_boot(self, reason)

        _cs.ControllerSession._on_input_rpc = _patched_on_input_rpc
        _cs.ControllerSession.stop = _patched_cs_stop
        _cs.ControllerSession.reset_boot_state = _patched_cs_reset_boot


if __name__ == "__main__":
    if len(sys.argv) <= 1 or sys.argv[1] != "--stadiacast-helper":
        _install_125hz_patch()
    from stadiacast.cli import main

    sys.exit(main())
