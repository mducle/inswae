function simpleKeys(original) {
  // return a copy of an object with only non-object keys to avoid circular references
  return Object.keys(original).reduce(function (obj, key) {
    if (typeof original[key] !== 'object') {
      obj[key] = original[key];
    }
    return obj;
  }, {});
};
    
class Figure {
  constructor(mplfig, parent_element, width, height) {
    this.mplfig = mplfig;
    this.root = document.createElement('div');
    this.root.setAttribute('style', 'display: inline-block');
    parent_element.appendChild(this.root);
    this.canvas = document.createElement("canvas");
    this.canvas.classList.add('mpl-canvas');
    this.canvas.setAttribute('style', 'box-sizing: content-box; pointer-events: none; position: relative; z-index: 0;');
    this.context = this.canvas.getContext('2d');
    var backingStore =
      this.context.backingStorePixelRatio ||
      this.context.webkitBackingStorePixelRatio ||
      this.context.mozBackingStorePixelRatio ||
      this.context.msBackingStorePixelRatio ||
      this.context.oBackingStorePixelRatio ||
      this.context.backingStorePixelRatio ||
      1;
    this.ratio = (window.devicePixelRatio || 1) / backingStore;
    // The top bar
    var titlebar = document.createElement('div');
    titlebar.classList = 'ui-dialog-titlebar ui-widget-header ui-corner-all ui-helper-clearfix';
    this.header = document.createElement('div');
    this.header.classList = 'ui-dialog-title';
    this.header.setAttribute('style', 'width: 100%; text-align: center; padding: 3px;');
    this.header.textContent = mplfig._title;
    titlebar.appendChild(this.header);
    this.root.appendChild(titlebar);
    // Main canvas div with canvas and rubberband for toolbar etc
    this.canvas_div = document.createElement("div");
    this.canvas_div.setAttribute('tabindex', '0');
    this.canvas_div.setAttribute('style', 'border: 1px solid #ddd; box-sizing: content-box; clear:both;' +
      'min-height: 1px; min-width: 1px; outline: 0; overflow: hidden; position: relative; resize: both; z-index: 2;');
    this.canvas.setAttribute("width", width * this.ratio);
    this.canvas.setAttribute("height", height * this.ratio);
    //this.canvas.setAttribute("style", "left: 0; top: 0; z-index: 0; outline: 0; width:" + width + "px; height: " + height + "px");
    this.canvas.classList.add('mpl-canvas');
    this.canvas.setAttribute('style', 'box-sizing: content-box; pointer-events: none; position: relative; z-index: 0;');
    this.canvas_div.appendChild(this.canvas);
    // Rubberband for zoom/pan etc
    this.rubberband_canvas = document.createElement('canvas');
    this.rubberband_canvas.setAttribute('style', 'box-sizing: content-box; left: 0; pointer-events: none; position: absolute; top: 0; z-index: 1;');
    this.rubberband_context = this.rubberband_canvas.getContext('2d');
    this.rubberband_context.strokeStyle = '#000000';
    this.rubberband_canvas.setAttribute('width', width * this.ratio);
    this.rubberband_canvas.setAttribute('height', height * this.ratio);
    this.canvas_div.appendChild(this.rubberband_canvas);
    // Event handling
    var fig = this; // Need to define this as var for closure below to work
    function on_keyboard_event_closure(name) {
      return function (event) {
        return fig.key_event(event, name);
      };
    }
    function on_mouse_event_closure(name) {
      var UA = navigator.userAgent;
      var isWebKit = /AppleWebKit/.test(UA) && !/Chrome/.test(UA);
      if(isWebKit) {
        return function (event) {
          event.preventDefault();
          return fig.mouse_event(event, name);
        };
      } else {
        return function (event) {
          return fig.mouse_event(event, name);
        };
      }
    }
    this.canvas_div.addEventListener('keydown', on_keyboard_event_closure('key_press'));
    this.canvas_div.addEventListener('keyup', on_keyboard_event_closure('key_release'));
    this.canvas_div.addEventListener('mousedown', on_mouse_event_closure('button_press'));
    this.canvas_div.addEventListener('mouseup', on_mouse_event_closure('button_release'));
    this.canvas_div.addEventListener('dblclick', on_mouse_event_closure('dblclick'));
    // Throttle sequential mouse events to 1 every 20ms.
    this.canvas_div.addEventListener('mousemove', on_mouse_event_closure('motion_notify'));
    this.canvas_div.addEventListener('mouseenter', on_mouse_event_closure('figure_enter'));
    this.canvas_div.addEventListener('mouseleave', on_mouse_event_closure('figure_leave'));
    this.canvas_div.addEventListener('wheel', function (event) {
      if (event.deltaY < 0) { event.step = 1; } else { event.step = -1; }
      on_mouse_event_closure('scroll')(event);
    });
    // Disable right mouse context menu.
    this.canvas_div.addEventListener('contextmenu', function (_e) { event.preventDefault(); return false; });
    this.root.appendChild(this.canvas_div);
    // The bottom bar, with toolbar and message display
    this._toolbar_images = [];
    this.init_toolbar(this);
  };

