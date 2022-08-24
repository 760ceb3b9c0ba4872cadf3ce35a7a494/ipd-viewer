from .constants import WINDOW_SIZE, WINDOW_MIN_SIZE
from ipd.ipd_file import IPDHeader, from_stream

from typing import Optional

import wx
import wx.aui

from PIL import Image
from pathlib import Path
from .panes import MetadataPane, PalettePane, ViewerPane
from .utils import UserCancelledException


class RootFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            parent=None,
            title=".ipd viewer",
            size=WINDOW_SIZE
        )

        self.SetMinSize(WINDOW_MIN_SIZE)

        self.header: Optional[IPDHeader] = None
        self.image: Optional[Image.Image] = None
        self.path: Optional[Path] = None

        # Menu
        self.menubar = wx.MenuBar()

        self.file_menu = wx.Menu()
        self.file_menu.Append(wx.ID_OPEN, "Open\tCtrl+O", "Open")
        self.file_menu.Append(wx.ID_SAVE, "Export\tCtrl+E", "Open")
        self.menubar.Append(self.file_menu, "&File")

        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MENU, self.menu_handler)

        self.mgr = wx.aui.AuiManager()
        self.mgr.SetManagedWindow(self)

        self.view_panel = ViewerPane(self)
        self.meta_panel = MetadataPane(self, select_callback=self.override_select_callback)
        self.palette_panel = PalettePane(self)

        self.panes = []
        view_pane: wx.aui.AuiPaneInfo = wx.aui.AuiPaneInfo()\
            .Dock()\
            .Center()\
            .MinSize((320, 240))\
            .BestSize((640, 480))\
            .CloseButton(False)\
            .Caption("Viewport")

        meta_pane: wx.aui.AuiPaneInfo = wx.aui.AuiPaneInfo()\
            .Dock()\
            .Right()\
            .MinSize((208, 80))\
            .MaxSize((208, 80))\
            .BestSize((208, 80))\
            .FloatingSize((208, 99))\
            .CloseButton(False)\
            .Caption("Metadata")

        palette_pane: wx.aui.AuiPaneInfo = wx.aui.AuiPaneInfo()\
            .Dock()\
            .Right()\
            .MinSize((208, 245))\
            .MaxSize((208, 245))\
            .BestSize((208, 245))\
            .FloatingSize((208, 263))\
            .CloseButton(False)\
            .Caption("Palette")

        palette_pane.dock_proportion = 1

        self.panes.append(meta_pane)
        self.panes.append(palette_pane)

        self.view_menu = wx.Menu()
        self.view_menu.Append(wx.ID_ZOOM_IN, "Zoom In\tCtrl++", "Zoom in")
        self.view_menu.Append(wx.ID_ZOOM_OUT, "Zoom Out\tCtrl+-", "Zoom out")
        self.view_menu.Append(wx.ID_ZOOM_100, "Actual Size\tCtrl+0", "Zoom to actual size")
        self.menubar.Append(self.view_menu, "&View")

        self.mgr.AddPane(
            window=self.view_panel,
            pane_info=view_pane
        )

        self.mgr.AddPane(
            window=self.meta_panel,
            pane_info=meta_pane
        )

        self.mgr.AddPane(
            window=self.palette_panel,
            pane_info=palette_pane
        )

        self.mgr.Update()

    def menu_handler(self, event: wx.CommandEvent):
        event_id = event.GetId()
        if event_id == wx.ID_EXIT:
            wx.Exit()

        # Zooming
        elif event_id == wx.ID_ZOOM_IN:
            self.view_panel.zoom_in()
        elif event_id == wx.ID_ZOOM_OUT:
            self.view_panel.zoom_out()
        elif event_id == wx.ID_ZOOM_100:
            self.view_panel.reset_zoom()

        # File handling
        elif event_id == wx.ID_OPEN:
            try:
                self.prompt_load_image()
            except UserCancelledException:
                pass
        elif event_id == wx.ID_SAVE:
            file_dialog: wx.FileDialog
            with wx.FileDialog(
                    parent=self,
                    message="Export .ipd file",
                    defaultFile=self.path.stem,
                    wildcard="PNG files (*.png)|*.png|"
                             "JPG files (*.jpg)|*.jpg|"
                             "BMP files (*.bmp)|*.bmp|"
                             "GIF files (*.gif)|*.gif",
                    style=wx.FD_SAVE
            ) as file_dialog:
                if file_dialog.ShowModal() != wx.ID_OK:
                    return

            file_format = (file_dialog.GetWildcard().split("|"))[1 + (file_dialog.GetFilterIndex() * 2)][2:]
            self.image.save(
                fp=file_dialog.GetPath(),
                format=file_format
            )

    def prompt_load_image(self):
        file_dialog: wx.FileDialog
        with wx.FileDialog(
                parent=self,
                message="Open .ipd file",
                wildcard="iPod game image files (*.ipd)|*.ipd",
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as file_dialog:
            if file_dialog.ShowModal() != wx.ID_OK:
                raise UserCancelledException("User cancelled")

            self.path = Path(file_dialog.GetPath())

        if self.load_image_from_ipd_path(self.path):
            self.apply_image()
            return True
        else:
            return False

    def load_image_from_ipd_path(self, path: Path, force_flip: bool = None):
        print(f"Loading from {path}, {force_flip=}")
        try:
            with open(path, "rb") as stream:
                self.header, self.image = from_stream(stream, force_flip=force_flip)
        except Exception as exception:
            exception_message = str(exception)

            if exception_message:
                message = f"{type(exception).__name__}: {exception_message}"
            else:
                message = f"{type(exception).__name__}"

            wx.MessageBox(
                message=message,
                caption="Couldn't load .ipd"
            )
            return False

        return True

    def apply_image(self, reset_selection: bool = True):
        rgba_image = self.image.convert("RGBA")
        bitmap = wx.Bitmap.FromBufferRGBA(
            width=rgba_image.width,
            height=rgba_image.height,
            data=rgba_image.tobytes()
        )
        self.view_panel.set_bitmap(bitmap)
        self.meta_panel.update(
            image=self.image,
            header=self.header,
            reset_selection=reset_selection
        )
        self.palette_panel.update(
            image=self.image,
            header=self.header
        )

    def override_select_callback(self, choice):
        if choice == 0:
            self.load_image_from_ipd_path(self.path, force_flip=None)
        elif choice == 1:
            self.load_image_from_ipd_path(self.path, force_flip=False)
        elif choice == 2:
            self.load_image_from_ipd_path(self.path, force_flip=True)

        self.apply_image(reset_selection=False)
        return choice
