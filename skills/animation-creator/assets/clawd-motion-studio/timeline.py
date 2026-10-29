"""Single source of truth for layout (UI pixels) and every timed event.

Three readers: the HTML/canvas texture builder (via `python timeline.py --json`),
the Blender scene (imports this module), and the audio synth (imports this module).

Conventions
- Time t in seconds, 0.0 .. 12.0. Blender frame = round(t * 30) + 1, so frame 1 is
  t = 0.000 and frame 360 is t = 11.967.
- UI pixels: the workspace is 1280 x 720 CSS px (screenshot at 3x -> 3840 x 2160),
  origin top-left. `ui_to_m` maps to Blender metres: X right, Y away from camera,
  slab tops at Z = 0.
- Comp pixels: the composition is 1920 x 1080.
Pure Python, no numpy, so Blender's bundled interpreter can import it.
"""
import json
import math
import sys

FPS = 30
DURATION = 12.0
FRAMES = 360
BPM = 120
BEAT = 60.0 / BPM  # 0.5 s


def t2f(t):
    return int(round(t * FPS)) + 1


def f2t(frame):
    return (frame - 1) / FPS


# ---------------------------------------------------------------- layout (UI px)
UI_W, UI_H = 1280, 720
UI_SCALE = 3
M_PER_PX = 0.0025  # 1280 px -> 3.2 m workspace


def ui_to_m(u, v):
    return ((u - UI_W / 2) * M_PER_PX, (UI_H / 2 - v) * M_PER_PX)


# Panel slabs: name -> (x, y, w, h). Menu bar + toolbar form one slab ("topbar").
PANELS = {
    "topbar":   (0, 0, 1280, 52),
    "project":  (0, 52, 300, 358),
    "comp":     (300, 52, 570, 358),
    "info":     (870, 52, 410, 70),
    "preview":  (870, 122, 410, 90),
    "effects":  (870, 212, 410, 198),
    "timeline": (0, 410, 1280, 310),
}
MENUBAR = (0, 0, 1280, 22)
TOOLBAR = (0, 22, 1280, 30)
MENU_ITEMS = ["File", "Edit", "Composition", "Layer", "Effect", "Animation", "View", "Window", "Help"]

# Composition panel internals
COMP_TABS = (300, 52, 570, 20)      # "Composition  Main Comp  ≡   Layer (none)   Footage (none)"
COMP_SUBTAB = (300, 72, 570, 18)    # "Main Comp" pill
COMP_VIEW = (345, 98, 480, 270)     # the comp canvas (16:9) drawn per frame
COMP_BOTTOM = (300, 378, 570, 26)   # 50%  Full  icons  camera  timecode  Active Camera  1 View  +0.0
TC_COMP = (488, 382, 96, 18)        # small blue timecode in comp bottom bar
COMP_PX_TO_UI = COMP_VIEW[2] / 1920.0  # 0.25


def comp_to_ui(cx, cy):
    return (COMP_VIEW[0] + cx * COMP_PX_TO_UI, COMP_VIEW[1] + cy * COMP_PX_TO_UI)


COMP_CENTER_UI = comp_to_ui(960, 540)  # (585, 233)

# Toolbar keycaps: name -> centre (u, v). Each cap is CAP_W x CAP_H UI px.
CAP_W, CAP_H = 24, 22
PREVIEW_CAP_W, PREVIEW_CAP_H = 32, 22
TOOL_ORDER = ["Home", "Selection", "Hand", "Zoom", "Rotate", "Camera", "PanBehind",
              "Rectangle", "Pen", "Type", "Brush", "Clone", "Eraser", "Roto", "Puppet"]
TOOL_X0, TOOL_DX, TOOL_Y = 150, 28, 37
TOOLS = {name: (TOOL_X0 + i * TOOL_DX, TOOL_Y) for i, name in enumerate(TOOL_ORDER)}

# Info panel: R G B A / X Y readouts. Preview panel transport caps.
PREVIEW_HEADER_Y = 132
PREVIEW_BUTTONS = {name: (930 + i * 40, 162) for i, name in
                   enumerate(["First", "Prev", "Play", "Next", "Last"])}
PREVIEW_SHORTCUT_Y = 194   # "Shortcut  Spacebar"

