// Keep the same research, advocacy and support destinations on older static pages.
document.querySelectorAll(".site-nav").forEach((navigation) => {
  const destinations = [
    ["index.html","Home"],["findings.html","Findings"],["publications.html","Publications"],
    ["participant-support.html#advocacy","Participant Advocacy"],["learn.html","Learn"],
    ["records-verification.html","Records Verification"],["about.html","About"],["contact.html","Contact"]
  ];
  const oldLinks = Array.from(navigation.querySelectorAll("a"));
  const page = window.location.pathname.split("/").pop() || "index.html";
  const support = oldLinks.find(a=>a.hasAttribute("data-haa-support") || a.href==="https://ko-fi.com/housingaccountabilityarchive");
  navigation.textContent = "";
  destinations.forEach(([href,label])=>{
    const link=document.createElement("a");
    link.href=href; link.textContent=label;
    if(page===href.split("#")[0])link.setAttribute("aria-current","page");
    navigation.append(link);
  });
  const link = support || document.createElement("a");
  link.href="https://ko-fi.com/housingaccountabilityarchive";link.textContent="Support HAA";
  link.target="_blank";link.rel="noopener noreferrer";link.dataset.haaSupport="";
  navigation.append(link);
});

// Add a consistent, accessible Ko-fi support link across HAA pages.
const haaSupportUrl = "https://ko-fi.com/housingaccountabilityarchive";

document.querySelectorAll(".site-nav").forEach((navigation) => {
  if (navigation.querySelector('a[data-haa-support], a[href="' + haaSupportUrl + '"]')) return;
  const supportLink = document.createElement("a");
  supportLink.href = haaSupportUrl;
  supportLink.textContent = "Support HAA";
  supportLink.target = "_blank";
  supportLink.rel = "noopener noreferrer";
  supportLink.dataset.haaSupport = "";
  navigation.append(supportLink);
});

document.querySelectorAll(".site-footer").forEach((footer) => {
  if (footer.querySelector('a[data-haa-support], a[href="' + haaSupportUrl + '"]')) return;
  const destination = footer.querySelector(".footer-inner") || footer;
  const paragraph = document.createElement("p");
  paragraph.className = "haa-footer-support";
  paragraph.append("Help sustain independent investigations and housing rights advocacy: ");
  const link = document.createElement("a");
  link.href = haaSupportUrl;
  link.textContent = "Support HAA on Ko-fi";
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.dataset.haaSupport = "";
  paragraph.append(link);
  destination.append(paragraph);
});


// Present a visually grouped mobile menu while preserving the desktop navigation.
document.querySelectorAll(".site-nav").forEach((navigation) => {
  if (navigation.querySelector(".nav-section-label")) return;

  const findLink = (label) => Array.from(navigation.querySelectorAll("a"))
    .find((link) => link.textContent.trim() === label);

  // Keep learning resources together, with verification before general learning.
  const recordsLink = findLink("Records Verification");
  const learnLink = findLink("Learn");
  if (recordsLink && learnLink) navigation.insertBefore(recordsLink, learnLink);

  [
    { before: "Home", label: "Explore HAA" },
    { before: "Findings", label: "Investigations & Evidence" },
    { before: "Participant Advocacy", label: "Participant advocacy" },
    { before: "Contact", label: "Connect & Support" }
  ].forEach(({ before, label }) => {
    const link = findLink(before);
    if (!link) return;
    const heading = document.createElement("span");
    heading.className = "nav-section-label";
    heading.textContent = label;
    heading.setAttribute("aria-hidden", "true");
    navigation.insertBefore(heading, link);
  });
});

const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");

if (menuToggle && siteNav) {
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && siteNav.classList.contains("is-open")) {
      siteNav.classList.remove("is-open");
      menuToggle.setAttribute("aria-expanded", "false");
      menuToggle.setAttribute("aria-label", "Open navigation");
      menuToggle.focus();
    }
  });
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
