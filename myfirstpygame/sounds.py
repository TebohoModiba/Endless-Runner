import pygame
import numpy as np

SAMPLE_RATE = 44100

def _make_sound(wave):
    """Convert a numpy array into a pygame Sound object."""
    wave = np.clip(wave, -1.0, 1.0)
    wave = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


def _sine(freq, duration, volume=0.5, fade=True):
    """Generate a sine wave tone."""
    t     = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave  = np.sin(2 * np.pi * freq * t) * volume
    if fade:
        fade_samples = int(SAMPLE_RATE * duration * 0.3)
        wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    return wave


def _noise(duration, volume=0.3):
    """Generate white noise."""
    samples = int(SAMPLE_RATE * duration)
    return (np.random.uniform(-1, 1, samples) * volume)


def make_jump_sound():
    """Rising pitch sweep — feels like launching upward."""
    duration = 0.25
    t        = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq     = np.linspace(200, 600, len(t))   # pitch rises from 200Hz to 600Hz
    wave     = np.sin(2 * np.pi * freq * t / SAMPLE_RATE * SAMPLE_RATE) * 0.4
    fade     = int(len(wave) * 0.3)
    wave[-fade:] *= np.linspace(1, 0, fade)
    return _make_sound(wave)


def make_death_sound():
    """Falling pitch + noise — feels like a crash."""
    duration = 0.6
    t        = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq     = np.linspace(400, 80, len(t))    # pitch falls from 400Hz to 80Hz
    tone     = np.sin(2 * np.pi * freq * t / SAMPLE_RATE * SAMPLE_RATE) * 0.4
    noise    = _noise(duration, volume=0.2)
    wave     = tone + noise
    fade     = int(len(wave) * 0.2)
    wave[-fade:] *= np.linspace(1, 0, fade)
    return _make_sound(wave)


def make_score_sound():
    """Short double-blip — plays every 50 points."""
    blip1 = _sine(520, 0.07, volume=0.3)
    blip2 = _sine(780, 0.07, volume=0.3)
    gap   = np.zeros(int(SAMPLE_RATE * 0.04))
    wave  = np.concatenate([blip1, gap, blip2])
    return _make_sound(wave)


def make_double_jump_sound():
    """Higher blip — distinct from the first jump."""
    duration = 0.2
    t        = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq     = np.linspace(500, 900, len(t))
    wave     = np.sin(2 * np.pi * freq * t / SAMPLE_RATE * SAMPLE_RATE) * 0.35
    fade     = int(len(wave) * 0.3)
    wave[-fade:] *= np.linspace(1, 0, fade)
    return _make_sound(wave)


def load_sounds():
    """Call this once after pygame.init() to get all sounds."""
    pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
    return {
        "jump":        make_jump_sound(),
        "double_jump": make_double_jump_sound(),
        "death":       make_death_sound(),
        "score":       make_score_sound(),
    }