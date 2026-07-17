import wx

#Each file should be made into some sort of clickable item that has information on the file directory for reference
#This can be used to edit the file on bulk or as singular file
#And can be used to export the data into music databases as a tracklist.

class DropTarget(wx.FileDropTarget):
    def __init__(self, obj, file_text):
        wx.FileDropTarget.__init__(self)
        self.obj = obj
        self.file_text: wx.StaticText = file_text

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            name = filename[filename.rfind("/")+1:filename.rfind(".")]
            self.file_text.SetLabel(f"{self.file_text.GetLabel()}\n{name}")

        return True

class HelloFrame(wx.Frame):
    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(HelloFrame, self).__init__(*args, **kw)

        # create a panel in the frame
        # pnl = wx.Panel(self)

        l_panel = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)

        l_panel_top = wx.Panel(l_panel, -1, style=wx.SUNKEN_BORDER)
        l_panel_bottom = wx.Panel(l_panel, -1, style=wx.SUNKEN_BORDER)

        r_panel = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)

        l_panel_top.SetBackgroundColour("LIGHT GREY")
        l_panel_bottom.SetBackgroundColour("GREY")
        r_panel.SetBackgroundColour("WHITE")


        drop_text = wx.StaticText(l_panel_top, label="Drop Files Here")
        style = drop_text.GetFont()
        drop_text.SetForegroundColour(wx.BLACK)
        style.PointSize += 8
        drop_text.SetFont(style)

        file_text = wx.StaticText(l_panel_bottom)
        file_text_style = file_text.GetFont()
        file_text.SetForegroundColour(wx.BLACK)
        file_text_style.PointSize += 2
        file_text.SetFont(file_text_style)

        text_sizer = wx.BoxSizer(wx.VERTICAL)
        text_sizer.AddStretchSpacer(1)
        text_sizer.Add(drop_text, 1, wx.ALIGN_CENTER_HORIZONTAL)
        text_sizer.AddStretchSpacer(1)
        l_panel_top.SetSizer(text_sizer)

        self.file_drop = DropTarget(l_panel_top, file_text)
        l_panel_top.SetDropTarget(self.file_drop)

        # put some text with a larger bold font on it
        # st = wx.StaticText(pnl, label="Hello World!")
        # font = st.GetFont()
        # font.PointSize += 10
        # font = font.Bold()
        # st.SetFont(font)

        l_sizer = wx.BoxSizer(wx.VERTICAL)
        l_sizer.Add(l_panel_top, 1, wx.EXPAND)
        l_sizer.Add(l_panel_bottom, 3, wx.EXPAND)
        l_panel.SetSizer(l_sizer)


        # and create a sizer to manage the layout of child widgets
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(l_panel, 1, wx.EXPAND)
        sizer.Add(r_panel, 2, wx.EXPAND)
        # sizer.Add(st, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))

        
        self.SetSize((600, 400))
        self.SetSizer(sizer)
        self.Layout()

        # create a menu bar
        self.makeMenuBar()


    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
                "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)


    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK|wx.ICON_INFORMATION)


if __name__ == '__main__':

    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = HelloFrame(None, title='Hello World 2')
    frm.Show()
    app.MainLoop()