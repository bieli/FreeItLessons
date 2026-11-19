// "Islands": Django renders the pages, React takes over the interactive parts.
//   <div data-island="Name" data-props-id="json-script-id" data-...></div>
import { StrictMode, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import { readJsonScript } from './context';

export function readProps(element) {
  const { island, propsId, ...dataset } = element.dataset;
  const props = { ...dataset, ...(propsId ? readJsonScript(propsId) : {}) };
  const template = element.querySelector(':scope > template');
  if (template) props.html = template.innerHTML;
  return props;
}

export function mountIslands(registry, root = document) {
  const roots = [];
  root.querySelectorAll('[data-island]').forEach((element) => {
    const Component = registry[element.dataset.island];
    if (!Component) {
      console.error(`Unknown island "${element.dataset.island}"`);
      return;
    }
    const props = readProps(element);
    const reactRoot = createRoot(element);
    reactRoot.render(
      <StrictMode>
        <Suspense fallback={null}>
          <Component {...props} />
        </Suspense>
      </StrictMode>,
    );
    roots.push(reactRoot);
  });
  return roots;
}
