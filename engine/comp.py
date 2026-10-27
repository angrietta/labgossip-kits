"""CLAY LAB 공용 합성: 자막 스프라이트, 팝 애니메이션, 효과음 합성, 요약 이미지/영상 출력.
에피소드의 composite.py가 frame(f, img) 함수와 sfx(add, at, tone, noise, thud) 함수만 정의하면 된다.
"""
import os, sys, wave, subprocess
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "deps"))
from PIL import Image, ImageDraw, ImageFont
try:
    import imageio_ffmpeg; FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG = "ffmpeg"

W, H, FPS = 1080, 1920, 24
FD = os.path.join(ROOT, "fonts") + os.sep
ANTON = lambda s: ImageFont.truetype(FD + "Anton-Regular.ttf", s)
ARCH = lambda s: ImageFont.truetype(FD + "ArchivoBlack-Regular.ttf", s)
INK, WHITE, YEL, RED = (20, 18, 18), (255, 255, 255), (255, 214, 0), (214, 30, 50)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a))
def eback(x):
    x = clamp(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

_cache = {}
def sprite(text, font, fill, stroke=10, box=None, pad=(26, 10), rot=0):
    k = (text, font.size, font.path, fill, stroke, box, rot, pad)
    if k in _cache: return _cache[k]
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d0.textbbox((0, 0), text, font=font, stroke_width=stroke)
    im = Image.new("RGBA", (r - l + 2 * pad[0], b - t + 2 * pad[1]), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if box: d.rectangle([0, 0, im.width - 1, im.height - 1], fill=box)
    d.text((pad[0] - l, pad[1] - t), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=INK)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    _cache[k] = im; return im

def put(fr, sp, cx, cy, sc=1.0, a=1.0):
    if a <= 0.01: return
    if abs(sc - 1) > 1e-3: sp = sp.resize((max(1, int(sp.width * sc)), max(1, int(sp.height * sc))), Image.BILINEAR)
    if a < 0.999: sp = sp.copy(); sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
    fr.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))

def pop(fr, sp, cx, cy, f, f0, f1=None, dur=6):
    """Pop in at f0 (overshoot), fade out over 3 frames at f1."""
    if f < f0 or (f1 and f >= f1 + 3): return
    k = seg(f, f0, f0 + dur); a = clamp(k * 3)
    if f1: a *= 1 - seg(f, f1, f1 + 3)
    put(fr, sp, cx, cy, 1.5 - 0.5 * eback(k), a)

def tag(fr, test_no, label):
    put(fr, sprite(" LAB GOSSIP ", ANTON(46), INK, stroke=0, box=YEL, pad=(10, 4)), 150, 110)
    put(fr, sprite(f"TEST {test_no:02d} · {label}", ARCH(30), WHITE, stroke=6), 40 + sprite(f"TEST {test_no:02d} · {label}", ARCH(30), WHITE, stroke=6).width / 2, 175)

def wrap_lines(fr, lines, font, cy, f, f0, color=WHITE, stroke=6, gap=8):
    """Static multi-line small text (sources, fine print), fades in at f0."""
    if f < f0: return
    a = seg(f, f0, f0 + 6); y = cy
    for ln in lines:
        sp = sprite(ln, font, color, stroke=stroke); put(fr, sp, W / 2, y, 1, a); y += sp.height + gap