# Effects & Presets: search "glow" and result tree rows (centre y)
EFFECTS_HEADER_Y = 222
EFFECTS_SEARCH = (880, 232, 390, 18)
EFFECTS_ROWS = [
    ("▾ Stylize", 264, 0),
    ("fx Glow", 282, 1),
    ("▾ Animation Presets", 300, 0),
    ("▾ Image - Special Effects", 318, 1),
    ("fx Glow - Neon.ffx", 336, 2),
    ("fx Glow Pulse.ffx", 354, 2),
]
GLOW_ROW = (880, 273, 390, 18)       # highlight rect for the selected "Glow" row
GLOW_CHIP_HOME = (958, 282)          # where the chip pops up
GLOW_LAND = (1012, 282)              # where Clawd lands on the Glow row

# Timeline panel
TL_TABS = (0, 410, 1280, 20)         # "Main Comp ×   Render Queue"
TC_TL = (12, 434, 130, 22)           # big blue timecode
TL_COLHEAD_Y = 466                   # "#  Layer Name  Mode  T TrkMat  Parent & Link"
TL_ROW_H = 20
TL_ROWS = [  # (label, kind, top y, track colour)
    ("1  T  MADE WITH CLAUDE", "layer", 476, "#d9534f"),
    ("Transform", "group", 496, None),
    ("Position", "prop", 514, None),
    ("Scale", "prop", 532, None),
    ("2  ★  Spark", "layer", 550, "#e6c229"),
    ("3  ★  Swoosh", "layer", 570, "#7fcfc0"),
    ("4  ▣  clawd.png", "layer", 590, "#a99be0"),
    ("5  ■  BG", "layer", 610, "#c9a77c"),
]
POSITION_ROW_Y = 523                 # centre of the Position row
RULER = (450, 434, 810, 22)          # ruler strip in the track area
TRACK_X0, TRACK_X1 = 450, 1260
COMP_DURATION = 10.0                 # ruler spans 0s .. 10s
PLAYHEAD_HEAD_Y = 445


def comp_t_to_u(ct):
    return TRACK_X0 + (TRACK_X1 - TRACK_X0) * ct / COMP_DURATION


# ---------------------------------------------------------------- heights (metres)
SLAB_THICK = 0.03
CAP_TOP_Z = 0.012        # toolbar / preview keycap top above slab top
CAP_PRESS = 0.007        # press depth
PLAYHEAD_TOP_Z = 0.030   # top of the 3D playhead head
KEY_GEM_TOP_Z = 0.016
COMP_GLASS_Z = 0.002

# ---------------------------------------------------------------- mascot (HERO)
BODY_UNITS = (12.0, 8.0, 6.0)        # width x height x depth units (prompt)
UNIT_M = 0.0117                      # body is 0.14 m wide = 56 UI px
BODY_W, BODY_H, BODY_D = (u * UNIT_M for u in BODY_UNITS)
LEG_H = 1.6 * UNIT_M                 # legs below the body
TERRACOTTA_HEX = "#D97757"
BODY_BASE_RGB = (0.5, 0.085, 0.03)  # follow-up 2

# ---------------------------------------------------------------- comp content
TITLE = "MADE WITH CLAUDE"           # 16 characters -> 16 key taps
SUBTITLE = "OPUS 5.5"
SUBTITLE_PX = 78                     # follow-up 1
SPARK_RAYS = 12
SPARK_RAY_WIDTH_PX = 16              # follow-up 1: twice as wide as the hairline version
KEY_TIMES = [1.0, 2.5, 4.0, 5.5]     # comp-time of the four Position keyframes
# Title Position offsets (comp px from centre 960,540) for each keyframe pose.
KEY_POSES = [(-250, 60), (0, -120), (190, 20), (0, 0)]  # follow-up 1: third pose 190 px right
END_COMP_T = 6.5                     # playhead rests here -> 0;00;06;15

