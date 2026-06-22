(function () {  // en-hint: v2.0 (navigation fallback only)
  'use strict';

  // Navigation fallback for the English reading-hint pill.
  //
  // In-page headings, terms, rubrics, field names and captions are now pilled
  // server-side by the `repeatable_builder` Sphinx extension (it splits the
  // doctree leaf and emits <span class="i18n-en-hint">…</span> directly). This
  // script only covers links that the HTML builder assembles from *other*
  // documents' titles -- the toctrees, the left sidebar tree and the
  // prev/next related-pages bar -- which are built after `doctree-resolved`
  // and so are out of reach of the server-side renderer.
  //
  // The hint text lives verbatim inside translated link text (plain text, no
  // markup), so there is nothing for CSS to select; this walks those links'
  // text nodes, finds `[...]` runs, and wraps them in
  // <span class="i18n-en-hint">…</span> -- the SAME class as the server-side
  // pill, so styling is identical.
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

  // Navigation links assembled from other docs' titles -- the only place the
  // server-side renderer cannot reach. Headings (h1-h6) are deliberately NOT
  // listed: they are pilled server-side now. Body paragraphs are excluded too,
  // where `[...]` is often code/indices.
  var SELECTORS = [
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
