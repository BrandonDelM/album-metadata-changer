import os
import wx
import math
import pyperclip
import wx.grid as gridlib
from tinytag import OtherFields, TinyTag
import unicodedata

#Each file should be made into some sort of clickable item that has information on the file directory for reference
#This can be used to edit the file on bulk or as singular file
#And can be used to export the data into music databases as a tracklist.

front_cover: bytes | None = None

class DropTarget(wx.FileDropTarget):
    def __init__(self, obj, track_grid, top_panel, info_grid):
        wx.FileDropTarget.__init__(self)
        self.obj = obj
        self.track_grid: gridlib.Grid = track_grid
        self.top_panel: wx.Panel = top_panel
        self.info_grid: gridlib.Grid = info_grid

    def OnDropFiles(self, x, y, filenames):
        global front_cover
        if self.track_grid.GetNumberRows() > 0:
            self.track_grid.DeleteRows(0, self.track_grid.GetNumberRows())
        for path in filenames:
            if os.path.isdir(path):
                contents = os.listdir(path)
                self.track_grid.InsertRows(pos=0, numRows=len(contents))
                
                tags: list[TinyTag] = [TinyTag.get(os.path.join(path, item),image=True) for item in contents if TinyTag.is_supported(os.path.join(path, item))]
                front_cover = tags[0].images.any.data
                if len(tags) <= 0:
                    return False
                disc_count: int = max([tag.disc or 1 for tag in tags]) #Get number of discs
                multi_disc: bool = True if disc_count > 1 else False #Checks if there are multiple discs
                discs: list[list[TinyTag]] = [sorted((tag for tag in tags if (tag.disc or 1) == disc_no), key=lambda tag: tag.track or float("inf")) for disc_no in range(1, disc_count+1)] #Separate tracks into discs
                
                row_i: int = 0 #Files in the folder aren't always going to be audio files..
                for disc_no, disc in enumerate(discs):
                    disc_prefix = f"{disc_no+1}." if multi_disc else "" 
                    for tag in disc:
                        track_no = tag.track or row_i
                        if tag.track == None:
                            print(f"row_i is given to file # {row_i}.")
                        artist_name = tag.artist or ""
                        track_title = tag.title or ""
                        duration = math.ceil(tag.duration)
                        duration = f"{int(duration // 60)}:{int(duration % 60):02d}"

                        print(artist_name, track_title, duration)

                        self.track_grid.SetCellValue(row_i, 0, f"{disc_prefix}{track_no}")
                        self.track_grid.SetCellValue(row_i, 1, str(artist_name))
                        self.track_grid.SetCellValue(row_i, 2, str(track_title))
                        self.track_grid.SetCellValue(row_i, 3, str(duration))

                        row_i += 1
                
                if row_i < len(contents):
                    self.track_grid.DeleteRows(row_i, len(contents) - row_i)
                self.get_credits(discs, multi_disc)
            else:
                print("WIP")
        self.track_grid.ForceRefresh()
        self.track_grid.AutoSize()
        self.top_panel.Layout()
        return True
    
    def get_credits(self, discs: list[list[TinyTag]], multi_disc: bool):
        if self.info_grid.GetNumberRows() > 0:
            self.info_grid.DeleteRows(0, self.info_grid.GetNumberRows())
        tracks: int = sum(len(disc) for disc in discs)
        self.info_grid.InsertRows(0, tracks)
        row_i: int = 0
        for disc_no, disc in enumerate(discs):
            disc_prefix = f"{disc_no+1}." if multi_disc else "" 
            for tag in disc:
                track_no = tag.track or row_i
                comment = tag.comment
                composer = tag.composer
                other_fields: OtherFields = tag.other
                catalog_no = other_fields.get("catalog_number")
                copyright = other_fields.get("copyright")
                lyricist = other_fields.get("lyricist")
                lyrics = other_fields.get("lyrics")
                publisher = other_fields.get("publisher")
                url = other_fields.get("url")
                if comment or composer or catalog_no or copyright or lyricist or lyrics or publisher or url:
                    self.info_grid.SetCellValue(row_i, 0, f"{disc_prefix}{track_no}")
                    self.info_grid.SetCellValue(row_i, 1, str(comment or ""))
                    self.info_grid.SetCellValue(row_i, 2, str(composer or ""))
                    self.info_grid.SetCellValue(row_i, 3, str(catalog_no or ""))
                    self.info_grid.SetCellValue(row_i, 4, str(copyright or ""))
                    self.info_grid.SetCellValue(row_i, 5, str(lyricist or ""))
                    self.info_grid.SetCellValue(row_i, 6, str(lyrics or ""))
                    self.info_grid.SetCellValue(row_i, 7, str(publisher or ""))
                    self.info_grid.SetCellValue(row_i, 8, str(url or ""))
                    row_i += 1
        if row_i < tracks:
            self.info_grid.DeleteRows(row_i, tracks - row_i)
        self.info_grid.AutoSizeColumns() 
        self.info_grid.AdjustScrollbars()
        self.info_grid.ForceRefresh()
        self.top_panel.Layout()
        return True

