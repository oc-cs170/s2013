import os
import wx
import json
import urllib

try:
    import wx.webview as wv
except ImportError:
    import wx.webkit as wv

    class WebView(wv.WebKitCtrl):
        def __init__(self, parent, id=wx.ID_ANY, point=wx.DefaultPosition, 
                     size=wx.DefaultSize, style=0, **kwargs):
            wv.WebKitCtrl.__init__(self, parent, winID=id, pos=point,
                                   size=size, style=style, **kwargs)

            size = size[0] - 100, size[1]
            self._skin = wx.Window(parent, pos=point, size=size)

        def Bind(self, *args, **kwargs):
            self._skin.Bind(*args, **kwargs)

        def SetCursor(self, cursor):
            self._skin.SetCursor(cursor)

        def CaptureMouse(self):
            self._skin.CaptureMouse()

        def ReleaseMouse(self):
            self._skin.ReleaseMouse()

    wv.WebView = WebView


class Selector(wx.Object):
    def __init__(self, webview, element_id, rect):
        self.webview = webview
        self.element_id = element_id
        self.rect = wx.Rect(*rect)
        self.hotspot = None

    def __repr__(self):
        return str((self.element_id, self.rect))

    def BeginDrag(self, pos, pt):
        self.hotspot = pos - self.rect.GetPosition()

    def EndDrag(self):
        pt = self._winLoc - self.hotspot
        # pt.x = self.editor.Snap(pt.x, self.editor.controller._settings.ide_sizeToGrid)
        # pt.y = self.editor.Snap(pt.y, self.editor.controller._settings.ide_sizeToGrid)

        # self.MoveWin(pt)        
        print 'NSB.fe.setCanvasRect("{0}", {1})'.format(self.element_id, list(pt) + list(self.rect.GetSize()))
        print self.webview.RunScript('NSB.fe.setCanvasRect("{0}", {1})'.format(self.element_id, list(pt) + list(self.rect.GetSize())))

        # self._win.Show()
        # self._dragImage = None

    def EndResize(self):
        self._resizing = False
        self._rect = self._win.GetRect()
        _log.debug('EndResize:{0!r}'.format(self._rect))
        if self.grab in [1, 2, 3, 5, 6, 7]:
            height = self.editor.Snap(self._rect.height - 2 - self.info.obj._offsetY, self.editor.controller._settings.ide_sizeToGrid)
            self._rect.Height = height + 2 + self.info.obj._offsetY
            self.editor.EndResize(self.info, 'height', height)
        if self.grab in [1, 3, 4, 5, 7, 8]:
            width = self.editor.Snap(self._rect.width - 2 - self.info.obj._offsetX, self.editor.controller._settings.ide_sizeToGrid)
            self._rect.Width = width + 2 + self.info.obj._offsetX
            self.editor.EndResize(self.info, 'width', width)
        if self.grab in [1, 2, 3]:
            top = self.editor.Snap(self._rect.top + 1, self.editor.controller._settings.ide_sizeToGrid)
            self._rect.Top = top - 1
            self.editor.EndResize(self.info, 'top', top)
        if self.grab in [1, 7, 8]:
            left = self.editor.Snap(self._rect.left + 1, self.editor.controller._settings.ide_sizeToGrid)
            self._rect.Left = left - 1
            self.editor.EndResize(self.info, 'left', left)
        self._win.SetRect(self._rect)
            
    def GetCursor(self, pos, can_resize):
        # Returns the Grab Handle index (0-8) and the stock cursor to use
        if not self.rect.Contains(pos):
            return None, None
        if not can_resize:
            return 0, wx.CURSOR_HAND
        pt = pos - self.rect.GetPosition()
        width, height = self.rect.GetSize()
        margin = 5
        # Key: (Left margin, Right margin, Top margin, Bottom margin)
        # Grab handles start in top/left at 1, increasing clockwise, 0 for none
        grab_cursor = {(False, False, False, False):    (0, wx.CURSOR_HAND),
                       (True, False, True, False):      (1, wx.CURSOR_SIZENWSE),
                       (False, False, True, False):     (2, wx.CURSOR_SIZENS),
                       (False, True, True, False):      (3, wx.CURSOR_SIZENESW),
                       (False, True, False, False):     (4, wx.CURSOR_SIZEWE),
                       (False, True, False, True):      (5, wx.CURSOR_SIZENWSE),
                       (False, False, False, True):     (6, wx.CURSOR_SIZENS),
                       (True, False, False, True):      (7, wx.CURSOR_SIZENESW),
                       (True, False, False, False):     (8, wx.CURSOR_SIZEWE)}
        grab, cursor = grab_cursor[(pt.x < margin, pt.x >= width - margin,
                                    pt.y < margin, pt.y >= height - margin)]
        return grab, cursor

    def GetPosition(self):
        return self.rect.GetPosition()

    def Move(self, pt):
        if pt.x - self.hotspot.x < 0:
            pt.x = self.hotspot.x
        if pt.y - self.hotspot.y < 0:
            pt.y = self.hotspot.y
        if pt.x + (self.rect.GetWidth() - self.hotspot.x)  > self.webview.GetSize().x - 6:
            pt.x = self.webview.GetSize().x - 6 - (self.rect.GetWidth() - self.hotspot.x) + 1
        if pt.y + (self.rect.GetSize().y - self.hotspot.y) > self.webview.GetSize().y - 6:
            pt.y = self.webview.GetSize().y - 6 - (self.webview.GetSize().y - self.hotspot.y) + 1
        print 'NSB.fe.setCanvasRect("{0}", {1})'.format(self.element_id, list(pt) + list(self.rect.GetSize()))
        print self.webview.RunScript('NSB.fe.setCanvasRect("{0}", {1})'.format(self.element_id, list(pt) + list(self.rect.GetSize())))
        self._winLoc = pt


class TestFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, pos=(150, 150), size=(600, 400))
        self.x, self.y = 10, 10
        size = wx.Size(480, 320)
        self.pt = None
        self._dragging = False
        self._resizing = False
        self._selector = None

        panel = wx.Panel(self)

        self.ScreenPnl = wv.WebView(name='ScreenPnl', parent=panel, point=wx.Point(8, 8),
              size=size, style=wx.RAISED_BORDER | wx.TAB_TRAVERSAL)
        self.ScreenPnl.SetClientSize(size)
        self.ScreenPnl.SetMinSize(self.ScreenPnl.GetSize())
        self.ScreenPnl.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        self.ScreenPnl.Bind(wx.EVT_LEFT_DOWN, self.OnSbmLeftDown)
        self.ScreenPnl.Bind(wx.EVT_LEFT_UP, self.OnSbmLeftUp)
        # self.ScreenPnl.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        # self.ScreenPnl.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        # self.ScreenPnl.Bind(wx.EVT_LEFT_DCLICK, self.OnDblClick)

        # self.sbm = wx.Window(panel, pos=(5, 5), size=(300, 300), style=wx.TRANSPARENT_WINDOW)

        # # self.sbm.Bind(wx.EVT_PAINT, self.OnSbmPaint)
        # self.sbm.Bind(wx.EVT_LEFT_DOWN, self.OnSbmLeftDown)
        self.ScreenPnl.Bind(wx.EVT_MOTION, self.OnSbmMotion)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddWindow(self.ScreenPnl, 0, flag=wx.ALL, border=5)
        panel.SetSizer(sizer)
        panel.Layout()

        self.bitmap = None
        # print 'loading:', self.ScreenPnl.RunScript('document.readyState')
        self.map = None
        self.ScreenPnl.LoadURL('file://'+os.path.join(os.getcwd(), 'wkevt.html'))
        # self.ScreenPnl.LoadURL('http://www.ebay.com')
        # print 'loading:', self.ScreenPnl.RunScript('document.readyState')
        # print 'map:', self.ScreenPnl.RunScript('NSB.fe.getMap()')

        self._selection = {}

    def BeginDrag(self, pos, pt):
        self._dragging = True
        for ss in self._selection.itervalues():
            ss.BeginDrag(pos, pt)

    def BeginResize(self):
        pass
        
    def DeselectAll(self, widget_id=None, notify_controller=True):
        # self.Refresh()
        for ww, ss in self._selection.items():
            if not widget_id or widget_id is not ww:
                # ss.Destroy()
                del self._selection[ww]
        # _log.debug('DeselectAll ' + str(self._selection))

        # if notify_controller:
        #     # TODO: this should be somewhere else - another method - perhaps a wrapper
        #     self.controller.Select(self.source, [self._form])
        self.ScreenPnl.RunScript('NSB.fe.select([])')

    def EndDrag(self, pos):
        for ww, ss in self._selection.iteritems():
            # reposition and draw the widgets
            print ('Left: {0}, PosX: {1}, PtX: {2}'.format(ss.rect.GetLeft(), pos.x, self.pt.x))
            # don't allow widgets to get dragged off screenpnl
            left = ss.rect.GetLeft() + pos.x - self.pt.x
            top = ss.rect.GetTop() + pos.y - self.pt.y
            if left < 0:
                left = 0
            if top < 0:
                top = 0
            if (left + ss.rect.GetWidth()) > (self.ScreenPnl.Size.x - 6):
                left = (self.ScreenPnl.Size.x - 6) - ss.rect.GetWidth() - 1
            if (top + ss.rect.GetHeight()) > (self.ScreenPnl.Size.y - 6):
                top = (self.ScreenPnl.Size.y - 6) - ss.rect.GetHeight() - 1
            # left = self.Snap(left, self.controller._settings.ide_sizeToGrid)
            # top = self.Snap(top, self.controller._settings.ide_sizeToGrid)
            # self.controller.SetProperty(self.source, [ss], 'left', left)
            # self.controller.SetProperty(self.source, [ss], 'top', top)

        # self.Show_(self._selection.keys())

        for ss in self._selection.itervalues():
            ss.EndDrag()

        # self.Refresh()
        self._dragging = False

    def EndResize(self, widget, prop, value):
        self._resizing = False
        # self.Refresh()
        # self.controller.SetProperty(self.source, [widget], prop, value)
        # self.Show_([widget])

    def HitTest(self, pos):
        if not self.map:
            self.map = json.loads(self.ScreenPnl.RunScript('NSB.fe.map'))

        for widget_id, widget_rect in self.map.iteritems():
            if wx.Rect(*widget_rect).Contains(pos):
                return widget_id
        return None

    def MoveSelection(self, pt):
        for ss in self._selection.itervalues():
            ss.Move(pt)

    def OnRightDown(self, event):
        print 'OnRightDown',
        pos = event.GetPosition()
        print pos
        self.OnLeftDown(event)
        # self.OnContextMenu(selector=bool(len(self._selection)), pos=pos)

    def OnRightUp(self, event):
        print 'OnRightUp'

    def EraseBackground(self, event):
        #print 'EraseBackground'
        if self.bitmap:
            dc = event.GetDC()
            pdc = wx.MemoryDC(self.bitmap)
            dc.Clear()
            dc.Blit(100, 100, self.bitmap.GetWidth(), self.bitmap.GetHeight(), pdc, 0, 0)

    def OnClose(self, event):
        self.Close()

    def OnSbmLeftDown(self, event):
        self.ScreenPnl.CaptureMouse()
        self.pt = pos = event.GetPosition()
        widget_id = self.HitTest(pos)
        print 'OnSbmLeftDown -- HitTest', widget_id

        if widget_id:  # new version for selection and multi-selection
            self.Select(widget_id, event.ControlDown())
            print 'self._selection', self._selection.values()
            if widget_id in self._selection:
                widget_rect = self._selection[widget_id].rect
                self._selection[widget_id].pt = wx.Point(pos.x - widget_rect[0], pos.y - widget_rect[1])
                # event.m_x = pt.x
                # event.m_y = pt.y
                # self._selection[widget].OnLeftDown(event)
            # _log.debug('Selecting... ' + str(self._selection.keys()))
            # self.controller.Select(self.source, self._selection.keys())
        else:
            self.DeselectAll()

        # event.Skip()

    def OnSbmLeftUp(self, event):
        # print('sbm left up')
        if self._dragging:
            self.EndDrag(event.GetPosition())
        if self._resizing:
            self.EndResize()
        self.ScreenPnl.ReleaseMouse()

    def OnSbmMotion(self, event):
        if not event.Dragging():
            self.SetCursor_(event.GetPosition())
        if event.LeftIsDown() and event.Dragging():
            print 'Left Drag, grab:', self.grab
            pt = event.GetPosition()
            if self.grab == 0:   # Drag
                topleft = self._selector.GetPosition()
                if not self._dragging:
                    tolerance = 2
                    dx = abs(pt.x - self.pt.x)
                    dy = abs(pt.y - self.pt.y)
                    if dx <= tolerance and dy <= tolerance:
                        return

                    pos = self.pt + topleft
                    self.BeginDrag(pos, pt)# + topleft)
                else:
                    self.MoveSelection(pt)# + topleft)
            else:               # Resize
                if not self._resizing:
                    tolerance = 2
                    dx = abs(pt.x - self.pt.x)
                    dy = abs(pt.y - self.pt.y)
                    if ((self.grab in [1, 3, 4, 5, 7, 8] and dx <= tolerance)
                        or
                        (self.grab in [1, 2, 3, 5, 6, 7] and dy <= tolerance)):
                        return

                    self.BeginResize()
                else:
                    self.Resize(pt)

    def OnSbmPaint(self, event):        
        pdc = wx.PaintDC(self.sbm)
        try:
            dc = wx.GCDC(pdc)
        except:
            dc = pdc
        rect = wx.Rect(self.x, self.y, 50, 50)
        r, g, b = (178, 34, 34)
        penclr = wx.Colour(r, g, b, 255)
        brushclr = wx.Colour(r, g, b, 128)
        dc.SetPen(wx.Pen(penclr))
        dc.SetBrush(wx.Brush(brushclr))
        dc.DrawRoundedRectangleRect(rect, 8)

    def Select(self, widget_id, add_to_selection=False):
        self.grab = 0
        if add_to_selection:
            # Add or subtract item from selection
            if widget_id in self._selection:
                # Subtract
                del self._selection[widget_id]
                # if len(self._selection):
                #     self._selector = self._selection.values()[0]
                # else:
                self._selector = None
                return
        else:
            if not widget_id in self._selection:
                # Deselect anything irrelevant
                self.DeselectAll(notify_controller=False)
            else:
                self._selector = self._selection[widget_id]
                return
        self._selection[widget_id] = self._selector = Selector(self.ScreenPnl, widget_id, self.map[widget_id])
        print 'self.ScreenPnl.RunScript', 'select({0})'.format(json.dumps(self._selection.keys()))
        print 'selected', self.ScreenPnl.RunScript('NSB.fe.select({0})'.format(json.dumps(self._selection.keys())))

    def Resize(self, pt):
        pass

    def SetCursor_(self, pos):
        print 'Setting cursor...'
        for sel in self._selection.itervalues():
            self.grab, cursor = sel.GetCursor(pos, len(self._selection) == 1)
            if cursor is not None:
                self.ScreenPnl.SetCursor(wx.StockCursor(cursor))
                self._selector = sel
                return
        else:
            self.ScreenPnl.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            self._selector = None


class TestApp(wx.App):
    def OnInit(self):
        frame = TestFrame(None, 'WebKit Event Tester')
        frame.Show()
        return True

app = TestApp()
app.MainLoop()