# ---------------------------------------------------------------- beats / events
T_KNOCKS = [0.5, 1.0]
T_PEEL0, T_PEEL1 = 1.5, 1.9
T_POP = 2.0
T_TYPE, T_RECT, T_PEN = 2.5, 3.0, 3.5
TYPE_START, TYPE_STEP = 2.55, 0.04   # letters at 2.55 + i*0.04
T_SPARK = T_RECT
T_SWOOSH0, T_SWOOSH1 = T_PEN + 0.02, T_PEN + 0.45
T_GLOW_LAND = 4.5
T_KICK = 5.0
T_CHIP_HIT = 5.5
T_KEYS = [6.0, 6.5, 7.0, 7.5]
T_PLAYHEAD_LAND = 8.0
T_REWIND0, T_REWIND1 = 8.0, 8.4
T_SURF0, T_SURF1 = 8.5, 9.6
T_PLAY = 10.0
T_FALLS = [10.45, 10.6, 10.75, 10.9, 11.05, 11.2]
FALL_ORDER = ["timeline", "project", "effects", "info", "topbar", "preview"]
T_FINAL_LAND = 11.0
T_WAVE0 = 11.2
FADE0 = 11.5


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lin(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_out_back(x, s=1.70158):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def ease_out_elastic(x):
    x = clamp(x)
    if x in (0.0, 1.0):
        return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi / 3)) + 1


def mix(a, b, s):
    return a + (b - a) * s


# ---------------------------------------------------------------- playhead
def playhead_t(t):
    """Comp time under the playhead at wall time t (AE logic)."""
    if t < HOPS_BY_LABEL["to_key0"]["t0"]:
        return 0.0
    # During each keyframe hop the playhead glides to that key time.
    prev = 0.0
    for i, label in enumerate(["to_key0", "to_key1", "to_key2", "to_key3"]):
        h = HOPS_BY_LABEL[label]
        if t < h["t0"]:
            return prev
        if t < h["t1"]:
            return mix(prev, KEY_TIMES[i], ease_in_out(lin(t, h["t0"], h["t1"])))
        prev = KEY_TIMES[i]
    if t < T_REWIND0:
        return KEY_TIMES[-1]
    if t < T_REWIND1:
        return mix(KEY_TIMES[-1], 0.0, ease_in_out(lin(t, T_REWIND0, T_REWIND1)))
    if t < T_SURF0:
        return 0.0
    if t < T_SURF1:
        return mix(0.0, END_COMP_T, smooth(lin(t, T_SURF0, T_SURF1)))
    return END_COMP_T


def timecode(ct):
    frames = int(round(ct * FPS))
    s, f = divmod(frames, FPS)
    return "0;00;%02d;%02d" % (s, f)


def keys_stamped(t):
    return sum(1 for tk in T_KEYS if t >= tk)


def title_offset(t):
    """Position of layer 1 (comp px offset from centre), real AE interpolation."""
    n = keys_stamped(t)
    if n == 0:
        return (0.0, 0.0)
    ct = playhead_t(t)
    times, poses = KEY_TIMES[:n], KEY_POSES[:n]
    if ct <= times[0]:
        return poses[0]
    if ct >= times[-1]:
        return poses[-1]
    for i in range(n - 1):
        if times[i] <= ct <= times[i + 1]:
            s = ease_in_out(lin(ct, times[i], times[i + 1]))  # easy-ease keys
            return (mix(poses[i][0], poses[i + 1][0], s), mix(poses[i][1], poses[i + 1][1], s))
    return poses[-1]


# ---------------------------------------------------------------- hops
def _tool(name):
    return TOOLS[name]


