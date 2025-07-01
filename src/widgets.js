const { h } = hyperapp;
const { Element } = osjsGui;

const filteredProps = (props, filterKeys) => {
  const keys = Object.keys(props);
  const filter = k => filterKeys.indexOf(k) === -1;

  return keys
    .filter(filter)
    .reduce((result, k) => Object.assign({
      [k]: props[k]
    }, result), {});
};

const createField = (name, props, defaultProps, cb, cbInput) => {
  const oninput = props.oninput || function() {};
  const onchange = props.onchange || function() {};
  const onkeydown = props.onkeydown || function() {};

  const getValue = cbInput || (ev => [ev.target.value]);
  const fieldProps = Object.assign(
    {
      oninput: ev => oninput(ev, ...getValue(ev)),
      onchange: ev => onchange(ev, ...getValue(ev)),
      onkeydown: ev => {
        if (ev.keyCode === 13 && props.onenter) {
          props.onenter(ev, ...getValue(ev));
        }
        onkeydown(ev);
      }
    },
    defaultProps,
    filteredProps(props, ['choices', 'label', 'box', 'oninput', 'onchange'])
  );

  return h(Element, Object.assign({}, props.box || {}, {
    class: 'osjs-gui-field osjs-gui-' + name
  }), cb(fieldProps));
};

const TextLabel = (props = {}, children = []) => {
  const placement = props.placement || 'top';
  const text = props.text || '';

  const elementProps = Object.assign({
    class: ['osjs-gui-field-label', 'osjs-gui-field-label-on-' + placement]
  }, props.box || {});

  return h(Element, elementProps, [
    h('label', {}, text),
    children
  ]);
};

export const NumberSpinner = (props = {}, children = []) =>
  createField('number-spinner', props, {
    type: 'number',
    value: 0
  }, (fieldProps) => h('input', fieldProps));

export const EditableTable = (props = {}, children = []) => {
  const nr = props.nr || 1;
  const nc = props.nc || 1;
  const row_titles = props.row_titles || "";
  const col_titles = props.col_titles || "";
  const col_widths = props.col_widths || [['auto']];
  const editable = props.editable || [[true]];
  const selectable = props.selectable || [[true]];
  const select_mode = props.sel_mode || "selectitems";
  const values = props.values || [[]];
  const styles = props.styles || {};
  const onchange = props.onchange || function(ev, val){};
  const onactivate = props.activated || function(ev, val){};
  const onclicked = props.clicked || function(ev, val){};
  const onselect = props.selected || function(val){};
  const currentcb = props.currentcb || function(val){};
  const editprop = {'type':'text', 'size':'5'}
  let curr_ic = props.curr_ic || 0;
  let curr_ir = props.curr_ir || 0;
  const oncellclick = (ev, ic, ir, isdouble) => {
    if (ev.type == 'click' || ev.type == 'keydown') {
      curr_ir = ir;
      curr_ic = ic;
      currentcb([curr_ir, curr_ic]);
    }
    let cell = ev.target;
    if (ev.target.tagName == 'INPUT') {
      cell = ev.target.parentNode;
    }
    onclicked(ev, [curr_ir, curr_ic]);
    if (isdouble) {
      onactivate(ev, [curr_ir, curr_ic]);
    }
    const row = cell.parentNode;
    const table = row.parentNode;
    const i0 = table.rows[0].cells[0].tagName == 'TH' ? 1 : 0;
    if (selectable[ic][ir]) {
      if (ev.shiftKey === false) {
        for (let i = 0; i < table.rows.length; i++) {
          for (let j = 0; j < table.rows[0].cells.length; j++) {
            table.rows[i].cells[j].style.backgroundColor = 'transparent';
          }
        }
      }
      if (select_mode == 'selectrows') {
        for (let i = i0; i < table.rows[0].cells.length; i++) {
          table.rows[ir+i0].cells[i].style.backgroundColor = '#AAAAAA';
        }
      } else if (select_mode == 'selectitems') {
          table.rows[ir+i0].cells[ic+i0].style.backgroundColor = '#AAAAAA';
      } else { // selectcolumns
        for (let i = i0; i < table.rows.length; i++) {
          table.rows[i].cells[ic+i0].style.backgroundColor = '#AAAAAA';
        }
      }
    }
    // Callback to Python code to set selection (currently highlighted cells)
    let selected_cells = []
    for (let i = i0; i < table.rows.length; i++) {
      for (let j = i0; j < table.rows[0].cells.length; j++) {
        if (table.rows[i].cells[j].style.backgroundColor != 'transparent') {
          selected_cells.push([i-i0, j-i0]);
        }
      }
    }
    onselect(selected_cells);
  };
  const onkeydown = ev => {
    if (ev.key == 'ArrowUp' && curr_ir > 0) {
      oncellclick(ev, curr_ic, curr_ir - 1, false);
    } else if (ev.key == 'ArrowDown' && curr_ir < nr-1) {
      oncellclick(ev, curr_ic, curr_ir + 1, false);
    } else if (ev.key == 'ArrowLeft' && curr_ic > 0) {
      oncellclick(ev, curr_ic - 1, curr_ir, false);
    } else if (ev.key == 'ArrowRight' && curr_ic < nc-1) {
      oncellclick(ev, curr_ic + 1, curr_ir, false);
    }
  };
  let contents = [];
  if (col_titles != "") {
    let row = [h('th', styles, '')]
    for (let ic=0; ic < nc; ic++) {
      row.push(h('th', styles, col_titles[ic]));
    }
    contents.push(h('tr', {}, row));
  }
  let col_styles = [];
  for (let ic=0; ic < nc; ic++) {
    col_styles.push({'width':col_widths[ic], ...styles});
  }
  for (let ir=0; ir < nr; ir++) {
    let row = [h('td', styles, row_titles[ir])] || [];
    for (let ic=0; ic < nc; ic++) {
      const this_style = {
        'onclick': ev => oncellclick(ev, ic, ir, false),
        'ondblclick': ev => oncellclick(ev, ic, ir, true),
        'onkeypress': ev => { if (!editable[ic][ir]) { oncellclick(ev, ic, ir, true) } },
        'onkeydown': ev => onkeydown(ev),
        ...col_styles[ic]
      };
      if (editable[ic][ir]) {
        row.push(h('td', this_style, h('input', {'value':values[ic][ir],
          'onchange': ev => onchange(ev, [ir, ic, ev.target.value]),
          ...editprop})));
      } else {
        row.push(h('td', {'tabindex':'0', ...this_style}, values[ic][ir]));
      }
    }
    contents.push(h('tr', {}, row));
  }
  return h('table', {'border':'0px', 'border-collapse':'collapse', 'bgColor':'white'}, contents);
};

