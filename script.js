const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");

if (menuToggle && siteNav) {
  const closeNavigation = ({ returnFocus = false } = {}) => {
    siteNav.classList.remove("is-open");
    menuToggle.setAttribute("aria-expanded", "false");
    menuToggle.setAttribute("aria-label", "Open navigation");
    if (returnFocus) menuToggle.focus();
  };

  menuToggle.addEventListener("click", () => {
    const isOpen = siteNav.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
  });

  siteNav.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeNavigation();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && siteNav.classList.contains("is-open")) {
      closeNavigation({ returnFocus: true });
    }
  });
}

function setupArchiveExplorer() {
  const explorer = document.querySelector("[data-archive-explorer]");
  if (!explorer) return;

  const search = explorer.querySelector("[data-archive-search]");
  const count = explorer.querySelector("[data-archive-count]");
  const countLabel = explorer.querySelector("[data-archive-count-label]");
  const empty = explorer.querySelector("[data-archive-empty]");
  const buttons = Array.from(explorer.querySelectorAll("[data-archive-filter]"));
  const items = Array.from(explorer.querySelectorAll("[data-archive-item]"));

  if (!search || !count || !countLabel || !empty || buttons.length === 0 || items.length === 0) return;

  let activeFilter = "all";

  const setActiveButton = (activeButton) => {
    activeFilter = activeButton.dataset.archiveFilter || "all";
    buttons.forEach((button) => {
      const isActive = button === activeButton;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
      button.tabIndex = isActive ? 0 : -1;
    });
  };

  const applyFilters = () => {
    const query = search.value.trim().toLowerCase();
    let visibleCount = 0;

    items.forEach((item) => {
      const type = item.dataset.type || "";
      const haystack = `${item.textContent} ${item.dataset.keywords || ""}`.toLowerCase();
      const matchesFilter = activeFilter === "all" || type === activeFilter;
      const matchesSearch = !query || haystack.includes(query);
      const isVisible = matchesFilter && matchesSearch;
      item.hidden = !isVisible;
      if (isVisible) visibleCount += 1;
    });

    count.textContent = String(visibleCount);
    countLabel.textContent = visibleCount === 1 ? " matching pathway" : " matching pathways";
    const hasCriteria = Boolean(query) || activeFilter !== "all";
    empty.hidden = visibleCount > 0 || !hasCriteria;
  };

  const activateFilter = (button) => {
    setActiveButton(button);
    if (activeFilter === "all") search.value = "";
    applyFilters();
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => activateFilter(button));
  });

  explorer.querySelector(".filter-bar")?.addEventListener("keydown", (event) => {
    const currentButton = event.target.closest("[data-archive-filter]");
    if (!currentButton) return;

    const currentIndex = buttons.indexOf(currentButton);
    let nextIndex;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") nextIndex = (currentIndex + 1) % buttons.length;
    if (event.key === "ArrowLeft" || event.key === "ArrowUp") nextIndex = (currentIndex - 1 + buttons.length) % buttons.length;
    if (event.key === "Home") nextIndex = 0;
    if (event.key === "End") nextIndex = buttons.length - 1;
    if (nextIndex === undefined) return;

    event.preventDefault();
    const nextButton = buttons[nextIndex];
    activateFilter(nextButton);
    nextButton.focus();
  });

  search.addEventListener("input", applyFilters);

  explorer.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || (!search.value && activeFilter === "all")) return;
    event.preventDefault();
    search.value = "";
    setActiveButton(buttons[0]);
    applyFilters();
    search.focus();
  });

  applyFilters();
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
      buttons.forEach((candidate) => candidate.setAttribute("aria-pressed", String(candidate === button)));
      applyFilter();
    });
  });

  search.addEventListener("input", applyFilter);
  applyFilter();
}

setupArchiveExplorer();
setupFilterableCards();