HOPS = [
    # label, t0 (take-off), t1 (landing), from (u, v), to (u, v), z0, z1, apex (m), flip
    dict(label="pop_to_type", t0=T_POP, t1=T_TYPE, a=COMP_CENTER_UI, b=_tool("Type"),
         z0=0.10, z1=CAP_TOP_Z, apex=0.30, flip=0, whoosh=True),
    dict(label="to_rect", t0=T_TYPE + 0.08, t1=T_RECT, a=_tool("Type"), b=_tool("Rectangle"),
         z0=CAP_TOP_Z, z1=CAP_TOP_Z, apex=0.11, flip=0, whoosh=False),
    dict(label="to_pen", t0=T_RECT + 0.08, t1=T_PEN, a=_tool("Rectangle"), b=_tool("Pen"),
         z0=CAP_TOP_Z, z1=CAP_TOP_Z, apex=0.09, flip=0, whoosh=False),
    dict(label="flip_to_glow", t0=T_PEN + 0.12, t1=T_GLOW_LAND, a=_tool("Pen"), b=GLOW_LAND,
         z0=CAP_TOP_Z, z1=0.0, apex=0.36, flip=1, whoosh=True),  # follow-up 3: apex 0.36 m
    dict(label="to_key0", t0=T_KICK + 0.15, t1=T_KEYS[0], a=GLOW_LAND, b=(comp_t_to_u(KEY_TIMES[0]), POSITION_ROW_Y),
         z0=0.0, z1=KEY_GEM_TOP_Z, apex=0.30, flip=0, whoosh=True),
    dict(label="to_key1", t0=T_KEYS[0] + 0.08, t1=T_KEYS[1], a=(comp_t_to_u(KEY_TIMES[0]), POSITION_ROW_Y),
         b=(comp_t_to_u(KEY_TIMES[1]), POSITION_ROW_Y), z0=KEY_GEM_TOP_Z, z1=KEY_GEM_TOP_Z, apex=0.10, flip=0, whoosh=False),
    dict(label="to_key2", t0=T_KEYS[1] + 0.08, t1=T_KEYS[2], a=(comp_t_to_u(KEY_TIMES[1]), POSITION_ROW_Y),
         b=(comp_t_to_u(KEY_TIMES[2]), POSITION_ROW_Y), z0=KEY_GEM_TOP_Z, z1=KEY_GEM_TOP_Z, apex=0.10, flip=0, whoosh=False),
    dict(label="to_key3", t0=T_KEYS[2] + 0.08, t1=T_KEYS[3], a=(comp_t_to_u(KEY_TIMES[2]), POSITION_ROW_Y),
         b=(comp_t_to_u(KEY_TIMES[3]), POSITION_ROW_Y), z0=KEY_GEM_TOP_Z, z1=KEY_GEM_TOP_Z, apex=0.10, flip=0, whoosh=False),
    dict(label="to_playhead", t0=T_KEYS[3] + 0.1, t1=T_PLAYHEAD_LAND, a=(comp_t_to_u(KEY_TIMES[3]), POSITION_ROW_Y),
         b=(comp_t_to_u(KEY_TIMES[3]), PLAYHEAD_HEAD_Y), z0=KEY_GEM_TOP_Z, z1=PLAYHEAD_TOP_Z, apex=0.12, flip=0, whoosh=False),
    dict(label="to_play", t0=T_SURF1, t1=T_PLAY, a=(comp_t_to_u(END_COMP_T), PLAYHEAD_HEAD_Y), b=PREVIEW_BUTTONS["Play"],
         z0=PLAYHEAD_TOP_Z, z1=CAP_TOP_Z, apex=0.26, flip=0, whoosh=True),
    # follow-up 3: land at x 800 instead of 862, on the comp panel's lower-right corner
    dict(label="to_comp_corner", t0=10.38, t1=T_FINAL_LAND, a=PREVIEW_BUTTONS["Play"], b=(800, 390),
         z0=CAP_TOP_Z, z1=0.0, apex=0.24, flip=0, whoosh=True),
]
HOPS_BY_LABEL = {h["label"]: h for h in HOPS}

# Which UI target each landing presses (drives cap press + state changes)
LANDING_TARGET = {
    "pop_to_type": ("tool", "Type"),
    "to_rect": ("tool", "Rectangle"),
    "to_pen": ("tool", "Pen"),
    "flip_to_glow": ("effect", "Glow"),
    "to_key0": ("key", 0), "to_key1": ("key", 1), "to_key2": ("key", 2), "to_key3": ("key", 3),
    "to_playhead": ("playhead", None),
    "to_play": ("preview", "Play"),
    "to_comp_corner": ("comp", None),
}


def _hop_at(t):
    """Return (hop, phase) where phase is 'air', or the most recent hop when resting."""
    last = None
    for h in HOPS:
        if h["t0"] <= t < h["t1"]:
            return h, "air"
        if t >= h["t1"]:
            last = h
    return last, "rest"


def active_tool(t):
    tool = "Selection"
    for label, (kind, name) in LANDING_TARGET.items():
        if kind == "tool" and t >= HOPS_BY_LABEL[label]["t1"]:
            tool = name
    return tool


def cap_press(name, t):
    """0..1 press depth for a toolbar/preview keycap: down while Clawd stands on it."""
    for label, (kind, target) in LANDING_TARGET.items():
        if kind in ("tool", "preview") and target == name:
            h = HOPS_BY_LABEL[label]
            idx = HOPS.index(h)
            nxt = HOPS[idx + 1]["t0"] if idx + 1 < len(HOPS) else DURATION
            if h["t1"] - 0.03 <= t < nxt + 0.06:
                down = smooth(lin(t, h["t1"] - 0.03, h["t1"] + 0.03))
                up = 1 - smooth(lin(t, nxt, nxt + 0.06))
                return min(down, up)
    return 0.0


