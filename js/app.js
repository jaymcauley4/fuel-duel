/* Fuel Duel — calculation engine */

const LITRES_PER_GALLON = 3.785411;
const FX_CC_MARKUP      = 1.0275;   // 2.75% above mid-market (Visa/MC + bank fee)
const TOLL_CAD          = 7.00;     // Sarnia → Port Huron
const TOLL_USD          = 5.00;     // Port Huron → Sarnia
const DEFAULT_TANK      = 60;
const PRICES_URL        = 'data/prices.json';

let fxRate  = null;
let prices  = null;
let tollsOn = true;

// ─── Init ─────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  const tankInput  = document.getElementById('tank');
  const tollToggle = document.getElementById('toll-toggle');

  // Single fetch — FX rate is bundled into prices.json by the scraper
  fetch(PRICES_URL)
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
    .then(data => {
      prices = data;
      fxRate = data.fx_usd_cad || null;
      if (!fxRate) {
        showError('FX rate unavailable. Run the scraper again.');
        return;
      }
      render();
      updateLastUpdated(data.updated_at);
    })
    .catch(() => showError('Price data unavailable. Check back soon.'));

  // Recalculate on tank input — no validation, just render
  tankInput.addEventListener('input', render);

  // Auto-select all on focus so user can immediately type a new value
  tankInput.addEventListener('focus', () => {
    setTimeout(() => tankInput.select(), 0);
  });
  // Also handle tap on mobile (touchstart fires before focus)
  tankInput.addEventListener('touchend', () => {
    setTimeout(() => tankInput.select(), 50);
  });

  // Toll toggle
  tollToggle.addEventListener('change', () => {
    tollsOn = tollToggle.checked;
    updateTollCard();
    render();
  });

  updateTollCard();
});

// ─── Calculation ──────────────────────────────────────────────────

function calculate(tank) {
  const fx = fxRate * FX_CC_MARKUP;

  const sarniaPerL  = prices.sarnia.price_cad_cents_per_litre / 100;
  const canadaTotal = sarniaPerL * tank;

  const phUsdPerGal = prices.port_huron.price_usd_per_gallon;
  const phPerLCad   = (phUsdPerGal / LITRES_PER_GALLON) * fx;
  const usaCost     = phPerLCad * tank;

  const tollTotal   = tollsOn ? TOLL_CAD + (TOLL_USD * fx) : 0;
  const usaTotal    = usaCost + tollTotal;

  const savings     = Math.abs(canadaTotal - usaTotal);
  const winner      = canadaTotal <= usaTotal ? 'Canada' : 'USA';

  return { sarniaPerL, phUsdPerGal, canadaTotal, usaTotal, savings, winner };
}

// ─── Render ───────────────────────────────────────────────────────

function render() {
  if (!fxRate || !prices) return;
  if (!prices.sarnia?.price_cad_cents_per_litre || !prices.port_huron?.price_usd_per_gallon) {
    showError('One or more price feeds unavailable. Check back soon.');
    return;
  }

  const tank  = parseTank();
  const { sarniaPerL, phUsdPerGal, canadaTotal, usaTotal, savings, winner } = calculate(tank);

  setText('sarnia-price',  fmt(sarniaPerL, 2));
  setText('sarnia-station', prices.sarnia.station_name || '');
  setText('sarnia-total',  '$' + fmt(canadaTotal, 2));

  setText('ph-price',   fmt(phUsdPerGal, 2));
  setText('ph-station', prices.port_huron.station_name || '');
  setText('ph-total',   '$' + fmt(usaTotal, 2));

  document.getElementById('sarnia-card').classList.toggle('winner', winner === 'Canada');
  document.getElementById('ph-card').classList.toggle('winner', winner === 'USA');

  document.getElementById('verdict-icon').innerHTML =
    winner === 'Canada' ? '&#x1F1E8;&#x1F1E6;' : '&#x1F1FA;&#x1F1F8;';

  document.getElementById('verdict-amount').innerHTML =
    `<span class="savings-muted">$${fmt(savings, 2)} cheaper in</span><br>` +
    `<span class="savings-winner">${winner}</span>`;
}

// ─── Helpers ─────────────────────────────────────────────────────

function parseTank() {
  const val = parseFloat(document.getElementById('tank').value);
  return val > 0 ? val : DEFAULT_TANK;
}

function updateTollCard() {
  const card   = document.getElementById('toll-card');
  const status = document.getElementById('toll-status');
  const detail = document.getElementById('toll-detail');

  if (tollsOn) {
    card.classList.add('active');
    status.textContent = 'Active';
    detail.textContent = '7 CAD + 5 USD Round Trip';
  } else {
    card.classList.remove('active');
    status.textContent = 'Excluded';
    detail.textContent = 'Tolls not counted';
  }
}

function updateLastUpdated(iso) {
  if (!iso) return;
  const diffMin = Math.round((Date.now() - new Date(iso)) / 60000);
  let label;
  if (diffMin < 2)       label = 'Prices just updated';
  else if (diffMin < 60) label = `Prices updated ${diffMin}m ago`;
  else                   label = `Prices updated ${Math.round(diffMin / 60)}h ago`;
  setText('last-updated', label);
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function fmt(n, decimals) {
  return Number(n).toFixed(decimals);
}

function showError(msg) {
  const banner = document.getElementById('error-banner');
  document.getElementById('error-msg').textContent = msg;
  banner.hidden = false;
}
