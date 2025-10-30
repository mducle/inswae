class Figure {
  constructor(id, div, width, height, title, toolbar) {
    this.div = div;
    this.div.id = id;
    this.canvas = document.createElement("canvas");
    this.canvas.id = id + "canvas";
    var context = this.canvas.getContext('2d');
    var backingStore =
      context.backingStorePixelRatio ||
      context.webkitBackingStorePixelRatio ||
      context.mozBackingStorePixelRatio ||
      context.msBackingStorePixelRatio ||
      context.oBackingStorePixelRatio ||
      context.backingStorePixelRatio ||
      1;
    this.ratio = (window.devicePixelRatio || 1) / backingStore;
    // The top bar
    var topbar = document.createElement("div");
    topbar.id = id + "top";
    topbar.setAttribute("style", "font-weight: bold; text-align: center");
    topbar.textContent = title;
    this.div.appendChild(topbar);
    // Main canvas div with canvas and rubberband for toolbar etc
    var canvas_div = document.createElement("div");
    canvas_div.setAttribute("style", "position: relative");
    this.canvas.setAttribute("width", width * this.ratio);
    this.canvas.setAttribute("height", height * this.ratio);
    this.canvas.setAttribute(
      "style",
      "left: 0; top: 0; z-index: 0; outline: 0; width:" + width + "px; height: " + height + "px");
    canvas_div.appendChild(this.canvas);
    var rubberband = document.createElement("canvas");
    rubberband.id = id + "rubberband";
    rubberband.setAttribute("width", width * this.ratio);
    rubberband.setAttribute("height", height * this.ratio);
    rubberband.setAttribute(
      "style",
      "position: absolute; left: 0; top: 0; z-index: 0; outline: 0; width: " + width + "px; height: " + height + "px");
    // Canvas must have a "tabindex" attr in order to receive keyboard events
    rubberband.setAttribute("tabindex", "0");
    var rubber_context = rubberband.getContext("2d");
    rubber_context.strokeStyle = "#000000";
    rubber_context.setLineDash([2, 2]);
    canvas_div.appendChild(rubberband);
    this.div.appendChild(canvas_div);
    // The bottom bar, with toolbar and message display
    this.bottom = document.createElement("div");
    this.bottom.id = id + "bottom";
    this.message = document.createElement("div");
    this.message.id = self._id + "message";
    this.message.setAttribute("style", "min-height: 1.5em");
    this.bottom.appendChild(this.message);
    this.div.appendChild(this.bottom);
  }
}


export const mpljs = { Figure }
