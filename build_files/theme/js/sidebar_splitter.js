/**
 * Draggable splitters for Furo's left navigation and right page TOC.
 *
 * Each side panel is clamped to 1%..25% of the page width. The middle content
 * area receives the remaining width, up to 98% when both panels are minimized.
 * Double-click resets a panel to the theme default.
 */
(function () {
  'use strict';

  var LS_LEFT = 'bl-sidebar-left-percent';
  var LS_RIGHT = 'bl-sidebar-right-percent';
  var MIN_PANEL_PERCENT = 1;
  var MAX_PANEL_PERCENT = 25;

  function isDrawerMode(element) {
    return window.getComputedStyle(element).position === 'fixed';
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function readStoredPercent(key) {
    try {
      var value = window.localStorage.getItem(key);
      var percent = Number(value);
      return Number.isFinite(percent) && percent > 0 ? percent : null;
    } catch (error) {
      return null;
    }
  }

  function writeStoredPercent(key, percent) {
    try {
      window.localStorage.setItem(key, percent.toFixed(3));
    } catch (error) {
      /* Ignore storage failures; dragging should still work for this page. */
    }
  }

  function removeStoredPercent(key) {
    try {
      window.localStorage.removeItem(key);
    } catch (error) {
      /* Ignore storage failures; reset still clears the inline width. */
    }
  }

  function setFixedWidth(element, width) {
    var px = Math.round(width) + 'px';
    element.style.width = px;
    element.style.minWidth = px;
    element.style.flexBasis = px;
  }

  function clearFixedWidth(element) {
    element.style.width = '';
    element.style.minWidth = '';
    element.style.flexBasis = '';
  }

  function makeSplitter(side) {
    var splitter = document.createElement('div');
    var grip = document.createElement('span');

    splitter.className = 'sidebar-splitter sidebar-splitter--' + side;
    splitter.setAttribute('role', 'separator');
    splitter.setAttribute('aria-orientation', 'vertical');
    splitter.title = side === 'left'
      ? 'Drag to resize navigation; double-click to reset'
      : 'Drag to resize page contents; double-click to reset';

    grip.className = 'sidebar-splitter__grip';
    grip.setAttribute('aria-hidden', 'true');
    splitter.appendChild(grip);

    return splitter;
  }

  function wireDrag(splitter, onDelta, onReset) {
    splitter.addEventListener('pointerdown', function (event) {
      if (event.pointerType === 'mouse' && event.button !== 0) {
        return;
      }

      event.preventDefault();

      var lastX = event.clientX;
      var previousCursor = document.body.style.cursor;
      var previousUserSelect = document.body.style.userSelect;
      var active = true;

      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      splitter.classList.add('is-dragging');

      if (splitter.setPointerCapture) {
        splitter.setPointerCapture(event.pointerId);
      }

      function onMove(moveEvent) {
        if (!active) {
          return;
        }

        var dx = moveEvent.clientX - lastX;
        lastX = moveEvent.clientX;

        if (dx !== 0) {
          onDelta(dx);
        }
      }

      function stopDrag(upEvent) {
        if (!active) {
          return;
        }

        active = false;
        document.body.style.cursor = previousCursor;
        document.body.style.userSelect = previousUserSelect;
        splitter.classList.remove('is-dragging');

        if (splitter.releasePointerCapture && upEvent) {
          splitter.releasePointerCapture(upEvent.pointerId);
        }

        window.removeEventListener('pointermove', onMove);
        window.removeEventListener('pointerup', stopDrag);
        window.removeEventListener('pointercancel', stopDrag);
      }

      window.addEventListener('pointermove', onMove);
      window.addEventListener('pointerup', stopDrag);
      window.addEventListener('pointercancel', stopDrag);
    });

    splitter.addEventListener('dblclick', function (event) {
      event.preventDefault();
      onReset();
    });
  }

  function init() {
    var page = document.querySelector('.page');
    var sidebar = document.querySelector('.sidebar-drawer');
    var main = document.querySelector('.main');
    var toc = document.querySelector('.toc-drawer');
    var content = main && main.querySelector('.content');
    var sidebarContainer = sidebar && sidebar.querySelector('.sidebar-container');

    if (!page || !sidebar || !main || !toc || !content) {
      return;
    }

    if (page.querySelector('.sidebar-splitter')) {
      return;
    }

    var leftSplitter = makeSplitter('left');
    var rightSplitter = makeSplitter('right');

    sidebar.parentNode.insertBefore(leftSplitter, sidebar.nextSibling);
    toc.parentNode.insertBefore(rightSplitter, toc);

    function pageWidth() {
      return page.clientWidth || document.documentElement.clientWidth || 1;
    }

    function clampPanelPercent(percent) {
      return clamp(percent, MIN_PANEL_PERCENT, MAX_PANEL_PERCENT);
    }

    function percentToWidth(percent) {
      return pageWidth() * clampPanelPercent(percent) / 100;
    }

    function widthToPercent(width) {
      return width / pageWidth() * 100;
    }

    function setFluidContent(enabled) {
      if (enabled) {
        content.style.flex = '1 1 auto';
        content.style.width = 'auto';
        content.style.minWidth = '0';
      } else {
        content.style.flex = '';
        content.style.width = '';
        content.style.minWidth = '';
      }
    }

    function setSidebarPercent(percent) {
      setFixedWidth(sidebar, percentToWidth(percent));
      if (sidebarContainer) {
        sidebarContainer.style.width = '100%';
      }
    }

    function clearSidebarWidth() {
      clearFixedWidth(sidebar);
      if (sidebarContainer) {
        sidebarContainer.style.width = '';
      }
    }

    function clearTocWidth() {
      clearFixedWidth(toc);
    }

    function currentSidebarPercent() {
      if (sidebar.style.width) {
        return widthToPercent(sidebar.offsetWidth);
      }
      return widthToPercent(
        sidebarContainer ? sidebarContainer.offsetWidth : sidebar.offsetWidth
      );
    }

    function currentTocPercent() {
      return widthToPercent(toc.offsetWidth);
    }

    function applyStoredWidths() {
      var leftPercent = readStoredPercent(LS_LEFT);
      var rightPercent = readStoredPercent(LS_RIGHT);
      var hasFluidPanel = false;

      if (isDrawerMode(sidebar)) {
        clearSidebarWidth();
        leftSplitter.hidden = true;
      } else {
        leftSplitter.hidden = false;
        if (leftPercent !== null) {
          setSidebarPercent(leftPercent);
          hasFluidPanel = true;
        } else {
          clearSidebarWidth();
        }
      }

      if (isDrawerMode(toc)) {
        clearTocWidth();
        rightSplitter.hidden = true;
      } else {
        rightSplitter.hidden = false;
        if (rightPercent !== null) {
          setFixedWidth(toc, percentToWidth(rightPercent));
          hasFluidPanel = true;
        } else {
          clearTocWidth();
        }
      }

      setFluidContent(hasFluidPanel);
    }

    applyStoredWidths();
    window.addEventListener('resize', applyStoredWidths);

    wireDrag(
      leftSplitter,
      function (dx) {
        if (isDrawerMode(sidebar)) {
          return;
        }

        var percent = clampPanelPercent(
          currentSidebarPercent() + widthToPercent(dx)
        );

        setSidebarPercent(percent);
        setFluidContent(true);
        writeStoredPercent(LS_LEFT, percent);
      },
      function () {
        removeStoredPercent(LS_LEFT);
        clearSidebarWidth();
        applyStoredWidths();
      }
    );

    wireDrag(
      rightSplitter,
      function (dx) {
        if (isDrawerMode(toc)) {
          return;
        }

        var percent = clampPanelPercent(
          currentTocPercent() - widthToPercent(dx)
        );

        setFixedWidth(toc, percentToWidth(percent));
        setFluidContent(true);
        writeStoredPercent(LS_RIGHT, percent);
      },
      function () {
        removeStoredPercent(LS_RIGHT);
        clearTocWidth();
        applyStoredWidths();
      }
    );
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
