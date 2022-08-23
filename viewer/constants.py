import wx

WINDOW_SIZE = (800, 600)
WINDOW_MIN_SIZE = (320, 240)

IMAGE_MIN_SCALE = 0.25
IMAGE_MAX_SCALE = 4
IMAGE_SCALE_INCREMENT = 0.25

SASH_GRAVITY = .65
PALETTE_COLOR_SIZE = 12

FLAG_NAMES = {
    0b00001000: ("32-byte, unknown", "4-bpp", True),
    0b00000010: (None, "16-bpp, 556 order", True),
    0b00001010: ("512-byte, 16-bpp, 565 order", "8-bpp", False),
    0b00000000: (None, "8-bpp", False),
    0b00000101: (None, "32-bpp, 8-bpc, RGBA", True),
    0b00001001: ("1024-byte, 32-bpp, 8-bpc, RGBA", "8-bpp", True),
    0b00000001: (None, "16-bpp, 565 order, RGB", False)
}
SETTINGS = wx.SystemSettings
