const { h } = hyperapp;
const { Element } = osjsGui;

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

export const jswidgets = { TextLabel }
