(function () {  // en-hint: v1.0
  'use strict';

  // Wraps an English reading-hint such as "[Add-ons]" inside translated
  // titles / navigation so CSS can render it as a small, muted pill.
  //
  // The hint text lives verbatim inside translated `msgstr` strings (plain
  // text, no markup), so there is nothing for CSS to select. This script
  // creates the wrapper at runtime: it walks text nodes inside headings and
  // navigation links, finds `[...]` runs, and wraps them in
  // <span class="i18n-en-hint">…</span>.
  //
  // Convention: only square brackets `[...]` are treated as hints. Parentheses
  // are intentionally NOT matched -- Vietnamese prose uses them for ordinary
  // asides and they cannot be distinguished from English hints reliably.

  // Only act on translated builds. The English source has no hints, and
  // skipping it avoids pilling legitimate `[...]` in English content.
  var lang = (typeof DOCUMENTATION_OPTIONS !== 'undefined')
    ? DOCUMENTATION_OPTIONS.LANGUAGE : '';
  if (!lang || lang === 'None' || lang === 'en') {
    return;
  }

  // Containers whose text may carry a hint. Scoped deliberately to titles and
  // navigation -- NOT body paragraphs, where `[...]` is often code/indices.
  var SELECTORS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    '.sidebar-tree a',            // furo left navigation
    '.toctree-wrapper a',         // in-page toctrees (e.g. section landing pages)
    '.related-pages a',           // bottom prev/next links (a.prev-page / a.next-page)
  ].join(', ');

  // Never descend into these (code, shortcuts, the permalink anchor, etc.).
  var SKIP = { CODE: 1, PRE: 1, KBD: 1, SAMP: 1, SCRIPT: 1, STYLE: 1 };
  var HINT_RE = /\[[^\][]+\]/g;

  function wrapHintsIn(root) {
    var walker = document.createTreeWalker(
      root, NodeFilter.SHOW_TEXT,
      {
        acceptNode: function (node) {
          if (!node.nodeValue || node.nodeValue.indexOf('[') === -1) {
            return NodeFilter.FILTER_REJECT;
          }
          var p = node.parentNode;
          while (p && p !== root) {
            if (SKIP[p.nodeName] || (p.classList &&
                (p.classList.contains('headerlink') ||
                 p.classList.contains('i18n-en-hint')))) {
              return NodeFilter.FILTER_REJECT;
            }
            p = p.parentNode;
          }
          return NodeFilter.FILTER_ACCEPT;
        },
      });

    var targets = [];
    while (walker.nextNode()) { targets.push(walker.currentNode); }

    targets.forEach(function (textNode) {
      var text = textNode.nodeValue;
      HINT_RE.lastIndex = 0;
      var frag = document.createDocumentFragment();
      var last = 0, m;
      while ((m = HINT_RE.exec(text)) !== null) {
        if (m.index > last) {
          frag.appendChild(document.createTextNode(text.slice(last, m.index)));
        }
        var span = document.createElement('span');
        span.className = 'i18n-en-hint';
        span.textContent = m[0].slice(1, -1);  // drop the surrounding []
        frag.appendChild(span);
        last = m.index + m[0].length;
      }
      if (last < text.length) {
        frag.appendChild(document.createTextNode(text.slice(last)));
      }
      textNode.parentNode.replaceChild(frag, textNode);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll(SELECTORS).forEach(wrapHintsIn);
  });
})();
