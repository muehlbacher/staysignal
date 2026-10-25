// Guest feedback flow: step 1 (stars) → step 2 (rating-dependent follow-up) → thank you.
(function () {
  var flow = document.getElementById('flow');
  if (flow) initFlow(flow);
  var share = document.querySelector('[data-share]');
  if (share) initShare(share);

  function initFlow(form) {
    var labels = JSON.parse(form.dataset.stars);
    var radios = form.querySelectorAll('.star-input');
    var stars = form.querySelectorAll('.star');
    var words = form.querySelectorAll('[data-word]');
    var tapText = words[0].textContent;
    var textarea = form.querySelector('#message');
    var textLabel = form.querySelector('[data-text-label]');
    var contactToggle = form.querySelector('[data-contact-toggle]');
    var contactFields = form.querySelector('[data-contact-fields]');
    var sendBtn = form.querySelector('[data-send-btn]');
    var currentBand = null;

    if (history.length <= 1) form.classList.add('no-back');

    function rating() {
      var r = form.querySelector('.star-input:checked');
      return r ? +r.value : 0;
    }
    function paint(n) {
      stars.forEach(function (s) { s.classList.toggle('on', +s.dataset.n <= n); });
    }
    function bandOf(n) { return n <= 2 ? 'low' : n === 3 ? 'mid' : 'high'; }

    function setBand(b) {
      if (b === currentBand) return;
      currentBand = b;
      form.querySelectorAll('[data-band]').forEach(function (el) {
        var on = el.dataset.band === b;
        el.classList.toggle('active', on);
        // Picks from another band don't apply to the new rating.
        if (!on) el.querySelectorAll('input').forEach(function (i) { i.checked = false; });
      });
      form.querySelectorAll('[data-band-extra]').forEach(function (el) {
        var on = el.dataset.bandExtra === b;
        el.classList.toggle('active', on);
        if (!on) el.querySelectorAll('input[type=checkbox]').forEach(function (i) { i.checked = false; });
      });
      textLabel.textContent = textarea.dataset['label' + cap(b)];
      textarea.placeholder = textarea.dataset['ph' + cap(b)];
      syncContact();
    }
    function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

    function syncContact() {
      var open = contactToggle.checked;
      contactFields.classList.toggle('open', open);
      contactFields.querySelector('[name=contact_info]').required = open;
    }

    function syncButton() {
      var extra = form.querySelector('[data-band].active input:checked, .opt-card.active input[type=checkbox]:checked') ||
        textarea.value.trim();
      sendBtn.textContent = extra ? form.dataset.send : form.dataset.sendOnly;
    }

    function update() {
      var n = rating();
      paint(n);
      words.forEach(function (w, i) { w.textContent = n ? labels[n - 1] : (i === 0 ? tapText : ''); });
      if (n) setBand(bandOf(n));
      syncButton();
    }

    function go(step) {
      form.classList.toggle('at-2', step === 2);
      window.scrollTo(0, 0);
    }

    radios.forEach(function (r) {
      r.addEventListener('change', function () {
        update();
        // Give the filled stars a beat before moving on.
        if (!form.classList.contains('at-2')) setTimeout(function () { go(2); }, 220);
      });
    });

    // Hover preview on step 1 only (desktop).
    form.querySelectorAll('.stars-lg .star').forEach(function (s) {
      s.addEventListener('mouseenter', function () { paint(+s.dataset.n); words[0].textContent = labels[s.dataset.n - 1]; });
      s.addEventListener('mouseleave', update);
    });

    form.addEventListener('change', syncButton);
    textarea.addEventListener('input', syncButton);
    contactToggle.addEventListener('change', syncContact);
    form.querySelector('[data-back]').addEventListener('click', function () { go(1); });
    form.querySelector('[data-close]').addEventListener('click', function () { history.back(); });

    update();
  }

  function initShare(card) {
    var btn = card.querySelector('[data-copy]');
    btn.addEventListener('click', function () {
      var text = btn.dataset.copy;
      if (text && navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function () { btn.textContent = btn.dataset.copied; }, function () {});
      }
    });
    var done = card.querySelector('[data-done]');
    done.addEventListener('click', function (e) {
      e.preventDefault();
      card.classList.add('done');
      card.innerHTML = '';
      var p = document.createElement('p');
      p.textContent = done.dataset.done;
      card.appendChild(p);
    });
  }
})();
