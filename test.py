# Source - https://stackoverflow.com/a/52102012
# Posted by Rolf of Saxony
# Retrieved 2026-07-13, License - CC BY-SA 4.0

import wx

class DropTarget(wx.FileDropTarget):
    def __init__(self, obj):
        wx.FileDropTarget.__init__(self)
        self.obj = obj

    def OnDropFiles(self, x, y, filenames):
        print("Drop Event",filenames)

#        image = Image.open(filenames[0])
#        image.thumbnail((PhotoMaxSize, PhotoMaxSize))
#        image.save('new.png')
#        pub.sendMessage('dnd', filepath='new.png')
        return True

class MyFrame(wx.Frame):
    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, ID, title, size=(300, 340))


        panel1 = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)
        panel2 = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)

        panel1.SetBackgroundColour("BLUE")
        panel2.SetBackgroundColour("RED")

        image_file = 'bgimage1.jpg'
        bmp1 = wx.Image(image_file,wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap1 = wx.StaticBitmap(panel1, -1, bmp1, (0, 0))

        # button
        closeButton = wx.Button(panel2, -1, label='Generate',pos=(30, 280))
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

        clearButton = wx.Button(panel2, -1, label='Clear',pos=(170, 280))
        clearButton.Bind(wx.EVT_BUTTON, self.OnClose)

        self.file_drop_target = DropTarget(self)
        self.SetDropTarget(self.file_drop_target)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(panel1, 0, wx.EXPAND,0)
        box.Add(panel2, 0, wx.EXPAND,0)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

    def OnClose(self, e):
        self.Close(True)

app = wx.App()
frame = MyFrame(None, -1, "Sizer Test")
frame.Show()
app.MainLoop()
