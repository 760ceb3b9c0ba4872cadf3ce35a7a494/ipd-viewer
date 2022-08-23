from PIL import Image
from ipd.ipd_file import IPDHeader
import wx
from ..constants import FLAG_NAMES
from ..utils import calculate_aspect_ratio


class MetadataPane(wx.ScrolledWindow):
    def __init__(self, parent, select_callback):
        super().__init__(
            parent=parent
        )
        self.SetMinSize((192, 192))
        self.outer_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_text = wx.StaticText(
            parent=self,
            label="!!!"
        )

        self.choice_box = wx.Choice(
            parent=self,
            choices=[
                "Auto",
                "Force top-bottom",
                "Force bottom-top"
            ]
        )
        self.choice_box.Bind(wx.EVT_CHOICE, lambda _: select_callback(self.choice_box.GetSelection()))

        self.sizer.Add(self.main_text, flag=wx.EXPAND)
        self.sizer.Add(
            window=self.choice_box,
            flag=wx.EXPAND | wx.TOP,
            border=6
        )

        self.palette_panel = None

        self.outer_sizer.Add(
            sizer=self.sizer,
            flag=wx.ALL | wx.EXPAND,
            border=4,
            proportion=1
        )
        self.SetSizer(self.outer_sizer)

    def update(self, image: Image.Image, header: IPDHeader, reset_selection: bool = True):
        if self.palette_panel:
            self.palette_panel.Destroy()

        ratio_x, ratio_y = calculate_aspect_ratio(header.width, header.height)
        palette_info, image_info, v_flip = FLAG_NAMES[header.flags]

        self.main_text.SetLabel(f"""Size: {header.width}x{header.height} [{ratio_x}:{ratio_y}]
Flags: {header.flags:08b}
Bits per pixel: {header.bits_per_pixel}
Drawing direction: {'Bottom-top' if v_flip else 'Top-bottom'}""")

        if reset_selection:
            self.choice_box.SetSelection(0)
