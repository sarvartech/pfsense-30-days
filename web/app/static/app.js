(function () {
  if (window.hljs) {
    document.querySelectorAll(".prose pre code").forEach(function (el) { window.hljs.highlightElement(el); });
  }
  if (window.mermaid) {
    var dark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    window.mermaid.initialize({ startOnLoad: true, theme: dark ? "dark" : "default", securityLevel: "strict" });
  }
})();
