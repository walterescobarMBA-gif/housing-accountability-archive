const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");

if (menuToggle && siteNav) {
  menuToggle.addEventListener("click", () => {
    const isOpen = siteNav.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
  });
}

const archiveItems = [
  {
    type: "review",
    title: "Current review status",
    summary: "Open public-interest questions about oversight, review routing, records handling, and stabilization controls.",
    href: "current-review.html",
    keywords: "current review oversight routing stabilization controls"
  },
  {
    type: "records",
    title: "Records verification",
    summary: "How the archive distinguishes public summaries, redacted materials, controlled records, and private evidence.",
    href: "records-verification.html",
    keywords: "records verification redacted controlled private evidence public summary"
  },
  {
    type: "privacy",
    title: "Confidentiality protocol",
    summary: "Publication limits for sensitive participant-level records, health information, addresses, and third-party identities.",
    href: "confidentiality.html",
    keywords: "confidentiality privacy medical health participant records addresses"
  },
  {
    type: "framework",
    title: "Publicly Funded Housing Program Administration",
    summary: "A systems frame for reviewing administrative displacement and housing stability in publicly funded programs.",
    href: "about.html",
    keywords: "publicly funded housing program administration hopwa systems accountability"
  }
];

function renderArchiveExplorer() {
  const search = document.querySelector("[data-archive-search]");
  const results = document.querySelector("[data-archive-results]");
  const count = document.querySelector("[data-archive-count]");
  const buttons = Array.from(document.querySelectorAll("[data-archive-filter]"));

  if (!search || !results || !count || buttons.length === 0) return;

  let activeFilter = "all";

  const render = () => {
    const query = search.value.trim().toLowerCase();
    const matches = archiveItems.filter((item) => {
      const haystack = `${item.type} ${item.title} ${item.summary} ${item.keywords}`.toLowerCase();
      const matchesFilter = activeFilter === "all" || item.type === activeFilter;
      return matchesFilter && (!query || haystack.includes(query));
    });

    count.textContent = String(matches.length);
    results.innerHTML = "";

    if (matches.length === 0) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No matching pathway. Try a broader term or use All.";
      results.append(empty);
      return;
    }

    matches.forEach((item) => {
      const link = document.createElement("a");
      link.className = "archive-result";
      link.href = item.href;
      link.innerHTML = `<span>${item.type}</span><strong>${item.title}</strong><p>${item.summary}</p>`;
      results.append(link);
    });
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      activeFilter = button.dataset.archiveFilter || "all";
      buttons.forEach((candidate) => candidate.classList.toggle("is-active", candidate === button));
      render();
    });
  });

  search.addEventListener("input", render);
  render();
}

function setupFilterableCards() {
  const search = document.querySelector("[data-filter-search]");
  const count = document.querySelector("[data-filter-count]");
  const buttons = Array.from(document.querySelectorAll("[data-filter-button]"));
  const items = Array.from(document.querySelectorAll("[data-filter-item]"));

  if (!search || !count || buttons.length === 0 || items.length === 0) return;

  let activeFilter = "all";

  const applyFilter = () => {
    const query = search.value.trim().toLowerCase();
    let visibleCount = 0;

    items.forEach((item) => {
      const haystack = `${item.textContent} ${item.dataset.filterTags || ""}`.toLowerCase();
      const matchesFilter = activeFilter === "all" || haystack.includes(activeFilter);
      const matchesSearch = !query || haystack.includes(query);
      const isVisible = matchesFilter && matchesSearch;
      item.hidden = !isVisible;
      if (isVisible) visibleCount += 1;
    });

    count.textContent = String(visibleCount);
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      activeFilter = button.dataset.filterButton || "all";
      buttons.forEach((candidate) => candidate.classList.toggle("is-active", candidate === button));
      applyFilter();
    });
  });

  search.addEventListener("input", applyFilter);
  applyFilter();
}

renderArchiveExplorer();
setupFilterableCards();
