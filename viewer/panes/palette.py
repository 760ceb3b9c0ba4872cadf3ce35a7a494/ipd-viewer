import math
from typing import Tuple, List

import wx
import colorsys
from PIL import Image
from ..constants import PALETTE_COLOR_SIZE
from ipd.ipd_file import IPDHeader
from ..utils import chunks


class ColorSquares(wx.StaticBitmap):
    def __init__(self, *,
                 parent,
                 colors: List[Tuple[int, int, int]],
                 square_size: int,
                 column_items: int,
                 hover_callback=None
                 ):
        super().__init__(
            parent=parent,
            style=wx.NO_FULL_REPAINT_ON_RESIZE
        )

        self._colors = colors
        self.column_items = column_items
        self.square_size = square_size
        self._last_hovered = None
        self.hover_callback = hover_callback

        self.SetMinSize(self._calculate_size(len(colors)))
        self.Bind(wx.EVT_MOTION, self._movement_handler)

    def _movement_handler(self, event: wx.MouseEvent):
        x, y = event.GetPosition()
        row = y // self.square_size
        column = x // self.square_size
        index = (row * self.column_items) + column

        if index != self._last_hovered:
            self._last_hovered = index
            # todo: check if there is actually a color here

            if self.hover_callback:
                self.hover_callback(index)

    def _calculate_size(self, count: int):
        rows = math.ceil(count / self.column_items)

        return (
            self.column_items * self.square_size,
            rows * self.square_size
        )

    def update(self, colors: List[Tuple[int, int, int]]):
        size = self._calculate_size(len(colors))
        self.SetMinSize(size)
        self._colors = colors

        bitmap = wx.Bitmap(*size)
        self.draw_to_bitmap(bitmap)
        self.SetBitmap(bitmap)
        self.Refresh()

    def draw_to_dc(self, dc: wx.DC):
        for i, color in enumerate(self._colors):
            h, s, v = colorsys.rgb_to_hsv(
                color[0] / 255,
                color[1] / 255,
                color[2] / 255
            )

            if v > .123:
                dr, dg, db = colorsys.hsv_to_rgb(h, s, max(v - .1, 0))
            else:
                dr, dg, db = colorsys.hsv_to_rgb(h, s, min(v + .1, 1))

            dark_color = (
                255 * dr,
                255 * dg,
                255 * db
            )

            column = i % self.column_items
            row = i // self.column_items
            x = column * self.square_size
            y = row * self.square_size

            dc.SetPen(wx.Pen(
                colour=dark_color,
                width=1,
                style=wx.PENSTYLE_SOLID
            ))

            dc.SetBrush(wx.Brush(
                colour=color,
                style=wx.BRUSHSTYLE_SOLID
            ))

            dc.DrawRectangle(x, y, self.square_size, self.square_size)

    def draw_to_bitmap(self, bitmap: wx.Bitmap):
        # I draw to a bitmap here to make the app faster
        # resizing the window becomes slower if we use PaintDC
        # this keeps everything looking smooth at high refresh rates
        dc = wx.MemoryDC(bitmap)
        self.draw_to_dc(dc)
        del dc


class PalettePane(wx.Window):
    def __init__(self, parent):
        super().__init__(
            parent=parent,
            size=((16 * PALETTE_COLOR_SIZE), -1)
        )

        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.windows = []

        self.color_squares = ColorSquares(
            parent=self,
            colors=[],
            square_size=PALETTE_COLOR_SIZE,
            column_items=16,
            hover_callback=self.hover_color
        )

        self.info_label = wx.StaticText(
            parent=self,
            label="ABC"
        )

        font: wx.Font = self.info_label.GetFont()
        font.SetPixelSize((0, 16))
        self.info_label.SetFont(font)

        self.sizer.Add(
            window=self.color_squares,
            flag=wx.BOTTOM,
            border=4
        )

        self.color_window = wx.Window(
            parent=self,
            size=(32, 32),
            style=wx.BORDER_THEME | wx.SHAPED
        )

        info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        info_sizer.Add(self.color_window, flag=wx.RIGHT, border=4)
        info_sizer.Add(self.info_label)

        self.sizer.Add(
            sizer=info_sizer,
            flag=wx.EXPAND
        )

        outer_sizer.Add(
            sizer=self.sizer,
            border=8,
            flag=wx.ALL
        )

        self.SetSizer(outer_sizer)

        self._colors = None

    def hover_color(self, index: int):
        color = self._colors[index]
        self.info_label.SetLabel(f"{index}: {color}\n"
                                 f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}")
        self.color_window.SetBackgroundColour(color)
        self.color_window.Refresh()

    def update(self, image: Image.Image, header: IPDHeader):
        palette = image.getpalette()
        if palette:
            self._colors = list(chunks(palette, 3))

            self.color_window.Show()
            self.color_squares.Show()
            self.color_squares.update(self._colors)
            self.hover_color(0)
        else:
            self._colors = []

            self.color_squares.Hide()
            self.color_window.Hide()
            self.info_label.SetLabel("This image is not indexed.")
        self.Layout()
        self.Refresh()
