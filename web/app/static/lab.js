(function () {
  var root = document.getElementById("lab-root");
  if (!root) return;
  var labId = root.dataset.lab;
  var termUrl = root.dataset.term;
  var expires = new Date(root.dataset.expires);
  var statusEl = document.getElementById("lab-status");
  var timerEl = document.getElementById("lab-timer");
  var frame = document.getElementById("term-frame");
  var wait = document.getElementById("term-wait");
  var msg = document.getElementById("term-msg");
  var opened = false;

  function setStatus(s, message) {
    statusEl.textContent = s;
    statusEl.className = "pill pill-" + s;
    if (s === "running" && !opened) {
      opened = true;
      frame.src = termUrl;
      frame.hidden = false;
      wait.hidden = true;
    } else if (s === "error" || s === "stopped" || s === "expired") {
      frame.hidden = true;
      wait.hidden = false;
      wait.querySelector(".spinner").hidden = true;
      msg.textContent = s === "error" ? "Xatolik: " + (message || "noma'lum") : "Laboratoriya yakunlangan (" + s + ").";
    }
  }

  function poll() {
    fetch("/labs/" + labId + "/status.json", { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        setStatus(d.status, d.message);
        if (d.status === "provisioning") setTimeout(poll, 3000);
      })
      .catch(function () { setTimeout(poll, 5000); });
  }

  function tick() {
    var left = Math.max(0, Math.floor((expires - new Date()) / 1000));
    var m = Math.floor(left / 60), s = left % 60;
    timerEl.textContent = m + ":" + (s < 10 ? "0" : "") + s;
    if (left === 0) setStatus("expired");
    else setTimeout(tick, 1000);
  }

  var btn = document.getElementById("btn-check");
  if (btn) {
    btn.addEventListener("click", function () {
      btn.disabled = true;
      btn.textContent = "Tekshirilmoqda…";
      fetch("/labs/" + labId + "/check", { method: "POST", credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d.error) { document.getElementById("check-summary").textContent = d.error; return; }
          (d.results || []).forEach(function (r) {
            var li = document.querySelector('#check-list li[data-id="' + r.id + '"]');
            if (!li) return;
            li.className = r.ok ? "ok" : "fail";
            li.querySelector(".mark").textContent = r.ok ? "✔" : "✘";
            li.title = r.output || "";
          });
          document.getElementById("check-summary").textContent = d.passed + "/" + d.total + " bajarildi" + (d.passed === d.total ? " 🎉" : "");
        })
        .catch(function () { document.getElementById("check-summary").textContent = "Tekshirishda xatolik"; })
        .finally(function () { btn.disabled = false; btn.textContent = "Tekshirish"; });
    });
  }

  setStatus(root.dataset.status);
  if (root.dataset.status === "provisioning") poll();
  tick();
})();
