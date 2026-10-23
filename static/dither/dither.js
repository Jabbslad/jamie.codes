// Halftone figures: post images start as a pre-dithered copy (signal green) and
// dissolve into the original when scrolled into view. The dissolve is a CSS
// animation over 17 tiny Bayer masks (see dither.css), so there is no per-frame
// pixel work. Without JS, or with reduced motion, the original image shows as normal.
(function () {
  var data = document.getElementById("dither-manifest");
  if (!data || !("IntersectionObserver" in window)) return;
  if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var manifest;
  try { manifest = JSON.parse(data.textContent); } catch (e) { return; }

  function reveal(fig, img) {
    var go = function () {
      if (document.hidden) {  // wait for the tab to be visible so the dissolve is seen
        document.addEventListener("visibilitychange", function once() {
          if (!document.hidden) { document.removeEventListener("visibilitychange", once); go(); }
        });
        return;
      }
      fig.classList.add("is-revealing");
      var layer = fig.querySelector(".dither-layer");
      var done = function () { fig.classList.remove("is-revealing"); fig.classList.add("is-revealed"); };
      layer.addEventListener("animationend", done, { once: true });
      setTimeout(done, 2000);  // never leave the original covered
    };
    var ready = img.complete && img.naturalWidth ? Promise.resolve()
      : (img.decode ? img.decode() : new Promise(function (r) { img.onload = r; }));
    ready.then(go, function () { fig.classList.add("is-revealed"); });
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      reveal(e.target, e.target.querySelector("img:not(.dither-layer)"));
    });
  }, { threshold: 0.35 });

  document.querySelectorAll("article section.body img").forEach(function (img) {
    var path;
    try { path = new URL(img.getAttribute("src"), location.href).pathname; } catch (e) { return; }
    var m = manifest[path];
    if (!m || img.closest(".dither-fig, .character-note")) return;
    var fig = document.createElement("span");
    fig.className = "dither-fig";
    fig.style.maxWidth = m.w + "px";
    fig.style.aspectRatio = m.w + " / " + m.h;
    var layer = document.createElement("img");
    layer.className = "dither-layer";
    layer.src = m.src;
    layer.alt = "";
    layer.setAttribute("aria-hidden", "true");
    layer.decoding = "async";
    var tag = document.createElement("span");
    tag.className = "dither-tag";
    tag.setAttribute("aria-hidden", "true");
    tag.textContent = "bayer 4x4";
    img.loading = "lazy";
    img.parentNode.insertBefore(fig, img);
    fig.appendChild(img);
    fig.appendChild(layer);
    fig.appendChild(tag);
    io.observe(fig);
  });
})();
