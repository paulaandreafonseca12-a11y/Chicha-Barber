
// ─────────────────────────────────────────────────────────────
// DATA INICIAL
// ─────────────────────────────────────────────────────────────

const TODAY = new Date();

const DAYS_OF_WEEK = [
  'DOMINGO','LUNES','MARTES',
  'MIÉRCOLES','JUEVES','VIERNES','SÁBADO'
];

const MONTHS = [
  'Ene','Feb','Mar','Abr','May','Jun',
  'Jul','Ago','Sep','Oct','Nov','Dic'
];

// Próximos 3 días
const days = [];

for (let i = 0; i < 3; i++) {

  const d = new Date();

  d.setDate(TODAY.getDate() + i);

  days.push({
    label: DAYS_OF_WEEK[d.getDay()],
    number: d.getDate(),
    month: MONTHS[d.getMonth()],
    closed: d.getDay() === 0,
    date: d
  });

}


// ─────────────────────────────────────────────────────────────
// HORARIOS
// ─────────────────────────────────────────────────────────────

const SLOT_SETS = [

  ['09:00','09:45','10:30','11:15','12:00','14:00','14:45','15:30','16:15','17:00','17:45','18:30'],

  ['09:00','09:45','10:30','11:15','12:00','14:00','14:45','15:30','16:15','17:00','17:45','18:30'],

  ['09:00','09:45','10:30','12:00','14:00','15:30','17:00','17:45','18:30'],

];


// 🔥 DISPONIBILIDAD REAL DESDE DJANGO
let UNAVAIL = {};


// ─────────────────────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────────────────────

let state = {
  step: 1,
  dayIndex: null,
  time: null,
  payment: 'persona'
};


// ─────────────────────────────────────────────────────────────
// CARGAR DISPONIBILIDAD
// ─────────────────────────────────────────────────────────────

async function cargarDisponibilidad() {

  try {

    // 🔥 URL CORRECTA DJANGO
    const response = await fetch('{% url "api_disponibilidad" %}');

    if (!response.ok) {
      throw new Error('Error cargando disponibilidad');
    }

    const data = await response.json();

    /*
      JSON esperado:

      {
        "2026-05-07": ["09:00","10:30"],
        "2026-05-08": ["14:00"]
      }
    */

    UNAVAIL = data;

    console.log("DISPONIBILIDAD:", UNAVAIL);

    init();

  } catch (error) {

    console.error("ERROR DISPONIBILIDAD:", error);

    init();

  }

}


// ─────────────────────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────────────────────

function init() {

  const grid = document.getElementById('day-grid');

  grid.innerHTML = '';

  days.forEach((d, i) => {

    const col = document.createElement('div');

    col.className = 'col-4';

    col.innerHTML = `

      <div class="day-card${d.closed ? ' disabled' : ''}"
           onclick="selectDay(${i}, this)">

        <div class="day-name">${d.label}</div>

        <div class="day-number">${d.number}</div>

        <div class="day-month">${d.month}</div>

        ${d.closed ? '<div class="badge-closed">CERRADO</div>' : ''}

      </div>

    `;

    grid.appendChild(col);

  });

}


// ─────────────────────────────────────────────────────────────
// SELECCIONAR DÍA
// ─────────────────────────────────────────────────────────────

function selectDay(i, el) {

  if (days[i].closed) return;

  document.querySelectorAll('.day-card')
    .forEach(c => c.classList.remove('selected'));

  el.classList.add('selected');

  state.dayIndex = i;

  state.time = null;

  renderSlots(i);

}


// ─────────────────────────────────────────────────────────────
// RENDERIZAR HORARIOS
// ─────────────────────────────────────────────────────────────

