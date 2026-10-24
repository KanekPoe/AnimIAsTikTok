"""Efectos de sonido y base musical sintetizados con numpy (sin archivos externos)."""
import numpy as np

SR = 48000
rng = np.random.default_rng(3)


def _t(d):
    return np.arange(int(d * SR)) / SR


def env(d, a=0.005, r=None):
    t = _t(d)
    r = r or d
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / (r / 4))
    return e


def noise(d):
    return rng.uniform(-1, 1, int(d * SR))


def lowpass(x, k=8):
    return np.convolve(x, np.ones(k) / k, mode="same")


def sweep(f0, f1, d, wave="sine"):
    t = _t(d)
    f = np.geomspace(f0, f1, len(t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) if wave == "sine" else np.sign(np.sin(ph)) * 0.6


def tone(f, d, a=0.005, r=None):
    return np.sin(2 * np.pi * f * _t(d)) * env(d, a, r)


# --- efectos -----------------------------------------------------------------
def whoosh(d=0.45, up=True):
    n = noise(d)
    k = np.linspace(40, 4, len(n)).astype(int) if up else np.linspace(4, 40, len(n)).astype(int)
    out = np.empty_like(n)
    for i in range(0, len(n), 512):  # filtro que se abre/cierra
        kk = max(2, int(k[i]))
        out[i:i + 512] = lowpass(n[i:i + 512 + kk], kk)[:len(n[i:i + 512])]
    shape = np.sin(np.linspace(0, np.pi, len(n))) ** 1.5
    return out * shape * 0.9


def impact():
    d = 1.4
    boom = sweep(90, 35, d) * env(d, 0.002, 1.2)
    crack = lowpass(noise(0.25), 3) * env(0.25, 0.001, 0.15)
    out = boom * 1.0
    out[:len(crack)] += crack * 0.8
    return out


def stamp():
    d = 0.35
    return (sweep(160, 60, d) * env(d, 0.001, 0.25) + lowpass(noise(d), 4) * env(d, 0.001, 0.08)) * 0.9


def blip(f=880, d=0.12):
    return tone(f, d, 0.002, 0.1) * 0.5


def pop():
    return sweep(300, 900, 0.09) * env(0.09, 0.002, 0.09) * 0.5


def holo_open():
    out = np.zeros(int(0.35 * SR))
    for i, f in enumerate((660, 990, 1320)):
        s = tone(f, 0.12, 0.002, 0.1) * 0.25
        o = int(i * 0.06 * SR)
        out[o:o + len(s)] += s
    return out


def click():
    return lowpass(noise(0.03), 2) * env(0.03, 0.0005, 0.02) * 0.7


def sparkle():
    out = np.zeros(int(1.0 * SR))
    for i, f in enumerate((1047, 1319, 1568, 2093, 2637, 3136)):
        s = tone(f, 0.35, 0.002, 0.3) * 0.18
        o = int(i * 0.07 * SR)
        out[o:o + len(s)] += s
    return out


def drip():
    return sweep(1400, 500, 0.12) * env(0.12, 0.001, 0.1) * 0.45


def clunk():
    """Golpe metálico (casco)."""
    return (sweep(220, 110, 0.25) * env(0.25, 0.001, 0.2) + tone(1250, 0.25, 0.001, 0.12) * 0.3) * 0.8


def rise_alarm():
    r = sweep(200, 800, 0.35, "square") * np.linspace(0, 0.3, int(0.35 * SR))
    b = np.concatenate([tone(880, 0.12) * 0.35, np.zeros(int(0.05 * SR)), tone(880, 0.12) * 0.35])
    return np.concatenate([r, b])


def thud():
    return sweep(120, 45, 0.4) * env(0.4, 0.001, 0.3)


def ding_dong():
    return np.concatenate([tone(988, 0.3, 0.002, 0.3), tone(784, 0.5, 0.002, 0.45)]) * 0.35


def zip_strike():
    return sweep(400, 2400, 0.18, "square") * env(0.18, 0.001, 0.18) * 0.18


def rocket():
    return whoosh(0.9, up=True) * 0.8 + sweep(80, 300, 0.9) * 0.15


def mech():
    out = np.zeros(int(0.6 * SR))
    for i in range(4):
        s = click() * 1.2
        o = int(i * 0.12 * SR)
        out[o:o + len(s)] += s
    return out + sweep(300, 150, 0.6, "square") * env(0.6, 0.01, 0.6) * 0.08


def chime():
    out = np.zeros(int(1.6 * SR))
    for f in (523, 659, 784, 1047):
        out += tone(f, 1.6, 0.01, 1.4) * 0.12
    return out


GAG_SFX = {
    "globe_return": lambda: whoosh(0.4),
    "remote": blip,
    "closed_sign": ding_dong,
    "screen:stamp": stamp,
    "screen:crossed": zip_strike,
    "globe_split": sparkle,
    "sweat": drip,
    "screen:phase1": holo_open,
    "hardhat": clunk,
    "screen:mars": rocket,
    "red_button": rise_alarm,
    "screen:tanks": mech,
    "charger": thud,
    "screen:off": lambda: sweep(800, 80, 0.15) * 0.3,
}


# --- base musical ------------------------------------------------------------
def music_bed(duration, bpm=100):
    """Base suave: bombo, hi-hat y acordes filtrados (Am-F-C-G)."""
    n = int(duration * SR)
    out = np.zeros(n)
    beat = 60 / bpm
    chords = [(220, 261.6, 329.6), (174.6, 220, 261.6), (130.8, 164.8, 196), (196, 246.9, 293.7)]
    t_bar = beat * 4
    for b in range(int(duration / t_bar) + 1):
        ch = chords[b % 4]
        s = int(b * t_bar * SR)
        d = min(t_bar, duration - b * t_bar)
        if d <= 0:
            break
        t = _t(d)
        pad = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t) for f in ch)
        pad *= np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.3) * 0.05
        out[s:s + len(pad)] += pad
    for k in range(int(duration / beat)):
        s = int(k * beat * SR)
        kick = sweep(110, 45, 0.25) * env(0.25, 0.001, 0.2) * 0.35
        out[s:s + len(kick)] += kick[:max(0, n - s)]
        h = int((k + 0.5) * beat * SR)
        hat = lowpass(noise(0.05), 1) * env(0.05, 0.0005, 0.03) * 0.06
        out[h:h + len(hat)] += hat[:max(0, n - h)]
    return out