# ---------------------------------------------------------------- mascot state
def mascot_state(t):
    """Clawd pose at time t. Positions in metres; angles in radians."""
    st = dict(visible=t >= T_POP, scale=1.0, squash=0.0, yaw=0.0, pitch=0.0, roll=0.0,
              eyes="open", wave=0.0, kick=0.0, lean=0.0)
    if t < T_POP:
        u, v = COMP_CENTER_UI
        st.update(u=u, v=v, z=0.0)
        return st
    h, phase = _hop_at(t)
    if phase == "air":
        s = lin(t, h["t0"], h["t1"])
        u = mix(h["a"][0], h["b"][0], s)
        v = mix(h["a"][1], h["b"][1], s)
        z = mix(h["z0"], h["z1"], s) + 4 * h["apex"] * s * (1 - s)
        du, dv = h["b"][0] - h["a"][0], h["b"][1] - h["a"][1]
        heading = math.atan2(du, abs(dv) + 40.0)  # 0 = toward camera; never show his back
        st["yaw"] = _soft_yaw(heading)
        st["squash"] = -0.10 * math.sin(math.pi * s)  # stretch mid-air
        if h["flip"]:
            st["pitch"] = -2 * math.pi * ease_in_out(lin(s, 0.15, 0.85))
        if h["label"] == "pop_to_type":
            st["scale"] = mix(0.55, 1.0, ease_out_elastic(lin(t, T_POP, T_POP + 0.35)))
        st.update(u=u, v=v, z=z)
    else:
        u, v = h["b"]
        z = h["z1"]
        # landing squash, then take-off anticipation for the next hop
        land = lin(t, h["t1"], h["t1"] + 0.16)
        sq = 0.22 * math.sin(math.pi * land) * (1 - land)
        nxt = next((n for n in HOPS if n["t0"] > t), None)
        if nxt is not None:
            pre = lin(t, nxt["t0"] - 0.09, nxt["t0"])
            sq = max(sq, 0.16 * math.sin(math.pi * pre))
        st["squash"] = sq
        kind, target = LANDING_TARGET[h["label"]]
        if kind in ("tool", "preview"):
            z -= CAP_PRESS * cap_press(target, t)
        st["yaw"] = _soft_yaw(0.0)
        if h["label"] == "flip_to_glow":
            # face the chip (left), lunge and kick at T_KICK
            st["yaw"] = -math.pi / 2 * 0.8 * smooth(lin(t, T_GLOW_LAND + 0.1, T_GLOW_LAND + 0.3))
            lunge = smooth(lin(t, T_KICK - 0.12, T_KICK)) * (1 - smooth(lin(t, T_KICK + 0.02, T_KICK + 0.14)))
            u -= 14 * lunge
            st["kick"] = lunge
        if h["label"] == "to_playhead":
            u = comp_t_to_u(playhead_t(t))
            z = PLAYHEAD_TOP_Z
            ride = (T_REWIND0 <= t < T_REWIND1) or (T_SURF0 <= t < T_SURF1)
            if ride:
                vel = playhead_t(t + 1 / FPS) - playhead_t(t)
                st["lean"] = clamp(-vel * 6, -0.35, 0.35)
                st["yaw"] = math.pi / 2 * (1 if vel >= 0 else -1) * 0.75  # side-on surf stance
            if T_SURF0 <= t < T_SURF1:
                st["roll"] = 0.06 * math.sin((t - T_SURF0) * 14)
        if h["label"] == "to_comp_corner":
            st["yaw"] = -0.25
            if t >= T_WAVE0:
                st["eyes"] = "happy"
                st["wave"] = smooth(lin(t, T_WAVE0, T_WAVE0 + 0.12))
        st.update(u=u, v=v, z=z)
    return st


def _soft_yaw(heading):
    """Blend travel heading toward camera-facing so the face stays readable."""
    while heading > math.pi:
        heading -= 2 * math.pi
    while heading < -math.pi:
        heading += 2 * math.pi
    return heading * 0.6


def wave_angle(t):
    if t < T_WAVE0:
        return 0.0
    return smooth(lin(t, T_WAVE0, T_WAVE0 + 0.12)) * (0.9 + 0.5 * math.sin((t - T_WAVE0) * 2 * math.pi * 2.4))


