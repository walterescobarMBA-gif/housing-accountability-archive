const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");

if (menuToggle && siteNav) {
  menuToggle.addEventListener("click", () => {
    const isOpen = siteNav.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
  });

  siteNav.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      siteNav.classList.remove("is-open");
      menuToggle.setAttribute("aria-expanded", "false");
      menuToggle.setAttribute("aria-label", "Open navigation");
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && siteNav.classList.contains("is-open")) {
      siteNav.classList.remove("is-open");
      menuToggle.setAttribute("aria-expanded", "false");
      menuToggle.setAttribute("aria-label", "Open navigation");
      menuToggle.focus();
    }
  });
}

const archiveItems = [
  {
    type: "site",
    title: "Housing Accountability Archive",
    summary: "The public homepage for HAA's educational resources, records methodology, confidentiality safeguards, and current-review status.",
    href: "index.html",
    keywords: "home housing accountability archive public interest records literacy"
  },
  {
    type: "site",
    title: "About",
    summary: "An overview of Publicly Funded Housing Program Administration as the subject of HAA's current review series.",
    href: "about.html",
    keywords: "about current review series publicly funded housing program administration"
  },
  {
    type: "learn",
    title: "What Housing Accountability Archive Is",
    summary: "HAA's independent role, public-interest purpose, limits, review method, and confidentiality principles.",
    href: "about-haa.html",
    keywords: "about HAA independent participant founded methodology limits confidentiality"
  },
  {
    type: "learn",
    title: "HAA Learning Center",
    summary: "Evergreen guides to housing administration, supportive services, participant pathways, documentation, and accountability.",
    href: "learn.html",
    keywords: "learn education administration supportive services participant pathway documentation accountability"
  },
  {
    type: "review",
    title: "Current review status",
    summary: "A neutral status page for the unpublished review's records-development and reconciliation process.",
    href: "current-review.html",
    keywords: "current review oversight routing stabilization controls"
  },
  {
    type: "review",
    title: "Administrative Oversight Referral HAA-OR-2026-001",
    summary: "A public procedural-status entry for a referral submitted to the Los Angeles City Controller.",
    href: "oversight-action-haa-or-2026-001.html",
    keywords: "oversight action referral controller FWA0003652 pending intake review"
  },
  {
    type: "records",
    title: "Methodology and Records Verification",
    summary: "HAA's source hierarchy, verification statuses, response and correction process, version control, and publication limits.",
    href: "records-verification.html",
    keywords: "methodology records verification sources status response correction version publication limits"
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
    title: "How Publicly Funded Housing Administration Works",
    summary: "A plain-language guide to federal authorization, local administration, project sponsors, delivery, monitoring, and participant records.",
    href: "housing-administration.html",
    keywords: "publicly funded housing administration authority grantee sponsor contractor oversight records"
  },
  {
    type: "framework",
    title: "Administrative Displacement",
    summary: "The related conceptual-framework initiative for examining when administrative process becomes a housing consequence.",
    href: "https://administrativedisplacement.org/",
    keywords: "administrative displacement related initiative conceptual framework housing consequence"
  },
  {
    type: "learn",
    title: "What Supportive Services Are Supposed to Accomplish",
    summary: "How assessed needs, service planning, delivery, referrals, follow-up, and outcomes can support housing stability.",
    href: "supportive-services.html",
    keywords: "supportive services needs plan provider referral delivery follow up housing stability"
  },
  {
    type: "learn",
    title: "What a Participant Pathway to Housing Stability Should Look Like",
    summary: "A flexible ten-stage pathway and HAA's clearly labeled Participant Pathway Feasibility framework.",
    href: "participant-pathway.html",
    keywords: "participant pathway feasibility intake assessment housing plan transition follow up stabilization"
  },
  {
    type: "records",
    title: "Why Documentation Matters",
    summary: "How administrative receipts support continuity, participant rights, provider management, oversight, and outcomes.",
    href: "documentation-matters.html",
    keywords: "documentation administrative receipts intake assessment case notes referrals outcomes"
  },
  {
    type: "learn",
    title: "How Administrative Accountability Benefits Participants and Providers",
    summary: "Accountability as a practical management and public-interest tool for participants, providers, funders, and oversight bodies.",
    href: "accountability-benefits.html",
    keywords: "accountability participants providers funders oversight management benefits"
  },
  {
    type: "site",
    title: "Contact",
    summary: "Public contact channels for corrections, responses, research, and records-verification correspondence.",
    href: "contact.html",
    keywords: "contact corrections response research records email"
  },
  {
    type: "site",
    title: "Updates",
    summary: "A concise version history for public site improvements and publication-status changes.",
    href: "updates.html",
    keywords: "updates version history site publication changes"
  },
  {
    type: "site",
    title: "Page Not Found",
    summary: "The archive's navigation page for an unavailable or incorrect public URL.",
    href: "404.html",
    keywords: "404 missing page not found return home"
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
      buttons.forEach((candidate) => candidate.setAttribute("aria-pressed", String(candidate === button)));
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
      buttons.forEach((candidate) => candidate.setAttribute("aria-pressed", String(candidate === button)));
      applyFilter();
    });
  });

  search.addEventListener("input", applyFilter);
  applyFilter();
}

renderArchiveExplorer();
setupFilterableCards();
