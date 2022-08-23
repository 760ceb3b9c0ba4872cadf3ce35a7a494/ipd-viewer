import wx
from viewer import RootFrame
from viewer.utils import UserCancelledException


def run():
    app = wx.App()
    frame = RootFrame()
    while True:
        try:
            if frame.prompt_load_image():
                break
        except UserCancelledException:
            return
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    run()