# ---------------------------------------------------------------- peel card
def card_state(t):
    """Flat clawd card that peels off the comp between T_PEEL0 and T_POP."""
    if t < T_PEEL0 or t >= T_POP:
        return dict(visible=False, angle=0.0, lift=0.0, scale=1.0)
    p = ease_out_cubic(lin(t, T_PEEL0, T_PEEL1))
    wob = 0.08 * math.sin((t - T_PEEL1) * 40) * lin(t, T_PEEL1, T_POP) if t > T_PEEL1 else 0.0
    return dict(visible=True, angle=math.radians(82) * p + wob, lift=0.05 * p,
                scale=1.0 + 0.15 * lin(t, T_PEEL1, T_POP))


# ---------------------------------------------------------------- glow chip
def chip_state(t):
    if t < T_GLOW_LAND or t >= T_CHIP_HIT + 0.1:
        return dict(visible=False)
    u0, v0 = GLOW_CHIP_HOME
    if t < T_KICK:
        p = ease_out_back(lin(t, T_GLOW_LAND, T_GLOW_LAND + 0.18))
        bob = 0.006 * math.sin((t - T_GLOW_LAND) * 12)
        return dict(visible=True, u=u0, v=v0, z=0.07 * p + bob * p, scale=max(p, 0.001), spin=0.0, tilt=0.0)
    s = lin(t, T_KICK, T_CHIP_HIT)
    u1, v1 = COMP_CENTER_UI
    u = mix(u0, u1, ease_out_cubic(s) * 0.3 + s * 0.7)
    v = mix(v0, v1, s)
    z = mix(0.07, COMP_GLASS_Z + 0.02, s) + 4 * 0.28 * s * (1 - s)
    sc = 1.0 if t < T_CHIP_HIT else 1 - lin(t, T_CHIP_HIT, T_CHIP_HIT + 0.1)
    return dict(visible=True, u=u, v=v, z=z, scale=max(sc, 0.001), spin=s * 3 * math.pi, tilt=s * 0.6)


# ---------------------------------------------------------------- shards
def shards_active(t):
    return T_POP <= t < T_POP + 1.2


# ---------------------------------------------------------------- panel falls
def panel_fall(name, t):
    """(power 1->0, drop metres, tilt radians) for a falling panel; comp never falls."""
    if name not in FALL_ORDER:
        return 1.0, 0.0, 0.0
    t0 = T_FALLS[FALL_ORDER.index(name)]
    power = 1.0 - smooth(lin(t, t0, t0 + 0.12))
    if t0 <= t < t0 + 0.12:  # power-down flicker
        power *= 0.6 + 0.4 * (1 if int((t - t0) * 120) % 2 else 0)
    ft = max(0.0, t - (t0 + 0.08))
    drop = 0.5 * 9.0 * ft * ft
    tilt = 0.9 * ft * ft * (1 if FALL_ORDER.index(name) % 2 else -1)
    return power, drop, tilt