class HelloFrame(wx.Frame):

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(HelloFrame, self).__init__(*args, **kw)

        # Left Panel

        l_panel = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)
        l_panel_top = wx.Panel(l_panel, -1, style=wx.SUNKEN_BORDER)
        l_panel_bottom = wx.Panel(l_panel, -1, style=wx.SUNKEN_BORDER)

        #Left top
        drop_text = wx.StaticText(l_panel_top, label="Drop Files Here")
        style = drop_text.GetFont()
        # drop_text.SetForegroundColour(wx.BLACK)
        style.PointSize += 8
        drop_text.SetFont(style)

        #Left bottom
        info_text = wx.StaticText(l_panel_bottom)
        info_text_style = info_text.GetFont()
        info_text_style.PointSize += 2
        info_text.SetFont(info_text_style)
        info_text.SetLabelText("Info Text")

        self.infoGrid = gridlib.Grid(l_panel_bottom)
        self.infoGrid.CreateGrid(numRows=0, numCols=9)
        self.infoGrid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.infoGrid.SetColLabelValue(0, "#")
        self.infoGrid.SetColLabelValue(1, "Comment")
        self.infoGrid.SetColLabelValue(2, "Composer")
        self.infoGrid.SetColLabelValue(3, "Catalog #")
        self.infoGrid.SetColLabelValue(4, "Copyright")
        self.infoGrid.SetColLabelValue(5, "Lyricist")
        self.infoGrid.SetColLabelValue(6, "Lyrics")
        self.infoGrid.SetColLabelValue(7, "Publisher")
        self.infoGrid.SetColLabelValue(8, "URL")

        self.infoGrid.DisableDragColSize()
        self.infoGrid.DisableDragRowSize()
        self.infoGrid.DisableDragGridSize()
        self.infoGrid.SetDefaultCellOverflow(False)
        self.infoGrid.SetMinSize((250, 150))

        #Right panel

        r_panel = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)
        r_panel_top = wx.Panel(r_panel, -1, style=wx.SUNKEN_BORDER)
        r_panel_bottom = wx.Panel(r_panel, -1, style=wx.SUNKEN_BORDER)

        #Right grid
        self.trackGrid = gridlib.Grid(r_panel_top)
        self.trackGrid.CreateGrid(numRows=0, numCols=4)
        self.trackGrid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.trackGrid.SetColLabelValue(0, "#")
        self.trackGrid.SetColLabelValue(1, "Artist")
        self.trackGrid.SetColLabelValue(2, "Track Title")
        self.trackGrid.SetColLabelValue(3, "Duration")
        self.trackGrid.InsertRows()

        #Preview Button
        self.preview_button = wx.Button(r_panel_top, -1, "Preview")
        self.preview_button.Bind(wx.EVT_BUTTON, self.preview_button_click)

        #Preview Grid
        self.previewGrid = gridlib.Grid(r_panel_top)
        self.previewGrid.CreateGrid(numRows=0, numCols=3)
        self.previewGrid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.previewGrid.SetColLabelValue(0, "#")
        self.previewGrid.SetColLabelValue(1, "Track Name")
        self.previewGrid.SetColLabelValue(2, "Time")
        self.previewGrid.InsertRows()

        #Right panel grid settings
        #Artist Name
        self.enable_artist = wx.CheckBox(r_panel_bottom, -1, 'Add Artists To Tracklist')

        #Normalize Unicode
        self.normalize_unicode = wx.CheckBox(r_panel_bottom, -1, 'Normalize Unicode')
        self.normalize_unicode.SetOwnForegroundColour(wx.BLACK)

        #Title Case
        self.title_case = wx.CheckBox(r_panel_bottom, -1, "Title Case")
        self.normalize_unicode.SetOwnForegroundColour(wx.BLACK)

        #Download Cover
        self.dl_cover_button = wx.Button(r_panel_bottom, -1, "Download Cover")
        self.dl_cover_button.Bind(wx.EVT_BUTTON, self.dl_cover_button_click)
        self.dl_cover_button.SetOwnForegroundColour(wx.BLACK)

        #Export
        self.export_button = wx.Button(r_panel_bottom, -1, 'Export Tracklist')
        self.export_button.Bind(wx.EVT_BUTTON, self.export_button_click)

        #Styling

        # l_panel_top.SetBackgroundColour("BLACK")
        # l_panel_bottom.SetBackgroundColour("GREY")
        # r_panel.SetBackgroundColour("WHITE")
        # r_panel_top.SetBackgroundColour("WHITE")
        # r_panel_bottom.SetBackgroundColour("LIGHT GREY")

        text_sizer = wx.BoxSizer(wx.VERTICAL)
        text_sizer.AddStretchSpacer(1)
        text_sizer.Add(drop_text, 1, wx.ALIGN_CENTER_HORIZONTAL)
        text_sizer.AddStretchSpacer(1)
        l_panel_top.SetSizer(text_sizer)

        #File drop
        self.file_drop = DropTarget(l_panel_top, self.trackGrid, r_panel_top, self.infoGrid)
        l_panel_top.SetDropTarget(self.file_drop)

        l_sizer = wx.BoxSizer(wx.VERTICAL)
        l_sizer.Add(l_panel_top, 1, wx.EXPAND)
        l_sizer.Add(l_panel_bottom, 4, wx.EXPAND)
        l_panel.SetSizer(l_sizer)

        #l_sizer_bottom
        l_sizer_bottom = wx.BoxSizer(wx.VERTICAL)
        l_sizer_bottom.Add(info_text, 0, wx.CENTER)
        l_sizer_bottom.Add(self.infoGrid, 1, wx.EXPAND | wx.ALL, border=2)
        l_panel_bottom.SetSizer(l_sizer_bottom)

        #r_sizer_top
        r_sizer_top = wx.BoxSizer(wx.VERTICAL)
        r_sizer_top.Add(self.trackGrid, 1, wx.EXPAND)
        r_sizer_top.Add(self.preview_button, 0, wx.ALL | wx.CENTER, border=5)
        r_sizer_top.Add(self.previewGrid, 1, wx.EXPAND)
        r_panel_top.SetSizer(r_sizer_top)

        #r_sizer_bottom
        r_sizer_bottom = wx.BoxSizer(wx.VERTICAL)
        r_sizer_bottom.Add(self.enable_artist, 0, wx.ALL | wx.ALIGN_LEFT, border=2)
        r_sizer_bottom.Add(self.normalize_unicode, 0, wx.ALL | wx.ALIGN_LEFT, border=2)
        r_sizer_bottom.Add(self.title_case, 0, wx.ALL | wx.ALIGN_LEFT, border=2)
        r_sizer_bottom.Add(self.dl_cover_button, 0, wx.ALL | wx.EXPAND, border=2)
        r_sizer_bottom.Add(self.export_button, 0, wx.ALL | wx.EXPAND, border=2)
        r_panel_bottom.SetSizer(r_sizer_bottom)

        r_sizer = wx.BoxSizer(wx.VERTICAL)
        r_sizer.Add(r_panel_top, 2, wx.EXPAND)
        r_sizer.Add(r_panel_bottom, 1, wx.EXPAND)
        r_panel.SetSizer(r_sizer)

        # and create a sizer to manage the layout of child widgets
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(l_panel, 1, wx.EXPAND)
        sizer.Add(r_panel, 2, wx.EXPAND)
        # sizer.Add(st, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))

        
        self.SetSize((900, 900))
        self.Center()
        self.SetSizer(sizer)
        # self.SetSizerAndFit(sizer)
        self.Layout()
        self.Refresh()

        # create a menu bar
        self.makeMenuBar()

    def export_button_click(self, event):
        rows: int = self.trackGrid.GetNumberRows()
        tracklist: str = ""
        if self.enable_artist.IsChecked(): #Artist not enabled
            for row in range(rows):
                tracklist += f"{self.trackGrid.GetCellValue(row, 0)}|{self.trackGrid.GetCellValue(row, 1)} - {unicodedata.normalize('NFKC', self.trackGrid.GetCellValue(row, 2)) if self.normalize_unicode.IsChecked() else self.trackGrid.GetCellValue(row, 2)}|{self.trackGrid.GetCellValue(row, 3)}\n"
        else: #Artist enabled
            for row in range(rows):
                tracklist += f"{self.trackGrid.GetCellValue(row, 0)}|{unicodedata.normalize('NFKC', self.trackGrid.GetCellValue(row, 2)) if self.normalize_unicode.IsChecked() else self.trackGrid.GetCellValue(row, 2)}|{self.trackGrid.GetCellValue(row, 3)}\n"
        pyperclip.copy(tracklist)
    
    def preview_button_click(self, event):
        rows: int = self.trackGrid.GetNumberRows()
        if rows <= 0:
            wx.MessageBox("No tracklist to export (Tracklist is blank)", "Error", wx.ICON_ERROR)
            return False
        if self.previewGrid.GetNumberRows() > 0:
            self.previewGrid.DeleteRows(0, self.trackGrid.GetNumberRows())
        self.previewGrid.InsertRows(pos=0, numRows=rows)
        for row in range(rows):
            track_no = self.trackGrid.GetCellValue(row, 0)
            artist_name = f"{self.trackGrid.GetCellValue(row, 1)} - " if self.enable_artist.IsChecked() else ''
            track_title = unicodedata.normalize('NFKC', self.trackGrid.GetCellValue(row, 2)) if self.normalize_unicode.IsChecked() else self.trackGrid.GetCellValue(row, 2)
            duration = self.trackGrid.GetCellValue(row, 3)
            if self.title_case.IsChecked():
                track_title = track_title.title()
            
            self.previewGrid.SetCellValue(row, 0, f"{track_no}")
            self.previewGrid.SetCellValue(row, 1, f"{artist_name}{track_title}")
            self.previewGrid.SetCellValue(row, 2, str(duration))
        self.previewGrid.AutoSize()
        self.previewGrid.ForceRefresh()
        return True

    def dl_cover_button_click(self, event):
        if front_cover:
            try:
                downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                with open(os.path.join(downloads, 'cover.png'), 'wb') as img_file:
                    img_file.write(front_cover)
                wx.MessageBox("Image successfully downloaded to Downloads folder", "Success", wx.OK)
            except Exception as e:
                wx.MessageBox(f"Error while trying to download image: {e}", "Downloading Error", wx.ICON_ERROR)
        else:
            wx.MessageBox("No cover could be found for this release", "Error", wx.ICON_ERROR)
            print("No image to download")
    
    def track_capitalization(self):
        pass

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
    frm = HelloFrame(None, title='Album Tracklist Exporter')
    frm.Show()
    app.MainLoop()