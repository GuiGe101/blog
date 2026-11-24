/* zixuann blog: theme, search, progress, toc, menu */
(function () {
  const root = document.documentElement;

  const main = document.querySelector(".main-col, .article-shell, .page.single");
  const skip = document.querySelector(".skip-link");
  if (main) {
    if (!main.id) main.id = "main";
    if (skip) skip.setAttribute("href", "#" + main.id);
  }

  // 运行天数：按访客本机时间实时计算
  (function () {
    const el = document.getElementById("run-days");
    if (!el) return;
    const start = el.getAttribute("data-start");
    if (!start) return;
    function tick() {
      const d0 = new Date(start + "T00:00:00");
      const now = new Date();
      if (Number.isNaN(d0.getTime())) return;
      const days = Math.max(1, Math.floor((now - d0) / 86400000) + 1);
      el.textContent = days + " 天";
    }
    tick();
    setInterval(tick, 60000);
  })();

  // theme（柔和渐变切换 + 图标随状态）
  const SUN =
    '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 3v2.2M12 18.8V21M3 12h2.2M18.8 12H21M5.6 5.6l1.6 1.6M16.8 16.8l1.6 1.6M18.4 5.6l-1.6 1.6M7.2 16.8l-1.6 1.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';
  const MOON =
    '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>';
  const themeBtn = document.getElementById("theme-toggle");
  function paintThemeIcon() {
    if (!themeBtn) return;
    const dark = root.classList.contains("dark");
    themeBtn.innerHTML = dark ? SUN : MOON;
    themeBtn.setAttribute("aria-label", dark ? "切换到浅色" : "切换到深色");
    themeBtn.title = dark ? "切换到浅色" : "切换到深色";
  }
  function enableThemeAnim() {
    root.classList.add("theme-anim");
    clearTimeout(enableThemeAnim._t);
    enableThemeAnim._t = setTimeout(() => root.classList.remove("theme-anim"), 700);
  }
  if (themeBtn) {
    paintThemeIcon();
    themeBtn.addEventListener("click", () => {
      enableThemeAnim();
      const dark = root.classList.toggle("dark");
      try { localStorage.setItem("theme", dark ? "dark" : "light"); } catch (e) {}
      paintThemeIcon();
    });
  }

  // mobile menu
  const menuBtn = document.getElementById("menu-toggle");
  const mobileNav = document.getElementById("mobile-nav");
  if (menuBtn && mobileNav) {
    function setMenu(open) {
      mobileNav.classList.toggle("open", open);
      mobileNav.hidden = !open;
      menuBtn.setAttribute("aria-expanded", String(open));
      menuBtn.setAttribute("aria-label", open ? "关闭菜单" : "打开菜单");
    }
    menuBtn.addEventListener("click", () => setMenu(mobileNav.hidden));
    mobileNav.addEventListener("click", (e) => {
      if (e.target.closest("a")) setMenu(false);
    });
    document.addEventListener("click", (e) => {
      if (!mobileNav.hidden && !mobileNav.contains(e.target) && !menuBtn.contains(e.target)) {
        setMenu(false);
      }
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !mobileNav.hidden) {
        setMenu(false);
        menuBtn.focus();
      }
    });
  }

  // reading progress
  const progress = document.getElementById("progress");
  function updateProgress() {
    if (!progress) return;
    const h = document.documentElement.scrollHeight - window.innerHeight;
    const p = h > 0 ? (window.scrollY / h) * 100 : 0;
    progress.style.width = p + "%";
  }
  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();

  // toc active state
  const tocLinks = Array.from(document.querySelectorAll(".toc a[href^='#']"));
  if (tocLinks.length) {
    const map = new Map();
    tocLinks.forEach((a) => {
      const id = a.getAttribute("href").slice(1);
      const el = document.getElementById(id);
      if (el) map.set(el, a);
    });
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) {
            tocLinks.forEach((a) => a.classList.remove("active"));
            const a = map.get(en.target);
            if (a) a.classList.add("active");
          }
        });
      },
      { rootMargin: "0px 0px -70% 0px", threshold: 0 }
    );
    map.forEach((_, el) => io.observe(el));
  }

  // 评论加载 watchdog：CDN 或 server 挂掉时给出可见状态，而不是空白
  (function () {
    const box = document.getElementById("waline") || document.querySelector(".giscus");
    const fallback = document.getElementById("echo-fallback");
    if (!box || !fallback) return;
    setTimeout(() => {
      if (!box.childElementCount) fallback.hidden = false;
    }, 8000);
  })();

  // search
  const modal = document.getElementById("search-modal");
  const openBtn = document.getElementById("search-open");
  const input = document.getElementById("search-input");
  const results = document.getElementById("search-results");
  let index = null;
  let searchReturnFocus = null;
  // 相对路径：根目录、posts/ 子目录、file:// 预览都能取到索引
  const indexUrl = document.currentScript
    ? new URL("../search-index.json", document.currentScript.src).href
    : "search-index.json";

  async function loadIndex() {
    if (index) return index;
    try {
      const res = await fetch(indexUrl);
      index = await res.json();
    } catch (e) {
      index = [];
    }
    return index;
  }

  const escape = (value) =>
    String(value || "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    })[char]);

  function render(items) {
    if (!results) return;
    if (!items.length) {
      results.innerHTML =
        '<p class="search-empty">没有找到相关内容<small>换个词，或按 ESC 关闭</small></p>';
      return;
    }
    results.innerHTML = items
      .slice(0, 12)
      .map(
        (it) =>
          `<a href="${escape(it.url)}"><div>${escape(it.title)}</div><div class="meta">${escape(it.date || "")} · ${(
            it.tags || []
          ).map((t) => "#" + escape(t)).join(" ")}</div></a>`
      )
      .join("");
  }

  async function doSearch(q) {
    const data = await loadIndex();
    q = (q || "").trim().toLowerCase();
    if (!q) {
      render(data.slice(0, 8));
      return;
    }
    const hit = data.filter((it) => {
      const blob = [it.title, it.summary, it.category, (it.tags || []).join(" ")]
        .join(" ")
        .toLowerCase();
      return blob.includes(q);
    });
    render(hit);
  }

  function openSearch() {
    if (!modal) return;
    searchReturnFocus = document.activeElement;
    modal.hidden = false;
    loadIndex().then(() => doSearch(input ? input.value : ""));
    setTimeout(() => input && input.focus(), 30);
  }
  function closeSearch() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    if (searchReturnFocus && searchReturnFocus.focus) searchReturnFocus.focus();
  }

  if (openBtn) openBtn.addEventListener("click", openSearch);
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeSearch();
    });
  }
  if (input) {
    input.addEventListener("input", () => doSearch(input.value));
  }
  document.addEventListener("keydown", (e) => {
    if (e.key === "k" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      openSearch();
    }
    if (e.key === "Escape") closeSearch();
  });
})();