  init_toolbar() {
    toolbar = document.createElement('div');
    toolbar.classList = 'mpl-toolbar';
    this.root.appendChild(toolbar);
    var fig = this;
    function on_click_closure(name) {
        return function (_event) {
            return fig.toolbar_button_onclick(name);
        };
    }
    function on_mouseover_closure(tooltip) {
        return function (event) {
            if (!event.currentTarget.disabled) {
                return fig.toolbar_button_onmouseover(tooltip);
            }
        };
    }
    this.buttons = {};
    var buttonGroup = document.createElement('div');
    var toolbar_items = this.mplfig.get_toolbar_items();
    buttonGroup.classList = 'mpl-button-group';
    for (var toolbar_ind in toolbar_items) {
        var name = toolbar_items[toolbar_ind][0];
        var tooltip = toolbar_items[toolbar_ind][1];
        var image = toolbar_items[toolbar_ind][2];
        var method_name = toolbar_items[toolbar_ind][3];
        if (!name) {
            /* Instead of a spacer, we start a new button group. */
            if (buttonGroup.hasChildNodes()) {
                toolbar.appendChild(buttonGroup);
            }
            buttonGroup = document.createElement('div');
            buttonGroup.classList = 'mpl-button-group';
            continue;
        }
        var button = (this.buttons[name] = document.createElement('button'));
        button.classList = 'mpl-widget';
        button.setAttribute('role', 'button');
        button.setAttribute('aria-disabled', 'false');
        button.addEventListener('click', on_click_closure(method_name));
        button.addEventListener('mouseover', on_mouseover_closure(tooltip));
        var icon_img = new Image();
        this._toolbar_images.push(icon_img)
        const image_bytes = this.mplfig.get_toolbar_image(image);
        const blob = new Blob([image_bytes], { type: 'image/png' });
        icon_img.src = (window.URL || window.webkitURL).createObjectURL(blob);
        icon_img.alt = tooltip;
        button.appendChild(icon_img);
        buttonGroup.appendChild(button);
    }
    if (buttonGroup.hasChildNodes()) {
        toolbar.appendChild(buttonGroup);
    }
    var fmt_picker = document.createElement('select');
    fmt_picker.classList = 'mpl-widget';
    toolbar.appendChild(fmt_picker);
    this.format_dropdown = fmt_picker;
    var extensions = ["eps", "jpeg", "pdf", "pgf", "png", "ps", "raw", "svg", "tif"];
    var default_extension = "png";
    for (var ind in extensions) {
        var fmt = extensions[ind];
        var option = document.createElement('option');
        option.selected = fmt === default_extension;
        option.innerHTML = fmt;
        fmt_picker.appendChild(option);
    }
    this.message = document.createElement('span');
    this.message.classList = 'mpl-message';
    toolbar.appendChild(this.message);
  };

  mouse_event(event, name) {
    if (name === 'button_press') {
        this.canvas.focus();
        this.canvas_div.focus();
    }
    // from https://stackoverflow.com/q/1114465
    var boundingRect = this.canvas.getBoundingClientRect();
    var x = (event.clientX - boundingRect.left) * this.ratio;
    var y = (event.clientY - boundingRect.top) * this.ratio;
    function getModifiers(event) {
      var mods = [];
      if (event.ctrlKey) { mods.push('ctrl'); }
      if (event.altKey) { mods.push('alt'); }
      if (event.shiftKey) { mods.push('shift'); }
      if (event.metaKey) { mods.push('meta'); }
      return mods;
    };
    this.mplfig.handle_mouse(name, x, y, event.button, event.step, getModifiers(event), simpleKeys(event));
    return false;
  };

  key_event(event, name) {
    // Prevent repeat events
    if (name === 'key_press') {
      if (event.key === this._key) {
        return;
      } else {
        this._key = event.key;
      }
    }
    if (name === 'key_release') {
      this._key = null;
    }
    var value = '';
    if (event.ctrlKey && event.key !== 'Control') {
      value += 'ctrl+'; }
    else if (event.altKey && event.key !== 'Alt') {
      value += 'alt+'; }
    else if (event.shiftKey && event.key !== 'Shift') {
      value += 'shift+'; }
    value += 'k' + event.key;
    this.mplfig.handle_key(name, value, simpleKeys(event));
    return false;
  };

  toolbar_button_onclick(name) {
    if (name === 'download') {
      var format = this.format_dropdown.options[this.format_dropdown.selectedIndex].value;
      this.mplfig.handle_save(format);
    } else {
      this.mplfig.handle_toolbar_button(name);
    }
  };

  toolbar_button_onmouseover(tooltip) {
    this.message.textContent = tooltip;
  };

  handle_message(msg) {
    this.message.textContent = msg['message'];
  };

  handle_rubberband(x0, x1, y0, y1) {
    x0 = Math.floor(x0 / this.ratio) + 0.5;
    y0 = Math.floor((this.canvas.height - y0) / this.ratio) + 0.5;
    x1 = Math.floor(x1 / this.ratio) + 0.5;
    y1 = Math.floor((this.canvas.height - y1) / this.ratio) + 0.5;
    var min_x = Math.min(x0, x1);
    var min_y = Math.min(y0, y1);
    var width = Math.abs(x1 - x0);
    var height = Math.abs(y1 - y0);
    this.rubberband_context.clearRect(0, 0, this.canvas.width / this.ratio, this.canvas.height / this.ratio);
    this.rubberband_context.strokeRect(min_x, min_y, width, height);
  };

  handle_history_buttons(back, forward) {
    this.buttons['Back'].disabled = !back;
    this.buttons['Back'].setAttribute('aria-disabled', !back);
    this.buttons['Forward'].disabled = !forward;
    this.buttons['Forward'].setAttribute('aria-disabled', !forward);
  };

  handle_navigate_mode(mode) {
    if (mode === 'PAN') {
        this.buttons['Pan'].classList.add('active');
        this.buttons['Zoom'].classList.remove('active');
    } else if (mode === 'ZOOM') {
        this.buttons['Pan'].classList.remove('active');
        this.buttons['Zoom'].classList.add('active');
    } else {
        this.buttons['Pan'].classList.remove('active');
        this.buttons['Zoom'].classList.remove('active');
    }
  };

};

export const mpljs = { Figure }
