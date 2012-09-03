var NSB = NSB || {};
NSB.fe = {
    _canvas_prefix: 'NSB:canvas:',
    _map: {},
    _selection: [],

    get 
    map() { return JSON.stringify(this._map); },

    createCanvas: function(element_name, rect, color) {
        var canvas = document.createElement('canvas');
        canvas.id = NSB.fe._canvas_prefix+element_name;
        canvas.className = 'canvasSelector canvas'+color;
        NSB.fe._selection[element_name] = canvas;
        document.body.appendChild(canvas);
        NSB.fe.setCanvasRect(element_name, rect);
        return canvas;
    },

    getElementRect: function(element) {
        return [element.offsetLeft, element.offsetTop,
                Math.max(element.offsetWidth, element.scrollWidth),
                Math.max(element.offsetHeight, element.scrollHeight)];
    },

    onLoad: function() {
        var i, 
            j,
            style,
            kids;

        // Build styles
        style = document.createElement('style');
        style.type = 'text/css';
        style.innerHTML  = '.canvasSelector {position: absolute; border:2px solid; zIndex:9999;}';
        style.innerHTML += '.canvasRed {border-color:red; }';
        style.innerHTML += '.canvasYellow {border-color:yellow; }';
        document.getElementsByTagName('head')[0].appendChild(style);

        // Create a map of form objects
        for (i = 0; i < document.forms.length; i++) {
            kids = document.forms[i].childNodes;
            for (j = 0; j < kids.length; j++) {
                if (typeof kids[j].id !== 'undefined')
                    NSB.fe._map[kids[j].id] = NSB.fe.getElementRect(kids[j])
            }
        }
    },

    select: function(elements) {
        var i,
            canvas,
            rect,
            canvas_color;

        // remove current selection
        for (i = 0; i < NSB.fe._selection.length; i++) {
            canvas = document.getElementById(NSB.fe._canvas_prefix+NSB.fe._selection[i]);
            document.body.removeChild(canvas);
        }

        canvas_color = (elements.length === 1) ? 'Red' : 'Yellow';

        // create new selection, as necessary
        for (i = 0; i < elements.length; i++) {
            rect = NSB.fe._map[elements[i]];
            canvas = NSB.fe.createCanvas(elements[i], rect, canvas_color);
            canvas.style.borderBottomWidth = 'dotted';
        }
        NSB.fe._selection = elements;
        return JSON.stringify(NSB.fe._selection);
    },

    setCanvasRect: function(element_name, rect) {
        var canvas = document.getElementById(NSB.fe._canvas_prefix+element_name);

        if (typeof canvas !== 'undefined') {
            canvas.style.cssText = 'left:'+(rect[0] - 2)+'px; top:'+(rect[1] - 2)+'px; ';
            canvas.style.cssText += 'width:'+rect[2]+'px; height:'+rect[3]+'px; ';
            return canvas.style.cssText;
        }
        return 'No canvas!';
    }
};
window.addEventListener('load', NSB.fe.onLoad, false);
