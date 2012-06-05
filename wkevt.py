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

    # def BeginDrag(self, pos, pt):
    #     self.hotspot = pos - self.rect.GetPosition()

    # def EndDrag(self):
    #     pt = self._winLoc - self.hotspot
    #     # pt.x = self.editor.Snap(pt.x, self.editor.controller._settings.ide_sizeToGrid)
    #     # pt.y = self.editor.Snap(pt.y, self.editor.controller._settings.ide_sizeToGrid)

    #     # self.MoveWin(pt)        
    #     print 'NSB.fe.setCanvasRect("{0}", {1})'.format(self.element_id, list(pt) + list(self.rect.GetSize()))
    #     print self.webview.RunScript('NSB.fe.setCanvasRect("{0}", {1})'.format(self.element_id, list(pt) + list(self.rect.GetSize())))

    def EndResize(self):
        self._resizing = False
        self._rect = self._win.GetRect()
        print('EndResize:{0!r}'.format(self._rect))
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

    def Move(self, delta):
        pos = self.rect.GetPosition() + delta
        size = self.rect.GetSize()
        bounds = self.webview.GetSize()

        # Normalize adjusted position and size
        pos.x = min(max(0, pos.x), bounds.x - size.x)
        pos.y = min(max(0, pos.y), bounds.y - size.y)
        self.rect.SetTopLeft(pos)

        print 'NSB.fe.setCanvasRect("{0}", {1})'.format(self.element_id, list(self.rect))
        print self.webview.RunScript('NSB.fe.setCanvasRect("{0}", {1})'.format(self.element_id, list(self.rect)))

    def Resize(self, delta, grab):
        l, t, w, h = self.rect
        r, b = l + w, t + h
        bounds = self.webview.GetSize()

        # Normalize adjusted position and size
        min_size = 5
        if   grab in [1, 7, 8]:
            l = min(max(0, l + delta.x), r - min_size)
        elif grab in [3, 4, 5]:
            r = min(max(l + min_size, r + delta.x), bounds.x)
        if   grab in [1, 2, 3]:
            t = min(max(0, t + delta.y), b - min_size)
        elif grab in [5, 6, 7]:
            b = min(max(t + min_size, b + delta.y), bounds.y)
        self.rect.Set(l, t, r - l, b - t)

        print 'NSB.fe.setCanvasRect("{0}", {1})'.format(self.element_id, list(self.rect))
        print self.webview.RunScript('NSB.fe.setCanvasRect("{0}", {1})'.format(self.element_id, list(self.rect)))


class TestFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, pos=(150, 150), size=(600, 400))
        self.x, self.y = 10, 10
        size = wx.Size(480, 320)
        self.pt = None
        self._dragging = False
        self._resizing = False
        self._selection = {}    # A dict of Selector objects, keyed by widget_id as str

        panel = wx.Panel(self)

        self.ScreenPnl = wv.WebView(name='ScreenPnl', parent=panel, point=wx.Point(8, 8),
              size=size, style=wx.RAISED_BORDER | wx.TAB_TRAVERSAL)
        self.ScreenPnl.SetClientSize(size)
        self.ScreenPnl.SetMinSize(self.ScreenPnl.GetSize())
        self.ScreenPnl.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        self.ScreenPnl.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.ScreenPnl.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.ScreenPnl.Bind(wx.EVT_MOTION, self.OnMotion)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddWindow(self.ScreenPnl, 0, flag=wx.ALL, border=5)
        panel.SetSizer(sizer)
        panel.Layout()

        self.bitmap = None
        self.map = None
        self.ScreenPnl.LoadURL('file://'+os.path.join(os.getcwd(), 'wkevt.html'))
        # self.ScreenPnl.LoadURL('http://www.ebay.com')

    def BeginDrag(self, pos):
        self._dragging = True
        self.SetCursor_(pos)

    def BeginResize(self, pos):
        self._resizing = True
        # self.SetCursor_(pos)

    def Deselect(self, widget_id=None, notify_controller=True):
        if widget_id:   # Deselect One
            del self._selection[widget_id]
        else:           # Deselect All
            self._selection.clear()

        # if notify_controller:
        #     # TODO: this should be somewhere else - another method - perhaps a wrapper
        #     self.controller.Select(self.source, [self._form])
        print 'self.ScreenPnl.RunScript', 'select({0})'.format(json.dumps(self._selection.keys()))
        print 'selected', self.ScreenPnl.RunScript('NSB.fe.select({0})'.format(json.dumps(self._selection.keys())))

    def Drag(self, pos):
        delta = pos - self.pt
        if not self._dragging:
            tolerance = 2
            if abs(delta.x) <= tolerance and abs(delta.y) <= tolerance:
                return
            self.BeginDrag(pos)

        self.MoveSelection(delta)
        self.pt = pos

    def EndDrag(self):
        # MMD: Should the snap code be moved into MoveSelection?
        #     # left = self.Snap(left, self.controller._settings.ide_sizeToGrid)
        #     # top = self.Snap(top, self.controller._settings.ide_sizeToGrid)
        #     # self.controller.SetProperty(self.source, [ss], 'left', left)
        #     # self.controller.SetProperty(self.source, [ss], 'top', top)

        # # self.Show_(self._selection.keys())
        self._dragging = False

    def EndResize(self):
        self._resizing = False
        # self.controller.SetProperty(self.source, [widget], prop, value)
        # self.Show_([widget])

    def HitTest(self, pos):
        if not self.map:
            self.map = json.loads(self.ScreenPnl.RunScript('NSB.fe.map'))

        for widget_id, widget_rect in self.map.iteritems():
            if wx.Rect(*widget_rect).Contains(pos):
                return widget_id
        return None

    def MoveSelection(self, delta):
        for ss in self._selection.itervalues():
            ss.Move(delta)

    def OnLeftDown(self, event):
        self.ScreenPnl.CaptureMouse()
        self.pt = pos = event.GetPosition()
        widget_id = self.HitTest(pos)
        print 'OnLeftDown -- HitTest', widget_id

        if widget_id:  # new version for selection and multi-selection
            self.Select(widget_id, event.ControlDown())
            print 'self._selection', self._selection.values()
            # self.controller.Select(self.source, self._selection.keys())
        else:
            self.Deselect()

        # event.Skip()

    def OnLeftUp(self, event):
        if self._dragging:
            self.EndDrag()
        if self._resizing:
            self.EndResize()
        self.ScreenPnl.ReleaseMouse()

    def OnMotion(self, event):
        if not event.Dragging():
            self.SetCursor_(event.GetPosition())
        if event.LeftIsDown() and event.Dragging():
            pos = event.GetPosition()
            if self.grab == 0:
                self.Drag(pos)
            else:
                self.Resize(pos)

    def Resize(self, pos):
        delta = pos - self.pt
        if not self._resizing:
            tolerance = 2
            if ((self.grab in [1, 3, 4, 5, 7, 8] and abs(delta.x) <= tolerance)
                or
                (self.grab in [1, 2, 3, 5, 6, 7] and abs(delta.y) <= tolerance)):
                return
            self.BeginResize(pos)

        # Line could be replaced by a ResizeSelection, similar to MoveSelection
        self._selection.values()[0].Resize(delta, self.grab)
        self.pt = pos

    def Select(self, widget_id, add_to_selection=False):
        self.grab = 0
        if add_to_selection:
            if widget_id in self._selection:
                # Deselect a selected item
                self.Deselect(widget_id)
                return
        else:
            if not widget_id in self._selection:
                # Deselect anything irrelevant
                self.Deselect(notify_controller=False)
            else:
                return
        self._selection[widget_id] = Selector(self.ScreenPnl, widget_id, self.map[widget_id])
        print 'self.ScreenPnl.RunScript', 'select({0})'.format(json.dumps(self._selection.keys()))
        print 'selected', self.ScreenPnl.RunScript('NSB.fe.select({0})'.format(json.dumps(self._selection.keys())))

    def SetCursor_(self, pos):
        for sel in self._selection.itervalues():
            self.grab, cursor = sel.GetCursor(pos, len(self._selection) == 1)
            if cursor is not None:
                self.ScreenPnl.SetCursor(wx.StockCursor(cursor))
                return
        else:
            self.ScreenPnl.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))


class TestApp(wx.App):
    def OnInit(self):
        frame = TestFrame(None, 'WebKit Event Tester')
        frame.Show()
        return True

app = TestApp()
app.MainLoop()
