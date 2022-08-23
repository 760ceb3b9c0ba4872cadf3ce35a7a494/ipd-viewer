import wx


class ScaledImage(wx.Panel):
    def __init__(self, parent, bitmap: wx.Bitmap = None, scale: float = 1):
        super().__init__(
            parent=parent,
            size=(0, 0)
        )

        self._bitmap = bitmap
        self.scale = scale

        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def _calc_size(self):
        if not self.bitmap:
            return 0, 0
        bit_x, bit_y = self.bitmap.GetSize()
        return int(bit_x * self._scale), int(bit_y * self._scale)

    def _update_size(self):
        new_size = self._calc_size()
        self.SetMinSize(new_size)

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self._update_size()

    @property
    def bitmap(self):
        return self._bitmap

    @bitmap.setter
    def bitmap(self, value):
        self._bitmap = value
        self._update_size()

    def OnPaint(self, _: wx.PaintEvent):
        if not self.bitmap:
            return

        dc = wx.PaintDC(self)
        gr: wx.GraphicsRenderer = wx.GraphicsRenderer.GetDefaultRenderer()
        gc: wx.GraphicsContext = gr.CreateContext(dc)

        # dc.DrawBitmap(self.bitmap, 0, 0, True)
        gc.DrawBitmap(self.bitmap, 0, 0, *self._calc_size())
