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
    // 折行禁则：收尾标点并入前一字，开引号并入后一字
    const CLOSE = "、，。：；！？）】」』》〉”’…～·";
    const OPEN = "（【「『《〈“‘";
    const walk = (parent) => {
      Array.from(parent.childNodes).forEach((child) => {
        if (child.nodeType === Node.TEXT_NODE) {
          const text = child.textContent || "";
          if (!text.trim()) return;
          const fragment = document.createDocumentFragment();
          const tokens = text.match(/[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*|[\s\S]/gu) || [];
          let openSpan = null;
          tokens.forEach((token) => {
            if (/^\s+$/.test(token)) {
              openSpan = null;
              fragment.appendChild(document.createTextNode(token));
              return;
            }
            if (openSpan) {
              openSpan.textContent += token;
              openSpan = null;
              return;
            }
            const previous = fragment.lastChild;
            if (
              CLOSE.includes(token) &&
              previous &&
              previous.nodeType === Node.ELEMENT_NODE &&
              previous.classList.contains("split-char")
            ) {
              previous.textContent += token;
              return;
            }
            const span = document.createElement("span");
            span.className = "split-char";
            span.style.setProperty("--char-index", String(index++));
            span.textContent = token;
            fragment.appendChild(span);
            if (OPEN.includes(token)) openSpan = span;
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

    // 滑动红条：弹簧积分驱动 transform/height，速度越快轻微拉伸
    const rails = Array.from(document.querySelectorAll(".toc-nav")).map((nav) => {
      const bar = document.createElement("span");
      bar.className = "toc-indicator";
      bar.setAttribute("aria-hidden", "true");
      nav.appendChild(bar);
      return { nav, bar };
    });
    const motionOff = window.matchMedia("(prefers-reduced-motion: reduce)");
    const springs = new WeakMap();
    const springsOf = (bar) => {
      let spring = springs.get(bar);
      if (!spring) {
        spring = { y: 0, h: 0, vy: 0, vh: 0, ty: 0, th: 0, raf: 0, last: 0 };
        springs.set(bar, spring);
      }
      return spring;
    };
    const paintBar = (rail, link, animate = true) => {
      if (!rail) return;
      const { bar } = rail;
      if (!link) {
        bar.classList.remove("is-on");
        return;
      }
      const spring = springsOf(bar);
      const targetY = link.offsetTop;
      const targetH = link.offsetHeight;
      const fresh = !bar.classList.contains("is-on");
      bar.classList.add("is-on");

      if (!animate || motionOff.matches) {
        spring.y = spring.ty = targetY;
        spring.h = spring.th = targetH;
        spring.vy = spring.vh = 0;
        bar.style.setProperty("--toc-y", targetY + "px");
        bar.style.setProperty("--toc-h", targetH + "px");
        bar.style.setProperty("--toc-stretch", "1");
        return;
      }

      spring.ty = targetY;
      spring.th = targetH;
      if (fresh) {
        spring.y = targetY;
        spring.h = 0;
        spring.vy = 0;
        spring.vh = 0;
      }
      if (spring.raf) return;

      const step = (now) => {
        const dt = Math.min(0.034, Math.max(0.001, (now - (spring.last || now)) / 1000));
        spring.last = now;
        // 位置：欠阻尼弹簧，收尾带一点回弹
        spring.vy += (-176 * (spring.y - spring.ty) - 21 * spring.vy) * dt;
        spring.y += spring.vy * dt;
        // 高度：更紧一些，避免条子变形拖太久
        spring.vh += (-230 * (spring.h - spring.th) - 30 * spring.vh) * dt;
        spring.h += spring.vh * dt;
        // 速度越快，竖向轻微拉伸（最多 18%）
        const stretch = 1 + Math.min(0.14, Math.abs(spring.vy) * 0.00085 + Math.abs(spring.vh) * 0.0004);
        bar.style.setProperty("--toc-y", spring.y.toFixed(2) + "px");
        bar.style.setProperty("--toc-h", Math.max(0, spring.h).toFixed(2) + "px");
        bar.style.setProperty("--toc-stretch", stretch.toFixed(3));
        const settled =
          Math.abs(spring.y - spring.ty) < 0.12 &&
          Math.abs(spring.vy) < 1.5 &&
          Math.abs(spring.h - spring.th) < 0.12 &&
          Math.abs(spring.vh) < 1.5;
        if (settled) {
          spring.y = spring.ty;
          spring.h = spring.th;
          spring.vy = spring.vh = 0;
          bar.style.setProperty("--toc-y", spring.ty + "px");
          bar.style.setProperty("--toc-h", spring.th + "px");
          bar.style.setProperty("--toc-stretch", "1");
          spring.raf = 0;
          spring.last = 0;
          return;
        }
        spring.raf = requestAnimationFrame(step);
      };
      spring.last = 0;
      spring.raf = requestAnimationFrame(step);
    };
    const syncBars = (animate) => {
      rails.forEach((rail) => paintBar(rail, rail.nav.querySelector("a.active"), animate));
    };
    rails.forEach((rail) => paintBar(rail, rail.nav.querySelector("a.active"), false));
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => syncBars(false)).catch(() => {});
    }
    let resizeTimer = 0;
    window.addEventListener("resize", () => {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(() => syncBars(false), 160);
    }, { passive: true });

    // 悬停时红条先滑到指针下的条目，移出后回到当前章节
    rails.forEach((rail) => {
      rail.nav.addEventListener("pointerover", (event) => {
        const link = event.target instanceof Element ? event.target.closest("a") : null;
        if (link && rail.nav.contains(link)) paintBar(rail, link, true);
      });
      rail.nav.addEventListener("pointerleave", () => paintBar(rail, rail.nav.querySelector("a.active"), true));
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
          syncBars(true);
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

/* ===== v6 · cinema interactions ===== */
(function () {
  "use strict";
  const root = document.documentElement;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const fine = window.matchMedia("(pointer: fine)").matches;

  // HUD 时钟
  const clocks = document.querySelectorAll("[data-clock]");
  if (clocks.length) {
    const pad = (n) => String(n).padStart(2, "0");
    const paint = () => {
      const now = new Date();
      const text = pad(now.getHours()) + ":" + pad(now.getMinutes()) + ":" + pad(now.getSeconds());
      clocks.forEach((node) => { node.textContent = text; });
    };
    paint();
    window.setInterval(paint, 1000);
  }

  // 数字滚动
  const counters = Array.from(document.querySelectorAll("[data-count]"));
  if (counters.length) {
    const animate = (node) => {
      const target = parseInt(node.dataset.count, 10);
      if (!Number.isFinite(target) || reduce.matches) return;
      const start = performance.now();
      const duration = 1100;
      const step = (now) => {
        const t = Math.min(1, (now - start) / duration);
        const eased = 1 - Math.pow(1 - t, 3);
        node.textContent = String(Math.round(target * eased)).padStart(2, "0");
        if (t < 1) requestAnimationFrame(step);
        else node.textContent = String(target).padStart(2, "0");
      };
      node.textContent = "00";
      requestAnimationFrame(step);
    };
    if ("IntersectionObserver" in window && !reduce.matches) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          animate(entry.target);
          io.unobserve(entry.target);
        });
      }, { threshold: 0.4 });
      counters.forEach((node) => io.observe(node));
    } else {
      counters.forEach(animate);
    }
  }

  if (!reduce.matches && fine) {
    // 磁吸按钮
    Array.from(document.querySelectorAll(".button-primary, .round-link")).forEach((node) => {
      node.classList.add("magnetic");
      node.addEventListener("pointermove", (event) => {
        const rect = node.getBoundingClientRect();
        const dx = (event.clientX - (rect.left + rect.width / 2)) / rect.width;
        const dy = (event.clientY - (rect.top + rect.height / 2)) / rect.height;
        node.classList.add("is-pulling");
        node.style.transform = "translate3d(" + (dx * 8).toFixed(2) + "px," + (dy * 6).toFixed(2) + "px,0)";
      });
      node.addEventListener("pointerleave", () => {
        node.classList.remove("is-pulling");
        node.style.transform = "";
      });
    });

    // 3D 倾斜
    Array.from(document.querySelectorAll("[data-tilt]")).forEach((node) => {
      let queued = false;
      let rx = 0;
      let ry = 0;
      node.addEventListener("pointermove", (event) => {
        const rect = node.getBoundingClientRect();
        const px = (event.clientX - rect.left) / rect.width - 0.5;
        const py = (event.clientY - rect.top) / rect.height - 0.5;
        rx = (py * -4).toFixed(2);
        ry = (px * 5).toFixed(2);
        if (queued) return;
        queued = true;
        requestAnimationFrame(() => {
          queued = false;
          node.classList.add("is-tilting");
          node.style.setProperty("--ty", rx + "deg");
          node.style.setProperty("--tx", ry + "deg");
        });
      });
      node.addEventListener("pointerleave", () => {
        node.classList.remove("is-tilting");
        node.style.removeProperty("--tx");
        node.style.removeProperty("--ty");
      });
    });
  }

  // 跑马灯随滚动速度倾斜
  const ticker = document.querySelector(".motion-ticker");
  if (ticker && !reduce.matches) {
    let last = window.scrollY;
    let skew = 0;
    let raf = 0;
    const tick = () => {
      skew *= 0.88;
      ticker.style.setProperty("--tick-skew", skew.toFixed(2) + "deg");
      if (Math.abs(skew) > 0.05) raf = requestAnimationFrame(tick);
      else raf = 0;
    };
    window.addEventListener("scroll", () => {
      const y = window.scrollY;
      const delta = y - last;
      last = y;
      skew = Math.max(-3.5, Math.min(3.5, delta * 0.35));
      if (!raf) raf = requestAnimationFrame(tick);
    }, { passive: true });
  }

  // 主题切换：圆形擦除（不支持时交还给原有逻辑）
  const themeButton = document.getElementById("theme-toggle");
  if (
    themeButton &&
    typeof document.startViewTransition === "function" &&
    !reduce.matches
  ) {
    document.addEventListener(
      "click",
      (event) => {
        const target = event.target instanceof Element ? event.target.closest("#theme-toggle") : null;
        if (!target) return;
        event.preventDefault();
        event.stopImmediatePropagation();

        const rect = target.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;
        const radius = Math.hypot(
          Math.max(x, window.innerWidth - x),
          Math.max(y, window.innerHeight - y)
        );
        const meta = document.querySelector('meta[name="theme-color"]');

        root.classList.add("theme-swap");
        const transition = document.startViewTransition(() => {
          const dark = root.classList.toggle("dark");
          try { localStorage.setItem("theme", dark ? "dark" : "light"); } catch (error) {}
          target.setAttribute("aria-label", dark ? "切换到浅色主题" : "切换到深色主题");
          target.setAttribute("aria-pressed", String(dark));
          if (meta) meta.setAttribute("content", dark ? "#0d1115" : "#f1ede4");
        });
        transition.ready
          .then(() => {
            const ease = "cubic-bezier(0.65, 0, 0.35, 1)";
            root.animate(
              { clipPath: ["circle(" + radius + "px at " + x + "px " + y + "px)", "circle(0px at " + x + "px " + y + "px)"] },
              { duration: 560, easing: ease, pseudoElement: "::view-transition-old(root)" }
            );
            root.animate(
              { clipPath: ["circle(0px at " + x + "px " + y + "px)", "circle(" + radius + "px at " + x + "px " + y + "px)"] },
              { duration: 560, easing: ease, pseudoElement: "::view-transition-new(root)" }
            );
          })
          .catch(() => {});
        transition.finished
          .then(() => root.classList.remove("theme-swap"))
          .catch(() => root.classList.remove("theme-swap"));
      },
      true
    );
  }
})();