# ---------------------------------------------------------------- comp canvas state
def comp_state(t):
    """Everything the comp canvas needs at wall time t (comp pixels, 1920x1080)."""
    letters = sum(1 for i in range(len(TITLE)) if t >= TYPE_START + i * TYPE_STEP)
    ox, oy = title_offset(t)
    knock = 0.0
    for tk in T_KNOCKS:
        if tk <= t < tk + 0.25:
            knock = max(knock, math.sin(math.pi * lin(t, tk, tk + 0.18)) * (1 - lin(t, tk, tk + 0.25)))
    ripples = [round(lin(t, tk, tk + 0.45), 4) for tk in T_KNOCKS if tk <= t < tk + 0.45]
    return dict(
        flat_clawd=t < T_PEEL0,                       # clawd.png layer drawn flat
        handles=t < T_PEEL0,                          # selection handles + anchor point
        knock=round(knock, 4),                        # 0..1 bump toward the glass
        ripples=ripples,                              # knock ripple progress list
        cracks=round(1.0 - lin(t, T_POP + 0.6, T_POP + 1.4), 4) if t >= T_POP else 0.0,
        crack_grow=round(ease_out_cubic(lin(t, T_POP, T_POP + 0.12)), 4) if t >= T_POP else 0.0,
        letters=letters,                              # typed characters of TITLE
        cursor=T_TYPE <= t < TYPE_START + len(TITLE) * TYPE_STEP + 0.3,
        title_dx=round(ox, 2), title_dy=round(oy, 2),
        spark=round(ease_out_elastic(lin(t, T_SPARK, T_SPARK + 0.5)), 4) if t >= T_SPARK else 0.0,
        spark_rot=round(0.25 * (t - T_SPARK), 4) if t >= T_SPARK else 0.0,
        swoosh=round(ease_in_out(lin(t, T_SWOOSH0, T_SWOOSH1)), 4),
        glow=round(ease_out_cubic(lin(t, T_CHIP_HIT, T_CHIP_HIT + 0.3)), 4),
        shimmer=round(math.sin(math.pi * lin(t, T_CHIP_HIT, T_CHIP_HIT + 0.6)), 4) if T_CHIP_HIT <= t < T_CHIP_HIT + 0.6 else 0.0,
        flash=round(math.exp(-(t - T_PLAY) * 9.0), 4) if t >= T_PLAY else 0.0,
        subtitle=round(ease_out_back(lin(t, T_PLAY + 0.05, T_PLAY + 0.45)), 4) if t >= T_PLAY else 0.0,
        particles=round(t - T_PLAY, 4) if T_PLAY <= t < T_PLAY + 1.8 else -1.0,  # age; seeded on the JS side
        selected_layer="clawd.png" if t < T_PEEL0 else ("MADE WITH CLAUDE" if t >= T_TYPE else None),
    )


def ui_state(t):
    return dict(
        active_tool=active_tool(t),
        glow_selected=t >= T_GLOW_LAND,
        play_pressed=t >= T_PLAY,
        keys=keys_stamped(t),
        playhead_t=round(playhead_t(t), 5),
        timecode=timecode(playhead_t(t)),
    )


# ---------------------------------------------------------------- sound events
NOTE = {"C5": 523.25, "E5": 659.25, "G5": 783.99, "C6": 1046.50}


def events():
    """Every audible cue: (time, kind, params). Sorted by time."""
    ev = []
    for tk in T_KNOCKS:
        ev.append((tk, "glass_knock", {}))
    ev.append((T_PEEL0, "sticker_peel", {"dur": T_PEEL1 - T_PEEL0}))
    ev.append((T_PEEL0, "riser", {"dur": T_POP - T_PEEL0}))
    ev.append((T_POP, "pop", {}))
    ev.append((T_POP, "glass_break", {}))
    ev.append((T_POP, "sub_boom", {}))
    ev.append((T_POP, "beat_drop", {}))
    for h in HOPS:
        ev.append((h["t0"], "boing", {"hop": h["label"]}))
        if h["whoosh"]:
            ev.append((h["t0"] + 0.05, "whoosh", {"dur": h["t1"] - h["t0"], "hop": h["label"]}))
        ev.append((h["t1"], "pomf", {"hop": h["label"]}))
    for label in ("pop_to_type", "to_rect", "to_pen"):
        ev.append((HOPS_BY_LABEL[label]["t1"], "keycap_click", {"tool": LANDING_TARGET[label][1]}))
        ev.append((HOPS_BY_LABEL[label]["t1"] + 0.03, "ui_blip", {"tool": LANDING_TARGET[label][1]}))
    for i in range(len(TITLE)):
        ev.append((TYPE_START + i * TYPE_STEP, "key_tap", {"char": TITLE[i], "i": i}))
    ev.append((T_SPARK + 0.02, "bloop", {}))
    ev.append((T_SWOOSH0, "pen_scribble", {"dur": T_SWOOSH1 - T_SWOOSH0}))
    ev.append((T_GLOW_LAND + 0.04, "select_blip", {}))
    ev.append((T_KICK, "thwack", {}))
    ev.append((T_KICK + 0.02, "whoosh", {"dur": T_CHIP_HIT - T_KICK, "hop": "chip"}))
    ev.append((T_CHIP_HIT, "magic_shimmer", {"dur": 0.9}))
    ev.append((T_CHIP_HIT, "bells", {}))
    for tk, note in zip(T_KEYS, ["C5", "E5", "G5", "C6"]):
        ev.append((tk, "ding", {"note": note, "freq": NOTE[note]}))
    ev.append((T_REWIND0, "tape_rewind", {"dur": T_REWIND1 - T_REWIND0}))
    ev.append((T_SURF0, "skate_roll", {"dur": T_SURF1 - T_SURF0}))
    # scrub ticks every comp frame-group the playhead crosses during the surf (each 0.25 s of comp time)
    k = 1
    tt = T_SURF0
    while tt < T_SURF1:
        if playhead_t(tt) >= k * 0.25:
            ev.append((tt, "scrub_tick", {"comp_t": k * 0.25}))
            k += 1
        tt += 1.0 / 240
    ev.append((T_PLAY, "ui_click", {}))
    ev.append((T_PLAY, "brass_stab", {"chord": "C major"}))
    ev.append((T_PLAY, "shimmer", {"dur": 1.2}))
    for name, tf in zip(FALL_ORDER, T_FALLS):
        ev.append((tf, "power_down", {"panel": name}))
        ev.append((tf + 0.1, "whoosh", {"dur": 0.5, "hop": "fall_" + name}))
    ev.append((T_FALLS[-1] + 0.15, "boom", {}))
    ev.append((T_WAVE0, "yay_chirps", {}))
    ev.append((T_WAVE0 + 0.1, "sparkles", {"dur": 0.7}))
    ev.append((FADE0, "fade_out", {"dur": DURATION - FADE0}))
    ev.sort(key=lambda e: e[0])
    return ev


