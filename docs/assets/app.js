/* zixuann blog: theme, search, progress, toc, menu */
(function () {
  const root = document.documentElement;

  // theme（柔和渐变切换）
  const themeBtn = document.getElementById("theme-toggle");
  function enableThemeAnim() {
    root.classList.add("theme-anim");
    clearTimeout(enableThemeAnim._t);
    enableThemeAnim._t = setTimeout(() => root.classList.remove("theme-anim"), 700);
  }
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      enableThemeAnim();
      const dark = root.classList.toggle("dark");
      try { localStorage.setItem("theme", dark ? "dark" : "light"); } catch (e) {}
    });
  }

  // mobile menu
  const menuBtn = document.getElementById("menu-toggle");
  const mobileNav = document.getElementById("mobile-nav");
  if (menuBtn && mobileNav) {
    menuBtn.addEventListener("click", () => mobileNav.classList.toggle("open"));
  }

  // liquid glass: static shine only (no moving light)

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

  // search
  const modal = document.getElementById("search-modal");
  const openBtn = document.getElementById("search-open");
  const input = document.getElementById("search-input");
  const results = document.getElementById("search-results");
  let index = null;
  const indexUrl = "/search-index.json";

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

  function render(items) {
    if (!results) return;
    if (!items.length) {
      results.innerHTML = '<a href="#">没有找到相关内容</a>';
      return;
    }
    results.innerHTML = items
      .slice(0, 12)
      .map(
        (it) =>
          `<a href="${it.url}"><div>${it.title}</div><div class="meta">${it.date || ""} · ${(
            it.tags || []
          ).map((t) => "#" + t).join(" ")}</div></a>`
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
    modal.hidden = false;
    loadIndex().then(() => doSearch(""));
    setTimeout(() => input && input.focus(), 30);
  }
  function closeSearch() {
    if (modal) modal.hidden = true;
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
