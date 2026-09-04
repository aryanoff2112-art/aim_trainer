import pygame

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

SAMPLE_RATE = 44100

def _tone(freq, duration, volume=0.25, wave="sine"):
    if not _HAS_NUMPY:
        return None
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    if wave == "square":
        wave_data = np.sign(np.sin(freq * t * 2 * np.pi))
    else:
        wave_data = np.sin(freq * t * 2 * np.pi)

    fade = np.linspace(1, 0, len(t))  # avoid a click at the tail
    wave_data = wave_data * fade * volume
    audio = (wave_data * 32767).astype(np.int16)
    stereo = np.column_stack([audio, audio])
    return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))

_sound_cache = None

def _build_tones():
    return {
        "hit": _tone(880, 0.06),
        "bonus": _tone(1320, 0.08),
        "golden": _tone(1760, 0.10),
        "tiny": _tone(1046, 0.06),
        "bomb": _tone(140, 0.18, wave="square"),
        "decoy": _tone(220, 0.10, wave="square"),
        "reverse": _tone(180, 0.12, wave="square"),
        "levelup": _tone(660, 0.15),
        "gameover": _tone(330, 0.30),
        "countdown": _tone(500, 0.08),
        "go": _tone(900, 0.12),
        "achievement": _tone(1200, 0.20),
    }

class SoundEngine:
    """Cheap, dependency-light feedback tones. If numpy or the mixer are
    unavailable, play() is a silent no-op instead of raising."""

    def __init__(self, user_settings):
        global _sound_cache
        self.user_settings = user_settings
        self.sounds = {}

        if not _HAS_NUMPY:
            return

        if _sound_cache is not None:
            self.sounds = _sound_cache
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            _sound_cache = _build_tones()
            self.sounds = _sound_cache
        except pygame.error:
            self.sounds = {}

    def play(self, name):
        if not self.user_settings.get("sound_enabled", True):
            return
        sound = self.sounds.get(name)
        if sound is not None:
            try:
                sound.play()
            except pygame.error:
                pass