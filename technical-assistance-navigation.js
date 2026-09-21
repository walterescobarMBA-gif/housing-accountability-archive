/* Add a single technical-assistance link to HAA's existing navigation and footer.
   Uses the existing site navigation patterns; no analytics or external requests. */
(function () {
  'use strict';
  var page = 'technical-assistance.html';
  var navs = document.querySelectorAll('.site-nav, .primary-nav');
  navs.forEach(function (nav) {
    if (nav.querySelector('a[href="' + page + '"]')) return;
    var link = document.createElement('a');
    link.href = page;
    link.textContent = 'Technical Assistance';
    if (location.pathname.endsWith('/' + page)) link.setAttribute('aria-current', 'page');
    var before = nav.querySelector('a[href="confidentiality.html"], a[href="contact.html"]');
    if (before) nav.insertBefore(link, before);
    else nav.appendChild(link);
  });
})();