function renderSlots(i) {

  const d = days[i];

  // Fecha YYYY-MM-DD
  const y = d.date.getFullYear();

  const m = String(d.date.getMonth() + 1).padStart(2, '0');

  const day = String(d.date.getDate()).padStart(2, '0');

  const fechaKey = `${y}-${m}-${day}`;

  const slots = SLOT_SETS[i];

  // 🔥 Horas ocupadas reales
  const unavail = UNAVAIL[fechaKey] || [];

  console.log("Fecha:", fechaKey);

  console.log("Horas ocupadas:", unavail);

  const grid = document.getElementById('time-grid');

  const ph = document.getElementById('time-placeholder');

  grid.innerHTML = '';

  slots.forEach(t => {

    // 🔥 Compatible con 09:00 o 09:00:00
    const isUnavail = unavail.some(
      h => h.slice(0,5) === t
    );

    const col = document.createElement('div');

    col.className = 'col-3';

    col.innerHTML = `

      <div class="time-slot${isUnavail ? ' unavailable' : ''}"

           onclick="${isUnavail ? '' : `selectTime('${t}', this)`}">

        ${t}

      </div>

    `;

    grid.appendChild(col);

  });

  ph.classList.add('d-none');

  grid.classList.remove('d-none');

}


// ─────────────────────────────────────────────────────────────
// SELECCIONAR HORA
// ─────────────────────────────────────────────────────────────

function selectTime(t, el) {

  if (el.classList.contains('unavailable')) return;

  document.querySelectorAll('.time-slot')
    .forEach(s => s.classList.remove('selected'));

  el.classList.add('selected');

  state.time = t;

}


// ─────────────────────────────────────────────────────────────
// PAGOS
// ─────────────────────────────────────────────────────────────

function selectPayment(el) {

  document.querySelectorAll('.payment-option')
    .forEach(p => p.classList.remove('selected'));

  el.classList.add('selected');

  state.payment = el.dataset.pay;

}


// ─────────────────────────────────────────────────────────────
// NAVEGACIÓN
// ─────────────────────────────────────────────────────────────

function goStep(n) {

  document.querySelectorAll('.step-panel')
    .forEach(p => p.classList.add('d-none'));

  const panel = document.getElementById('panel-' + n);

  if (panel) {

    panel.classList.remove('d-none');

    panel.classList.add('step-panel');

  }

  state.step = n;

  updateStepper(n);

}


function updateStepper(current) {

  [1,2,3].forEach(i => {

    const item = document.getElementById('step-indicator-' + i);

    const circle = document.getElementById('circle-' + i);

    if (!item || !circle) return;

    item.classList.remove('active', 'done');

    if (i < current) {

      item.classList.add('done');

      circle.innerHTML = '✓';

    }

    else if (i === current) {

      item.classList.add('active');

      circle.textContent = i;

    }

    else {

      circle.textContent = i;

    }

  });

}


// ─────────────────────────────────────────────────────────────
// BOTÓN PASO 1
// ─────────────────────────────────────────────────────────────

document.getElementById('btn-step1')
.addEventListener('click', () => {

  if (state.dayIndex === null) {

    alert('Selecciona un día');

    return;

  }

  if (!state.time) {

    alert('Selecciona un horario');

    return;

  }

  goStep(2);

});


// ─────────────────────────────────────────────────────────────
// RESERVAR
// ─────────────────────────────────────────────────────────────

function reservar() {

  const nombre =
    document.getElementById('inp-nombre').value.trim();

  const apellido =
    document.getElementById('inp-apellido').value.trim();

  const email =
    document.getElementById('inp-email').value.trim();

  const tel =
    document.getElementById('inp-tel').value.trim();

  const d = days[state.dayIndex];

  const y = d.date.getFullYear();

  const m = String(d.date.getMonth() + 1).padStart(2, '0');

  const day = String(d.date.getDate()).padStart(2, '0');

  const fechaStr = `${y}-${m}-${day}`;

  document.getElementById('hidden-nombre_cliente').value =
    `${nombre} ${apellido}`;

  document.getElementById('hidden-correo').value =
    email;

  document.getElementById('hidden-telefono').value =
    tel;

  document.getElementById('hidden-fecha').value =
    fechaStr;

  document.getElementById('hidden-hora').value =
    state.time;

  document.getElementById('reserva-form').submit();

}


// ─────────────────────────────────────────────────────────────
// RESTART
// ─────────────────────────────────────────────────────────────

function restart() {

  location.reload();

}


// ─────────────────────────────────────────────────────────────
// INICIO
// ─────────────────────────────────────────────────────────────

cargarDisponibilidad();

