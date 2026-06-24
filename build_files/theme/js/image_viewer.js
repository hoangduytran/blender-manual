/**
 * Lightbox-style image viewer for manual figures.
 *
 * Adds a small zoom button to article figures. The image opens in a fixed
 * frame where it can be zoomed with wheel/buttons and panned by dragging.
 */
(function () {
  'use strict';

  var VIEWER_CLASS = 'manual-image-viewer';
  var SOURCE_CLASS = 'manual-image-viewer-source';
  var FIGURE_CLASS = 'manual-image-viewer-figure';
  var BUTTON_CLASS = 'manual-image-viewer-trigger';
  var OPEN_CLASS = 'manual-image-viewer-open';
  var IMAGE_EXT = /\.(apng|avif|gif|jpe?g|png|svg|webp)([?#].*)?$/i;
  var MIN_SCALE = 0.1;
  var MAX_SCALE = 8;
  var ZOOM_STEP = 1.25;
  var LARGE_IMAGE_MAX_VIEWPORT_WIDTH = 0.92;
  var LARGE_IMAGE_MAX_VIEWPORT_HEIGHT = 0.72;
  var NATURAL_IMAGE_MAX_VIEWPORT_HEIGHT = 0.82;

  var viewer = null;
  var state = {
    image: null,
    src: '',
    scale: 1,
    fitScale: 1,
    x: 0,
    y: 0,
    dragging: false,
    lastX: 0,
    lastY: 0,
    openMode: 'fit',
  };

  function append(parent, tagName, className, text) {
    var element = document.createElement(tagName);
    if (className) {
      element.className = className;
    }
    if (text) {
      element.textContent = text;
    }
    parent.appendChild(element);
    return element;
  }

  function setButton(button, label, action, title) {
    button.type = 'button';
    button.textContent = label;
    button.dataset.action = action;
    button.title = title;
    button.setAttribute('aria-label', title);
  }

  function closest(element, selector) {
    return element.closest ? element.closest(selector) : null;
  }

  function isImageHref(href) {
    return IMAGE_EXT.test(href || '');
  }

  function displaySrc(image) {
    return image.currentSrc || image.src;
  }

  function fullSizeSrc(image) {
    var anchor = closest(image, 'a');
    if (anchor && isImageHref(anchor.getAttribute('href'))) {
      return anchor.href;
    }
    return displaySrc(image);
  }

  function isEligibleImage(image) {
    if (!displaySrc(image) || image.classList.contains(SOURCE_CLASS)) {
      return false;
    }
    if (!closest(image, 'article[role="main"]')) {
      return false;
    }
    if (!closest(image, 'figure')) {
      return false;
    }
    if (closest(image, '.sidebar-drawer, .toc-drawer, .mobile-header')) {
      return false;
    }
    if (closest(image, '.card, .toctree-wrapper')) {
      return false;
    }
    if (closest(image, '.' + VIEWER_CLASS)) {
      return false;
    }
    return true;
  }

  function clearInlineSize(image) {
    image.style.width = '';
    image.style.maxWidth = '';
    image.style.maxHeight = '';
    image.style.height = '';
  }

  function applyInlineSize(image) {
    var figure = closest(image, 'figure');
    var naturalWidth = image.naturalWidth || 0;
    var naturalHeight = image.naturalHeight || 0;
    var viewportWidth = window.innerWidth
      || (document.documentElement && document.documentElement.clientWidth)
      || 0;
    var viewportHeight = window.innerHeight
      || (document.documentElement && document.documentElement.clientHeight)
      || 0;
    var contentWidth = figure && figure.clientWidth ? figure.clientWidth : 0;
    var floatingFigure = figure && (
      figure.classList.contains('align-left')
      || figure.classList.contains('align-right')
    );
    var availableWidth = Math.max(1, Math.min(
      floatingFigure ? contentWidth || viewportWidth : viewportWidth,
      viewportWidth * LARGE_IMAGE_MAX_VIEWPORT_WIDTH
    ));
    var availableHeight = Math.max(1, viewportHeight * LARGE_IMAGE_MAX_VIEWPORT_HEIGHT);
    var naturalMaxHeight = Math.max(1, viewportHeight * NATURAL_IMAGE_MAX_VIEWPORT_HEIGHT);
    var fitsNaturally = naturalWidth > 0
      && naturalHeight > 0
      && naturalWidth <= availableWidth
      && naturalHeight <= naturalMaxHeight;

    clearInlineSize(image);
    image.classList.toggle('manual-image-viewer-source--natural', fitsNaturally);
    image.classList.toggle('manual-image-viewer-source--balanced', !fitsNaturally);
    if (figure) {
      figure.classList.toggle('manual-image-viewer-figure--natural', fitsNaturally);
      figure.classList.toggle('manual-image-viewer-figure--balanced', !fitsNaturally);
    }

    if (fitsNaturally) {
      image.style.width = naturalWidth + 'px';
      image.style.maxWidth = '100%';
    } else {
      image.style.maxWidth = 'min(100%, ' + Math.round(availableWidth) + 'px)';
      image.style.maxHeight = Math.round(availableHeight) + 'px';
      image.style.height = 'auto';
    }
  }

  function observeInlineSize(image) {
    if (image.complete && image.naturalWidth) {
      applyInlineSize(image);
    } else {
      image.addEventListener('load', function () {
        applyInlineSize(image);
      });
    }

    window.addEventListener('resize', function () {
      applyInlineSize(image);
    });
  }

  function captionFor(image) {
    var figure = closest(image, 'figure');
    var caption = figure && (
      figure.querySelector('figcaption .caption-text')
      || figure.querySelector('figcaption')
    );
    var text = caption ? caption.textContent : image.getAttribute('alt');
    return (text || '').trim();
  }

  function ensureViewer() {
    if (viewer) {
      return viewer;
    }

    var root = append(document.body, 'div', VIEWER_CLASS);
    var backdrop = append(root, 'button', 'manual-image-viewer__backdrop');
    var back = append(root, 'button', 'manual-image-viewer__back', '<');
    var frame = append(root, 'div', 'manual-image-viewer__frame');
    var toolbar = append(frame, 'div', 'manual-image-viewer__toolbar');
    var viewport = append(frame, 'div', 'manual-image-viewer__viewport');
    var image = append(viewport, 'img', 'manual-image-viewer__image');
    var caption = append(frame, 'div', 'manual-image-viewer__caption');
    var zoomOut = append(toolbar, 'button', 'manual-image-viewer__tool');
    var zoomIn = append(toolbar, 'button', 'manual-image-viewer__tool');
    var fit = append(toolbar, 'button', 'manual-image-viewer__tool');
    var fill = append(toolbar, 'button', 'manual-image-viewer__tool');
    var actual = append(toolbar, 'button', 'manual-image-viewer__tool');
    var full = append(toolbar, 'button', 'manual-image-viewer__tool');
    var open = append(toolbar, 'a', 'manual-image-viewer__tool manual-image-viewer__open', 'Open');
    var close = append(toolbar, 'button', 'manual-image-viewer__tool');

    root.hidden = true;
    frame.setAttribute('role', 'dialog');
    frame.setAttribute('aria-modal', 'true');
    frame.setAttribute('aria-label', 'Image viewer');
    backdrop.type = 'button';
    backdrop.setAttribute('aria-label', 'Close image viewer');
    back.type = 'button';
    back.title = 'Back to page';
    back.setAttribute('aria-label', 'Back to page');
    image.draggable = false;
    open.target = '_blank';
    open.rel = 'noopener';
    open.title = 'Open image in a new tab';
    open.setAttribute('aria-label', 'Open image in a new tab');

    setButton(zoomOut, '-', 'zoom-out', 'Zoom out');
    setButton(zoomIn, '+', 'zoom-in', 'Zoom in');
    setButton(fit, 'Fit', 'fit', 'Fit image');
    setButton(fill, 'Fill', 'fill', 'Fill screen');
    setButton(actual, '1:1', 'actual', 'Actual size');
    setButton(full, 'Full', 'full', 'Use full page');
    setButton(close, 'x', 'close', 'Close image viewer');

    toolbar.addEventListener('click', onToolbarClick);
    backdrop.addEventListener('click', closeViewer);
    back.addEventListener('click', closeViewer);
    viewport.addEventListener('wheel', onWheel, { passive: false });
    viewport.addEventListener('pointerdown', onPointerDown);
    viewport.addEventListener('dblclick', function () {
      setScale(state.scale === state.fitScale ? 1 : state.fitScale);
    });
    image.addEventListener('load', resetView);
    document.addEventListener('keydown', onKeyDown);
    window.addEventListener('resize', function () {
      if (!root.hidden) {
        resetView();
      }
    });

    viewer = {
      root: root,
      viewport: viewport,
      image: image,
      caption: caption,
      open: open,
    };
    return viewer;
  }

  function fitScale() {
    if (!state.image || !viewer) {
      return 1;
    }

    var bounds = viewer.viewport.getBoundingClientRect();
    var imageWidth = state.image.naturalWidth || state.image.width || 1;
    var imageHeight = state.image.naturalHeight || state.image.height || 1;
    var scale = Math.min(
      bounds.width / imageWidth,
      bounds.height / imageHeight,
      1
    );
    return Math.max(MIN_SCALE, scale);
  }

  function fillScale() {
    if (!state.image || !viewer) {
      return 1;
    }

    var bounds = viewer.viewport.getBoundingClientRect();
    var imageWidth = state.image.naturalWidth || state.image.width || 1;
    var imageHeight = state.image.naturalHeight || state.image.height || 1;
    var scale = Math.max(
      bounds.width / imageWidth,
      bounds.height / imageHeight,
      state.fitScale
    );
    return clamp(scale, MIN_SCALE, MAX_SCALE);
  }

  function applyTransform() {
    if (!viewer) {
      return;
    }

    viewer.image.style.left = 'calc(50% + ' + Math.round(state.x) + 'px)';
    viewer.image.style.top = 'calc(50% + ' + Math.round(state.y) + 'px)';
    viewer.image.style.transform = 'translate(-50%, -50%) scale('
      + state.scale.toFixed(4)
      + ')';
  }

  function resetView() {
    state.fitScale = fitScale();
    state.scale = state.openMode === 'fill' ? fillScale() : state.fitScale;
    state.x = 0;
    state.y = 0;
    applyTransform();
  }

  function setScale(nextScale, originX, originY) {
    if (!viewer) {
      return;
    }

    var oldScale = state.scale;
    var scale = clamp(nextScale, MIN_SCALE, MAX_SCALE);

    if (originX !== undefined && originY !== undefined && oldScale > 0) {
      state.x = originX - (originX - state.x) * (scale / oldScale);
      state.y = originY - (originY - state.y) * (scale / oldScale);
    }

    state.scale = scale;
    applyTransform();
  }

  function zoomBy(factor) {
    setScale(state.scale * factor);
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function setFullPage(enabled) {
    if (!viewer) {
      return;
    }

    viewer.root.classList.toggle('is-full-page', enabled);
  }

  function openViewer(image, options) {
    var nextViewer = ensureViewer();
    var src = fullSizeSrc(image);
    var fullPage = options && options.fullPage;
    var fill = options && options.fill;

    state.image = image;
    state.src = src;
    state.openMode = fill ? 'fill' : 'fit';
    state.scale = 1;
    state.fitScale = 1;
    state.x = 0;
    state.y = 0;

    nextViewer.caption.textContent = captionFor(image);
    nextViewer.caption.hidden = !nextViewer.caption.textContent;
    nextViewer.open.href = src;
    nextViewer.image.alt = image.getAttribute('alt') || '';
    setFullPage(!!fullPage);

    if (nextViewer.image.src === src && nextViewer.image.complete) {
      resetView();
    } else {
      nextViewer.image.src = src;
    }

    nextViewer.root.hidden = false;
    document.body.classList.add(OPEN_CLASS);

    if (nextViewer.image.complete) {
      resetView();
    }
  }

  function closeViewer() {
    if (!viewer || viewer.root.hidden) {
      return;
    }
    viewer.root.hidden = true;
    document.body.classList.remove(OPEN_CLASS);
    state.dragging = false;
  }

  function onToolbarClick(event) {
    var action = event.target.dataset.action;

    if (action === 'zoom-out') {
      zoomBy(1 / ZOOM_STEP);
    } else if (action === 'zoom-in') {
      zoomBy(ZOOM_STEP);
    } else if (action === 'fit') {
      state.openMode = 'fit';
      resetView();
    } else if (action === 'fill') {
      state.openMode = 'fill';
      resetView();
    } else if (action === 'actual') {
      setScale(1);
    } else if (action === 'full') {
      setFullPage(!viewer.root.classList.contains('is-full-page'));
      resetView();
    } else if (action === 'close') {
      closeViewer();
    }
  }

  function onWheel(event) {
    if (!viewer || viewer.root.hidden) {
      return;
    }

    event.preventDefault();

    var bounds = viewer.viewport.getBoundingClientRect();
    var originX = event.clientX - bounds.left - bounds.width / 2;
    var originY = event.clientY - bounds.top - bounds.height / 2;
    var factor = event.deltaY < 0 ? ZOOM_STEP : 1 / ZOOM_STEP;

    setScale(state.scale * factor, originX, originY);
  }

  function onPointerDown(event) {
    if (event.pointerType === 'mouse' && event.button !== 0) {
      return;
    }

    event.preventDefault();
    state.dragging = true;
    state.lastX = event.clientX;
    state.lastY = event.clientY;
    viewer.viewport.classList.add('is-panning');

    if (viewer.viewport.setPointerCapture) {
      viewer.viewport.setPointerCapture(event.pointerId);
    }

    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp);
    window.addEventListener('pointercancel', onPointerUp);
  }

  function onPointerMove(event) {
    if (!state.dragging) {
      return;
    }

    state.x += event.clientX - state.lastX;
    state.y += event.clientY - state.lastY;
    state.lastX = event.clientX;
    state.lastY = event.clientY;
    applyTransform();
  }

  function onPointerUp(event) {
    state.dragging = false;
    if (viewer) {
      viewer.viewport.classList.remove('is-panning');
      if (viewer.viewport.releasePointerCapture && event) {
        viewer.viewport.releasePointerCapture(event.pointerId);
      }
    }
    window.removeEventListener('pointermove', onPointerMove);
    window.removeEventListener('pointerup', onPointerUp);
    window.removeEventListener('pointercancel', onPointerUp);
  }

  function onKeyDown(event) {
    if (!viewer || viewer.root.hidden) {
      return;
    }

    if (event.key === 'Escape') {
      closeViewer();
    } else if (event.key === '+' || event.key === '=') {
      zoomBy(ZOOM_STEP);
    } else if (event.key === '-' || event.key === '_') {
      zoomBy(1 / ZOOM_STEP);
    } else if (event.key === '0') {
      resetView();
    }
  }

  function addTrigger(image) {
    var figure = closest(image, 'figure');
    var zoomButton;
    var fullButton;

    if (!figure || figure.classList.contains(FIGURE_CLASS)) {
      return;
    }

    figure.classList.add(FIGURE_CLASS);
    image.classList.add(SOURCE_CLASS);
    observeInlineSize(image);

    zoomButton = append(figure, 'button', BUTTON_CLASS + ' manual-image-viewer-trigger--zoom', '+');
    zoomButton.type = 'button';
    zoomButton.title = 'View larger image';
    zoomButton.setAttribute('aria-label', 'View larger image');
    zoomButton.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      openViewer(image);
    });

    fullButton = append(figure, 'button', BUTTON_CLASS + ' manual-image-viewer-trigger--full', 'Full');
    fullButton.type = 'button';
    fullButton.title = 'View image full page';
    fullButton.setAttribute('aria-label', 'View image full page');
    fullButton.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      openViewer(image, { fullPage: true, fill: true });
    });

    image.addEventListener('click', function (event) {
      var anchor = closest(image, 'a');
      if (anchor && !isImageHref(anchor.getAttribute('href'))) {
        return;
      }
      event.preventDefault();
      openViewer(image);
    });
  }

  function init() {
    var images = document.querySelectorAll('article[role="main"] img');
    images.forEach(function (image) {
      if (isEligibleImage(image)) {
        addTrigger(image);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