export const ListWidget = (props = {}, children = []) => {
  const items = props.items || [[]];
  const id = props.id || "listwidgetinstance";
  const selchanged = props.selectionchanged || function(sel){};
  const currentcb = props.currentcb || function(val){};
  const curr_ii = props.curr_ii || 0;
  const clearselection = () => {
    const thislist = document.getElementById(id);
    for (let ii=0; ii < items.length; ii++) {
      thislist.children[ii].style.backgroundColor = 'transparent';
    }
  }
  const onclick = (ev, ii) => {
    const thislist = document.getElementById(id);
    if (ev.shiftKey === false) {
      clearselection();
      if (ev.type == 'click') {
        ev.target.style.backgroundColor = '#AAAAAA';
        selchanged([ii]);
      } else {
        if (ev.key == 'ArrowUp' && curr_ii > 0) {
          ii = curr_ii - 1;
        } else if (ev.key == 'ArrowDown' && curr_ii < items.length-1) {
          ii = curr_ii + 1;
        }
        thislist.children[ii].style.backgroundColor = '#AAAAAA';
      }
    } else {
      if (ev.type == 'click') {
        const j0 = ii > curr_ii ? curr_ii : ii;
        const j1 = ii > curr_ii ? ii : curr_ii;
        for (let jj=j0; jj<=j1; jj++) {
          thislist.children[jj].style.backgroundColor = '#AAAAAA';
        }
      } else {
        if (ev.key == 'ArrowUp' && curr_ii > 0) {
          ii = curr_ii - 1;
        } else if (ev.key == 'ArrowDown' && curr_ii < items.length-1) {
          ii = curr_ii + 1;
        }
        thislist.children[ii].style.backgroundColor = '#AAAAAA';
      }
      let selection = [];
      for (let ii=0; ii < items.length; ii++) {
        if (thislist.children[ii].style.backgroundColor != 'transparent') {
          selection.push(ii);
        }
      }
      selchanged(selection);
    }
    currentcb(ii);
  };
  let contents = []
  for (let ii=0; ii < items.length; ii++) {
    contents.push(h('li', {
      'tabindex':'0',
      'onclick': ev => onclick(ev, ii),
      'onkeydown': ev => onclick(ev, ii),
    }, items[ii]))
  }
  return h('ul', {'id':id,
    'style':{'list-style-type':'none', 'display':'table-row', 'background-color':'white'}
  }, contents);
};

export const jswidgets = { TextLabel, NumberSpinner, EditableTable, ListWidget }
