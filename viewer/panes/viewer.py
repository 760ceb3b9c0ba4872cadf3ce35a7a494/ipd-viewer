import wx
from ..scaled_image import ScaledImage
from ..constants import IMAGE_MAX_SCALE, IMAGE_MIN_SCALE, IMAGE_SCALE_INCREMENT


class ViewerPane(wx.ScrolledWindow):
    def __init__(self, parent):
        super().__init__(
            parent=parent
        )
        self.SetMinSize((320, 240))
        self.SetScrollbars(1, 1, 1, 1)
        self.SetBackgroundColour((30, 30, 30))
        self.outer_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.image_win = ScaledImage(
            parent=self,
            bitmap=None,
            scale=1
        )

        self.sizer.Add(self.image_win, flag=wx.ALIGN_CENTER_VERTICAL)

        self.outer_sizer.Add(
            sizer=self.sizer,
            proportion=1,
            flag=wx.ALIGN_CENTER_HORIZONTAL
        )
        self.SetSizer(self.outer_sizer)

    def _refresh(self):
        self.Refresh()
        self.Layout()

    def zoom_in(self):
        if self.image_win.scale < IMAGE_MAX_SCALE:
            self.image_win.scale += IMAGE_SCALE_INCREMENT
        self._refresh()

    def zoom_out(self):
        if self.image_win.scale > IMAGE_MIN_SCALE:
            self.image_win.scale -= IMAGE_SCALE_INCREMENT
        self._refresh()

    def reset_zoom(self):
        self.image_win.scale = 1
        self._refresh()

    def set_bitmap(self, bitmap: wx.Bitmap):
        self.image_win.scale = 1
        self.image_win.bitmap = bitmap
        self._refresh()
