/* Gozo Cottage – tiny progressive enhancement (inlined by tools/build.py) */
(function () {
  var menu = document.querySelector("details.menu");
  if (!menu) return;
  menu.addEventListener("click", function (e) {
    if (e.target.closest("a")) menu.removeAttribute("open");
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") menu.removeAttribute("open");
  });
})();
