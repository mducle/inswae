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

export const EditableTable = (props = {}, children = []) => {
  const nr = props.nr || 1;
  const nc = props.nc || 1;
  const row_titles = props.row_titles || "";
  const col_titles = props.col_titles || "";
  const editable = props.editable || [[true]];
  const values = props.values || [[]];
  const styles = props.styles || {'border':'0px', 'border-collapse':'collapse'};
  const onchange = props.onchange || function(ev, val){};
  const editprop = {'type':'text', 'size':'1'}
  let contents = [];
  if (col_titles != "") {
    let row = [h('th', styles, '')]
    for (let ic=0; ic < nc; ic++) {
      row.push(h('th', styles, col_titles[ic]));
    }
    contents.push(h('tr', {}, row));
  }
  for (let ir=0; ir < nr; ir++) {
    let row = [h('td', styles, row_titles[ir])] || [];
    for (let ic=0; ic < nc; ic++) {
      if (editable[ic][ir]) {
        row.push(h('td', styles, h('input', {'value':values[ic][ir], 
          'onchange': ev => props.onchange(ev, [ir, ic, ev.target.value]),
          ...editprop})));
      } else {
        row.push(h('td', styles, values[ic][ir]));
      }
    }
    contents.push(h('tr', {}, row));
  }
  return h('table', {'onchange':onchange, ...styles}, contents);
};

export const NumberSpinner = (props = {}, children = []) =>
  createField('number-spinner', props, {
    type: 'number',
    value: 0
  }, (fieldProps) => h('input', fieldProps));

export const jswidgets = { TextLabel, NumberSpinner, EditableTable }
