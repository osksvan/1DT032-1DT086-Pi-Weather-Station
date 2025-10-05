document.addEventListener("DOMContentLoaded", function() {
  const menuLinks = document.querySelectorAll("li.menu");

  menuLinks.forEach(link => {
    const linkPath = new URL(link.querySelector("a").getAttribute("href"), window.location.origin).pathname;
    if (window.location.pathname === linkPath) {
      link.classList.add("active");
    }
  });
});