MUSIC = dict(
    bpm=BPM,
    pre_drop="soft pad + ticking hats until T_POP",
    drop_at=T_POP,
    chords=["F", "G", "Am", "C"],  # one bar (2 s) each, looped from the drop
    brass_stab_at=T_PLAY,
    ring_out_from=T_PLAY,
    fade=(FADE0, DURATION),
)


# ---------------------------------------------------------------- JSON dump
def dump():
    layout = dict(
        ui=dict(w=UI_W, h=UI_H, scale=UI_SCALE), panels=PANELS, menubar=MENUBAR, toolbar=TOOLBAR,
        menu_items=MENU_ITEMS, comp_tabs=COMP_TABS, comp_subtab=COMP_SUBTAB, comp_view=COMP_VIEW,
        comp_bottom=COMP_BOTTOM, tc_comp=TC_COMP, tc_tl=TC_TL, tools=TOOLS, tool_order=TOOL_ORDER,
        cap=dict(w=CAP_W, h=CAP_H), preview_cap=dict(w=PREVIEW_CAP_W, h=PREVIEW_CAP_H), preview_buttons=PREVIEW_BUTTONS, preview_header_y=PREVIEW_HEADER_Y,
        preview_shortcut_y=PREVIEW_SHORTCUT_Y, effects_header_y=EFFECTS_HEADER_Y,
        effects_search=EFFECTS_SEARCH, effects_rows=EFFECTS_ROWS, glow_row=GLOW_ROW,
        tl_tabs=TL_TABS, tl_colhead_y=TL_COLHEAD_Y, tl_row_h=TL_ROW_H, tl_rows=TL_ROWS,
        position_row_y=POSITION_ROW_Y, ruler=RULER, track_x=[TRACK_X0, TRACK_X1],
        comp_duration=COMP_DURATION, playhead_head_y=PLAYHEAD_HEAD_Y,
    )
    comp = dict(title=TITLE, subtitle=SUBTITLE, subtitle_px=SUBTITLE_PX, spark_rays=SPARK_RAYS,
                spark_ray_width_px=SPARK_RAY_WIDTH_PX, key_times=KEY_TIMES, key_poses=KEY_POSES,
                terracotta=TERRACOTTA_HEX)
    frames = []
    for f in range(1, FRAMES + 1):
        t = f2t(f)
        frames.append(dict(frame=f, t=round(t, 5), comp=comp_state(t), ui=ui_state(t)))
    return dict(fps=FPS, frames_total=FRAMES, duration=DURATION, bpm=BPM, layout=layout,
                comp=comp, frames=frames,
                events=[dict(t=round(e[0], 5), kind=e[1], **e[2]) for e in events()])


if __name__ == "__main__":
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        with open(out, "w") as fh:
            json.dump(dump(), fh, indent=1, ensure_ascii=False)
        print("wrote", out)
    else:
        for e in events():
            print("%6.3f  f%03d  %-14s %s" % (e[0], t2f(e[0]), e[1], e[2]))