# ------------------------------------------------------------------ audio
SR = 44100
class Mixer:
    """Soft sound design: every sound has a smooth attack and release (no clicks), noise is heavily
    low-passed into a gentle 'whoosh', and the master is low-passed and normalised instead of clipped."""
    def __init__(self, f_end):
        self.n = int(f_end / FPS * SR) + SR // 2; self.out = np.zeros(self.n); self.rng = np.random.default_rng(2)
    def at(self, f): return int(f / FPS * SR)
    def add(self, i0, s):
        m = min(len(s), self.n - i0)
        if m > 0: self.out[i0:i0 + m] += s[:m]
    @staticmethod
    def env(n, attack=0.006, release=0.03, dec=0.0):
        x = np.arange(n) / SR; e = np.exp(-x * dec) if dec else np.ones(n)
        a = max(1, int(attack * SR)); r = max(1, int(release * SR))
        e[:a] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
        e[-r:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
        return e
    def tone(self, fq, d, amp, dec=8):
        """Soft mallet: sine + a little octave, smooth attack."""
        n = int(d * SR); x = np.arange(n) / SR
        w = np.sin(2 * np.pi * fq * x) + 0.18 * np.sin(4 * np.pi * fq * x) * np.exp(-x * dec * 2)
        return 0.6 * amp * w * self.env(n, 0.006, 0.03, dec)
    @staticmethod
    def _lp(x, k):
        for _ in range(3):
            x = np.convolve(x, np.ones(k) / k, "same")
        return x
    def noise(self, d, amp, lp=30):
        """Gentle whoosh (was a harsh crackle): low-passed noise with a rounded envelope, much quieter."""
        n = int(d * SR); x = self._lp(self.rng.standard_normal(n), max(lp, 90) * 2)
        x /= (np.abs(x).max() + 1e-9)
        return 0.35 * amp * x * np.sin(np.linspace(0, np.pi, n)) ** 2
    def thud(self, amp=0.9, f0=90, f1=38, d=0.5, dec=7):
        n = int(d * SR); x = np.arange(n) / SR
        w = np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-x * 9) + f1) / SR)
        return 0.55 * amp * w * self.env(n, 0.004, 0.05, dec)
    def sweep(self, fa, fb, d, amp, dec=3):
        n = int(d * SR); x = np.arange(n) / SR; fq = fa + (fb - fa) * x / d
        return 0.6 * amp * np.sin(2 * np.pi * np.cumsum(fq) / SR) * self.env(n, 0.02, 0.08, dec)
    def bubble(self, amp=0.08):
        """Small water 'bloop': short rising sine."""
        return self.sweep(260, 620, 0.09, amp * 1.6, 12)
    def bed(self, f_end, skip=()):
        notes = [261.6, 329.6, 392.0, 523.3, 392.0, 329.6]
        for k in range(int(f_end / FPS * 4)):
            t0 = k * 0.25
            if any(a <= t0 * FPS < b for a, b in skip): continue
            n = int(0.3 * SR); x = np.arange(n) / SR; fq = notes[k % 6] * (0.5 if k % 4 == 0 else 1)
            self.add(int(t0 * SR), 0.035 * np.sin(2 * np.pi * fq * x) * self.env(n, 0.015, 0.08, 7))
    def save(self, path):
        o = self.out.copy()
        a = np.exp(-2 * np.pi * 5000 / SR); y = np.zeros_like(o); acc = 0.0      # one-pole low-pass at 5 kHz
        for i in range(0, len(o), SR):                                          # chunked for speed
            seg_ = o[i:i + SR]; out = np.empty_like(seg_)
            for j, v in enumerate(seg_):
                acc = (1 - a) * v + a * acc; out[j] = acc
            y[i:i + SR] = out
        rms = np.sqrt((y ** 2).mean()) + 1e-9
        y = y * (0.07 / rms)                                                    # comfortable overall loudness
        mag = np.abs(y); knee = 0.55                                            # soft limiter: peaks are rounded, never clipped
        y = np.where(mag > knee, np.sign(y) * (knee + 0.3 * np.tanh((mag - knee) / 0.3)), y)
        fade = int(0.3 * SR); y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
        with wave.open(path, "w") as wv:
            wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((y * 32000).astype(np.int16).tobytes())

# ------------------------------------------------------------------ outputs
def load(frames_dir, f):
    p = os.path.join(frames_dir, f"{f:04d}.png")             # every frame rendered (24 fps)
    if not os.path.exists(p):
        return None
    return Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")

def main(ep_dir, f_end, frame_fn, sfx_fn, out_name):
    frames_dir = os.path.join(ep_dir, "out", "frames")
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if args and args[0] == "sheet":                       # summary image: chosen frames with captions, 3 x 2
        fs = [int(x) for x in args[1:]]; tw, th = 360, 640
        sheet = Image.new("RGB", (tw * 3, th * ((len(fs) + 2) // 3)), (30, 30, 30))
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(fs):
            img = load(frames_dir, f)
            if img is None: continue
            frame_fn(f, img)
            sheet.paste(img.convert("RGB").resize((tw, th)), ((i % 3) * tw, (i // 3) * th))
            d.rectangle([(i % 3) * tw, (i // 3) * th, (i % 3) * tw + 92, (i // 3) * th + 30], fill=(0, 0, 0))
            d.text(((i % 3) * tw + 6, (i // 3) * th + 6), f"{f / FPS:4.1f}s", fill=(255, 214, 0), font=ARCH(18))
        p = os.path.join(ep_dir, "summary.png"); sheet.save(p); print("summary:", p)
        return
    mix = Mixer(f_end); sfx_fn(mix); wav = os.path.join(ep_dir, "out", "sfx.wav"); mix.save(wav)
    out = os.path.join(ep_dir, out_name)
    p = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                          "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "160k", "-shortest", out], stdin=subprocess.PIPE)
    last = None
    for f in range(1, f_end + 1):
        img = load(frames_dir, f)
        if img is None:
            img = last.copy() if last is not None else Image.new("RGBA", (W, H), (0, 0, 0, 255))
        else:
            last = img.copy()
        frame_fn(f, img); p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait(); print("done:", out)
