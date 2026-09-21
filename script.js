const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");

// Surface the new technical-assistance offering in the existing navigation.
// The page also includes a static link for browsers without JavaScript.
if (siteNav && !siteNav.querySelector('a[href="technical-assistance.html"]')) {
  const assistanceLink = document.createElement("a");
  assistanceLink.href = "technical-assistance.html";
  assistanceLink.textContent = "Technical Assistance";
  const confidentialityLink = siteNav.querySelector('a[href="confidentiality.html"]');
  siteNav.insertBefore(assistanceLink, confidentialityLink || null);
}

if (menuToggle && siteNav) {
  menuToggle.addEventListener("click", () => {
    const isOpen = siteNav.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
  });
}

const archiveItems = [
  {
    type: "navigation",
    title: "Participant support",
    summary: "Participant-directed navigation for referral pathways, applications, administrative communication, documentation, and next steps.",
    href: "participant-support.html",
    keywords: "participant support navigation referral application administrative advocacy communication documentation"
  },
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
      buttons.forEach((candidate) => {
        const selected = candidate === button;
        candidate.classList.toggle("active", selected);
        candidate.setAttribute("aria-pressed", String(selected));
      });
      render();
    });
  });

  search.addEventListener("input", render);
  render();
}

renderArchiveExplorer();
