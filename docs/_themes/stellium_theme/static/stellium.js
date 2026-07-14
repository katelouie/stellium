/* Stellium theme — theme toggle, mobile navigation, search shortcuts, scroll-spy.
 *
 * `data-theme` is set pre-paint by an inline script in layout.html (so there is no
 * flash of the wrong theme); this file only wires the interactions.
 */
(function () {
  "use strict";

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") === "dark"
      ? "dark"
      : "light";
  }

  function setTheme(mode) {
    document.documentElement.setAttribute("data-theme", mode);
    try {
      localStorage.setItem("stellium-theme", mode);
    } catch (e) {
      /* private mode / storage disabled — the toggle still works for this page */
    }
  }

  // ---------------------------------------------------------------------------
  // Mobile navigation.
  //
  // Below 760px the sidebar leaves the grid. The scaffold set `display:none` and
  // offered nothing in its place, which left a phone with no way to navigate the
  // site at all. It becomes a drawer instead.
  // ---------------------------------------------------------------------------
  function wireMobileNav() {
    var button = document.getElementById("st-menu-toggle");
    var sidebar = document.getElementById("st-sidebar");
    var scrim = document.getElementById("st-scrim");
    if (!button || !sidebar || !scrim) return;

    function setOpen(open) {
      document.documentElement.classList.toggle("st-nav-open", open);
      button.setAttribute("aria-expanded", String(open));
      scrim.hidden = !open;
      if (open) {
        var first = sidebar.querySelector("a"); // land a keyboard user somewhere useful
        if (first) first.focus();
      } else {
        button.focus();
      }
    }

    button.addEventListener("click", function () {
      setOpen(!document.documentElement.classList.contains("st-nav-open"));
    });
    scrim.addEventListener("click", function () {
      setOpen(false);
    });
    // Following a link must close the drawer, or the new page loads behind it.
    sidebar.addEventListener("click", function (event) {
      if (event.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") setOpen(false);
    });
    // Resizing back to desktop must not leave the drawer state stuck on.
    window.addEventListener("resize", function () {
      if (window.innerWidth > 760) setOpen(false);
    });
  }

  // ---------------------------------------------------------------------------
  // Search: "/" and ⌘K / Ctrl-K, as the token sheet promises.
  // ---------------------------------------------------------------------------
  function wireSearch() {
    var input = document.querySelector(".st-search input");
    if (!input) return;

    document.addEventListener("keydown", function (event) {
      var typingElsewhere =
        document.activeElement &&
        /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);

      var slash = event.key === "/" && !typingElsewhere;
      var cmdK = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k";

      if (slash || cmdK) {
        event.preventDefault();
        input.focus();
        input.select();
      }
      if (event.key === "Escape" && document.activeElement === input) {
        input.blur();
      }
    });
  }

  // ---------------------------------------------------------------------------
  // On-this-page: highlight the heading you are actually looking at.
  // ---------------------------------------------------------------------------
  function wireScrollSpy() {
    var links = Array.prototype.slice.call(
      document.querySelectorAll(".st-toc a[href^='#']")
    );
    if (!links.length || !("IntersectionObserver" in window)) return;

    var byId = {};
    var targets = [];
    links.forEach(function (link) {
      var id = decodeURIComponent(link.getAttribute("href").slice(1));
      var heading = document.getElementById(id);
      if (heading) {
        byId[id] = link;
        targets.push(heading);
      }
    });

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          links.forEach(function (l) {
            l.classList.remove("st-active");
          });
          var active = byId[entry.target.id];
          if (active) active.classList.add("st-active");
        });
      },
      // Fire when a heading reaches the band just under the sticky topbar.
      { rootMargin: "-70px 0px -75% 0px", threshold: 0 }
    );
    targets.forEach(function (t) {
      observer.observe(t);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("st-theme-toggle");
    if (toggle) {
      toggle.addEventListener("click", function () {
        setTheme(currentTheme() === "dark" ? "light" : "dark");
      });
    }
    wireMobileNav();
    wireSearch();
    wireScrollSpy();
  });
})();
