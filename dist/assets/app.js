/* 归舸的大窝 · interactions */
(function () {
  "use strict";

  const root = document.documentElement;
  const body = document.body;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const motionEnabled = !reduceMotion.matches;

  // Header elevation
  const header = document.getElementById("site-header");
  const onScroll = () => {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 8);
    updateProgress();
    requestSceneUpdate();
  };

  // Theme
  const themeButton = document.getElementById("theme-toggle");
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  function paintThemeState() {
    const dark = root.classList.contains("dark");
    if (themeButton) {
      themeButton.setAttribute("aria-label", dark ? "切换到浅色主题" : "切换到深色主题");
      themeButton.setAttribute("aria-pressed", String(dark));
    }
    if (themeMeta) themeMeta.setAttribute("content", dark ? "#0d1115" : "#f1ede4");
  }
  paintThemeState();
  if (themeButton) {
    themeButton.addEventListener("click", () => {
      root.classList.add("theme-anim");
      const dark = root.classList.toggle("dark");
      try { localStorage.setItem("theme", dark ? "dark" : "light"); } catch (error) {}
      paintThemeState();
      window.clearTimeout(themeButton._timer);
      themeButton._timer = window.setTimeout(() => root.classList.remove("theme-anim"), 450);
    });
  }

  // Mobile navigation
  const menuButton = document.getElementById("menu-toggle");
  const mobileNav = document.getElementById("mobile-nav");
  function setMenu(open) {
    if (!mobileNav || !menuButton) return;
    mobileNav.hidden = !open;
    body.classList.toggle("menu-open", open);
    menuButton.setAttribute("aria-expanded", String(open));
    menuButton.setAttribute("aria-label", open ? "关闭菜单" : "打开菜单");
  }
  if (menuButton && mobileNav) {
    menuButton.addEventListener("click", () => setMenu(mobileNav.hidden));
    mobileNav.addEventListener("click", (event) => {
      if (event.target.closest("a")) setMenu(false);
    });
    document.addEventListener("click", (event) => {
      if (!mobileNav.hidden && !mobileNav.contains(event.target) && !menuButton.contains(event.target)) {
        setMenu(false);
      }
    });
  }

  // Reading progress
  const progress = document.getElementById("progress");
  function updateProgress() {
    if (!progress) return;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = max > 0 ? ((window.scrollY / max) * 100).toFixed(3) + "%" : "0%";
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });

  // Cinematic hero scene
  const heroStage = document.querySelector(".hero-stage");
  const hero = document.querySelector(".home-hero");
  let sceneQueued = false;
  let pointerQueued = false;
  let pointerX = 0;
  let pointerY = 0;

  function updateScene() {
    if (!heroStage || !hero) return;
    if (!motionEnabled || window.innerWidth <= 820) {
      hero.style.setProperty("--hero-progress", "0");
      return;
    }
    const travel = Math.max(1, heroStage.offsetHeight - window.innerHeight);
    const progress = Math.min(1, Math.max(0, -heroStage.getBoundingClientRect().top / travel));
    hero.style.setProperty("--hero-progress", progress.toFixed(4));
  }
  function requestSceneUpdate() {
    if (sceneQueued || !heroStage) return;
    sceneQueued = true;
    const run = () => {
      if (!sceneQueued) return;
      sceneQueued = false;
      updateScene();
    };
    requestAnimationFrame(run);
    window.setTimeout(run, 32);
  }
  if (window.matchMedia("(pointer: fine)").matches && motionEnabled) {
    document.addEventListener(
      "pointermove",
      (event) => {
        pointerX = event.clientX;
        pointerY = event.clientY;
        body.classList.add("pointer-active");
        if (pointerQueued) return;
        pointerQueued = true;
        const paint = () => {
          if (!pointerQueued) return;
          pointerQueued = false;
          root.style.setProperty("--pointer-x", pointerX + "px");
          root.style.setProperty("--pointer-y", pointerY + "px");
        };
        requestAnimationFrame(paint);
        window.setTimeout(paint, 32);
      },
      { passive: true }
    );
    document.addEventListener("mouseleave", () => body.classList.remove("pointer-active"));
  }

  // Staggered character reveal
  function splitText(element) {
    let index = 0;
    const walk = (parent) => {
      Array.from(parent.childNodes).forEach((child) => {
        if (child.nodeType === Node.TEXT_NODE) {
          const text = child.textContent || "";
          if (!text.trim()) return;
          const fragment = document.createDocumentFragment();
          const tokens = text.match(/[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*|[\s\S]/gu) || [];
          tokens.forEach((token) => {
            if (/^\s+$/.test(token)) {
              fragment.appendChild(document.createTextNode(token));
              return;
            }
            const span = document.createElement("span");
            span.className = "split-char";
            span.style.setProperty("--char-index", String(index++));
            span.textContent = token;
            fragment.appendChild(span);
          });
          child.replaceWith(fragment);
        } else if (child.nodeType === Node.ELEMENT_NODE && child.tagName !== "BR") {
          walk(child);
        }
      });
    };
    walk(element);
    element.classList.add("is-split");
  }
  if (motionEnabled) {
    document.querySelectorAll("[data-split]").forEach(splitText);
    window.setTimeout(() => {
      document.querySelectorAll(".split-char").forEach((character) => {
        character.style.opacity = "1";
        character.style.transform = "none";
      });
    }, 2400);
  }

  // Scroll reveals
  function setupReveals() {
    if (!motionEnabled || !("IntersectionObserver" in window)) {
      root.classList.add("motion-loaded");
      return;
    }
    const selectors = [
      ".lead-story",
      ".latest-panel",
      ".journal-item",
      ".rail-card",
      ".collection-head > *",
      ".archive-year",
      ".taxonomy-group",
      ".entry-list li",
      ".page-prose > *",
      ".article-header > *",
      ".toc-mobile",
      ".article-cover",
      ".series-nav",
      ".article-prose > h2",
      ".article-prose > h3",
      ".article-prose > blockquote",
      ".article-prose > .code-block",
      ".article-prose > .table-wrap",
      ".article-footer",
      ".related",
      ".comments",
    ].join(",");
    const elements = Array.from(document.querySelectorAll(selectors));
    const counts = new Map();
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "320px 0px 320px 0px", threshold: 0 }
    );
    elements.forEach((element) => {
      const parent = element.parentElement;
      const index = counts.get(parent) || 0;
      counts.set(parent, index + 1);
      element.style.setProperty("--reveal-delay", Math.min(index, 3) * 30 + "ms");
      element.classList.add("will-reveal");
      observer.observe(element);
    });
    window.setTimeout(() => {
      elements.forEach((element) => {
        const rect = element.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
          element.classList.add("is-visible");
        }
      });
    }, 1800);
    root.classList.add("motion-loaded");
  }
  setupReveals();
  updateScene();
  onScroll();

  // Live day counter
  const runDays = document.getElementById("run-days");
  if (runDays) {
    const start = new Date((runDays.dataset.start || "") + "T00:00:00");
    const tick = () => {
      if (Number.isNaN(start.getTime())) return;
      const days = Math.max(1, Math.floor((Date.now() - start.getTime()) / 86400000) + 1);
      runDays.textContent = days + " 天";
    };
    tick();
    window.setInterval(tick, 60000);
  }

  // Table of contents
  const tocLinks = Array.from(document.querySelectorAll(".toc-nav a, .toc-mobile a"));
  if (tocLinks.length) {
    const targets = new Map();
    tocLinks.forEach((link) => {
      const id = link.getAttribute("href").slice(1);
      const target = document.getElementById(id);
      if (target && !targets.has(target)) {
        targets.set(target, link.getAttribute("href"));
      }
    });
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          const visible = entries.find((entry) => entry.isIntersecting);
          if (!visible) return;
          const href = "#" + visible.target.id;
          tocLinks.forEach((link) => {
            const active = link.getAttribute("href") === href;
            link.classList.toggle("active", active);
            if (active) link.setAttribute("aria-current", "location");
            else link.removeAttribute("aria-current");
          });
        },
        { rootMargin: "-12% 0px -72% 0px", threshold: 0 }
      );
      targets.forEach((_, target) => observer.observe(target));
    }
  }

  // Code copy
  document.querySelectorAll(".code-block").forEach((block) => {
    const button = block.querySelector(".code-copy");
    const code = block.querySelector("code");
    if (!button || !code) return;
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(code.textContent || "");
        button.textContent = "已复制";
      } catch (error) {
        button.textContent = "复制失败";
      }
      window.setTimeout(() => { button.textContent = "复制"; }, 1600);
    });
  });

  // Comments fallback
  const commentBox = document.getElementById("waline") || document.querySelector(".giscus");
  const commentFallback = document.querySelector("[data-comments-fallback]");
  if (commentBox && commentFallback) {
    window.setTimeout(() => {
      if (!commentBox.childElementCount) commentFallback.hidden = false;
    }, 8000);
  }

  // Search
  const modal = document.getElementById("search-modal");
  const openButton = document.getElementById("search-open");
  const input = document.getElementById("search-input");
  const results = document.getElementById("search-results");
  const command = modal ? modal.querySelector(".command") : null;
  const siteBase = document.currentScript ? new URL("../", document.currentScript.src) : new URL("./", location.href);
  const indexUrl = new URL("search-index.json", siteBase).href;
  let index = null;
  let returnFocus = null;
  let selected = -1;
  let hits = [];

  const escapeHtml = (value) =>
    String(value || "").replace(/[&<>"']/g, (character) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    })[character]);
  const iconArrow = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';

  async function loadIndex() {
    if (index) return index;
    try {
      const response = await fetch(indexUrl);
      index = response.ok ? await response.json() : [];
    } catch (error) {
      index = [];
    }
    return index;
  }

  function drawResults(items, query) {
    if (!results) return;
    hits = items.slice(0, 12);
    selected = -1;
    if (!hits.length) {
      results.innerHTML = '<p class="search-empty">' + (query ? "没有找到相关记录。换个词试试。" : "还没有文章。") + "</p>";
      return;
    }
    results.innerHTML = hits
      .map(
        (item, position) =>
          '<a class="search-result" role="option" aria-selected="false" href="' + new URL(item.url, siteBase).href + '">' +
          iconArrow +
          "<span><strong>" + escapeHtml(item.title) + "</strong><span>" +
          escapeHtml(item.date || "") + " · " + escapeHtml(item.category || "") +
          (item.tags || []).map((tag) => " · #" + escapeHtml(tag)).join("") +
          "</span></span></a>"
      )
      .join("");
  }

  async function search(query) {
    const data = await loadIndex();
    const clean = (query || "").trim().toLowerCase();
    if (!clean) {
      drawResults(data, false);
      return;
    }
    drawResults(
      data.filter((item) =>
        [item.title, item.summary, item.category, (item.tags || []).join(" ")]
          .join(" ")
          .toLowerCase()
          .includes(clean)
      ),
      true
    );
  }

  function selectResult(next) {
    if (!results || !hits.length) return;
    const links = Array.from(results.querySelectorAll(".search-result"));
    if (!links.length) return;
    selected = (next + links.length) % links.length;
    links.forEach((link, position) => {
      const active = position === selected;
      link.classList.toggle("is-selected", active);
      link.setAttribute("aria-selected", String(active));
      if (active) link.scrollIntoView({ block: "nearest" });
    });
  }

  function openSearch() {
    if (!modal) return;
    returnFocus = document.activeElement;
    modal.hidden = false;
    body.classList.add("search-open");
    loadIndex().then(() => search(input ? input.value : ""));
    window.setTimeout(() => input && input.focus(), 30);
  }

  function closeSearch() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    body.classList.remove("search-open");
    if (returnFocus && typeof returnFocus.focus === "function") returnFocus.focus();
  }

  if (openButton) openButton.addEventListener("click", openSearch);
  if (modal) {
    modal.querySelectorAll("[data-search-close]").forEach((button) => button.addEventListener("click", closeSearch));
  }
  if (input) {
    input.addEventListener("input", () => search(input.value));
    input.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        selectResult(selected + 1);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        selectResult(selected - 1);
      } else if (event.key === "Enter" && selected >= 0) {
        event.preventDefault();
        const link = results && results.querySelectorAll(".search-result")[selected];
        if (link) location.href = link.href;
      }
    });
  }
  if (command) {
    command.addEventListener("keydown", (event) => {
      if (event.key !== "Tab") return;
      const focusable = Array.from(command.querySelectorAll('button, input, a[href]')).filter(
        (node) => !node.hidden && node.offsetParent !== null
      );
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
  }
  document.addEventListener("keydown", (event) => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement && document.activeElement.tagName);
    if ((event.key === "k" || event.key === "K") && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      if (modal && modal.hidden) openSearch();
      else closeSearch();
    } else if (event.key === "/" && !typing && modal && modal.hidden) {
      event.preventDefault();
      openSearch();
    } else if (event.key === "Escape") {
      if (modal && !modal.hidden) closeSearch();
      else if (mobileNav && !mobileNav.hidden) {
        setMenu(false);
        menuButton && menuButton.focus();
      }
    }
  });

  // Abacus counters
  async function counter(kind, key) {
    const endpoint = "https://abacus.jasoncameron.dev/" + kind + "/" + (body.dataset.countNs || "") + "/" + key;
    try {
      const response = await fetch(endpoint, { signal: AbortSignal.timeout(6000) });
      if (!response.ok) return null;
      const data = await response.json();
      return data && data.value;
    } catch (error) {
      return null;
    }
  }
  function paintStat(selector, value) {
    document.querySelectorAll(selector).forEach((node) => {
      node.textContent = value == null ? "—" : value;
      node.title = value == null ? "计数服务暂时连不上" : "";
    });
  }
  async function initCounters() {
    if (!body.dataset.countNs) return;
    const pageKey = body.dataset.pageKey;
    const pageViews = document.querySelector("[data-page-views]");
    if (pageKey && pageViews) {
      const views = await counter("hit", "page-" + pageKey);
      pageViews.textContent = views == null ? "—" : views;
    }
    const siteViews = await counter("hit", "site-pv");
    paintStat('[data-stat="pv"]', siteViews);
    let seen = false;
    try { seen = localStorage.getItem("zixuann-visited") === "1"; } catch (error) {}
    const visitors = await counter(seen ? "get" : "hit", "site-uv");
    try { localStorage.setItem("zixuann-visited", "1"); } catch (error) {}
    paintStat('[data-stat="uv"]', visitors);
  }
  initCounters();
})();