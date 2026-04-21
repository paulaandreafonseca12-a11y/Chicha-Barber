// ─── DATA ────────────────────────────────────────────────────────────────────
const TODAY = new Date();
const DAYS_OF_WEEK = ['DOMINGO','LUNES','MARTES','MIÉRCOLES','JUEVES','VIERNES','SÁBADO'];
const MONTHS = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];

// Construye los próximos 3 días desde hoy
const days = [];
for (let i = 0; i < 3; i++) {
  const d = new Date(TODAY);
  d.setDate(TODAY.getDate() + i);
  days.push({
    label:  DAYS_OF_WEEK[d.getDay()],
    number: d.getDate(),
    month:  MONTHS[d.getMonth()],
    closed: d.getDay() === 0,   // domingo = cerrado
    date:   d
  });
}

// Horarios disponibles por día (índice 0 = hoy, 1 = mañana, 2 = pasado)
const SLOT_SETS = [
  ['09:00','09:45','10:30','11:15','12:00','14:00','14:45','15:30','16:15','17:00','17:45','18:30'],
  ['09:00','09:45','10:30','11:15','12:00','14:00','14:45','15:30','16:15','17:00','17:45','18:30'],
  ['09:00','09:45','10:30','12:00','14:00','15:30','17:00','17:45','18:30'],
];

// Horarios no disponibles (ocupados) por día
const UNAVAIL = [
  ['11:15','16:15'],
  ['11:15','16:15'],
  [],
];

// ─── STATE ───────────────────────────────────────────────────────────────────
let state = { step: 1, dayIndex: null, time: null, payment: 'persona' };

// ─── INIT ─────────────────────────────────────────────────────────────────────
function init() {
  const grid = document.getElementById('day-grid');
  grid.innerHTML = '';

  days.forEach((d, i) => {
    const col = document.createElement('div');
    col.className = 'col-4';
    col.innerHTML = `
      <div class="day-card${d.closed ? ' disabled' : ''}" onclick="selectDay(${i}, this)">
        <div class="day-name">${d.label}</div>
        <div class="day-number">${d.number}</div>
        <div class="day-month">${d.month}</div>
        ${d.closed ? '<div class="badge-closed">CERRADO</div>' : ''}
      </div>`;
    grid.appendChild(col);
  });
}

// ─── SELECCIONAR DÍA ─────────────────────────────────────────────────────────
function selectDay(i, el) {
  if (days[i].closed) return;
  document.querySelectorAll('.day-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  state.dayIndex = i;
  state.time = null;
  renderSlots(i);
}

function renderSlots(i) {
  const slots   = SLOT_SETS[i];
  const unavail = UNAVAIL[i];
  const grid = document.getElementById('time-grid');
  const ph   = document.getElementById('time-placeholder');

  grid.innerHTML = '';
  slots.forEach(t => {
    const isUnavail = unavail.includes(t);
    const col = document.createElement('div');
    col.className = 'col-3';
    col.innerHTML = `
      <div class="time-slot${isUnavail ? ' unavailable' : ''}" onclick="selectTime('${t}', this)">
        ${t}
      </div>`;
    grid.appendChild(col);
  });

  ph.classList.add('d-none');
  grid.classList.remove('d-none');
}

// ─── SELECCIONAR HORA ─────────────────────────────────────────────────────────
function selectTime(t, el) {
  if (el.classList.contains('unavailable')) return;
  document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
  el.classList.add('selected');
  state.time = t;
}

// ─── MÉTODO DE PAGO ───────────────────────────────────────────────────────────
function selectPayment(el) {
  document.querySelectorAll('.payment-option').forEach(p => p.classList.remove('selected'));
  el.classList.add('selected');
  state.payment = el.dataset.pay;
}

// ─── NAVEGACIÓN ENTRE PASOS ───────────────────────────────────────────────────
function goStep(n) {
  document.querySelectorAll('.step-panel').forEach(p => p.classList.add('d-none'));
  const panel = document.getElementById('panel-' + n);
  if (panel) {
    panel.classList.remove('d-none');
    panel.classList.add('step-panel');
  }
  state.step = n;
  updateStepper(n);
}

function updateStepper(current) {
  [1, 2, 3].forEach(i => {
    const item   = document.getElementById('step-indicator-' + i);
    const circle = document.getElementById('circle-' + i);
    item.classList.remove('active', 'done');

    if (i < current) {
      item.classList.add('done');
      circle.innerHTML = '<i class="bi bi-check-lg"></i>';
    } else if (i === current) {
      item.classList.add('active');
      circle.textContent = i;
    } else {
      circle.textContent = i;
    }
  });
}

// ─── PASO 1 → PASO 2 ─────────────────────────────────────────────────────────
document.getElementById('btn-step1').addEventListener('click', () => {
  if (state.dayIndex === null) { alert('Por favor selecciona un día.'); return; }
  if (!state.time)             { alert('Por favor selecciona un horario.'); return; }
  goStep(2);
});

// ─── PASO 2 → PASO 3 ─────────────────────────────────────────────────────────
document.getElementById('btn-step2').addEventListener('click', () => {
  const nombre   = document.getElementById('inp-nombre').value.trim();
  const apellido = document.getElementById('inp-apellido').value.trim();
  const email    = document.getElementById('inp-email').value.trim();
  const tel      = document.getElementById('inp-tel').value.trim();

  if (!nombre || !apellido || !email || !tel) {
    alert('Por favor completa todos los campos.');
    return;
  }

  const d = days[state.dayIndex];
  document.getElementById('confirm-dia').textContent    = `${d.label.charAt(0) + d.label.slice(1).toLowerCase()} ${d.number} de ${d.month}`;
  document.getElementById('confirm-hora').textContent   = state.time;
  document.getElementById('confirm-nombre').textContent = `${nombre} ${apellido}`;
  document.getElementById('confirm-correo').textContent = email;
  document.getElementById('confirm-cel').textContent    = tel;
  document.getElementById('confirm-pago').textContent   = state.payment === 'electronico' ? 'Pago Electrónico' : 'Pago en Persona';

  goStep(3);
});

// ─── CONFIRMAR RESERVA ────────────────────────────────────────────────────────
function reservar() {
  const nombre = document.getElementById('inp-nombre').value.trim();
  const apellido = document.getElementById('inp-apellido').value.trim();
  const email = document.getElementById('inp-email').value.trim();
  const tel = document.getElementById('inp-tel').value.trim();

  const d = days[state.dayIndex];
  
  // Formatear la fecha a YYYY-MM-DD
  const year = d.date.getFullYear();
  const month = (d.date.getMonth() + 1).toString().padStart(2, '0');
  const day = d.date.getDate().toString().padStart(2, '0');
  const fechaStr = `${year}-${month}-${day}`;
  const horaStr = state.time; // "HH:MM"

  // Llenar los campos del formulario oculto
  document.getElementById('hidden-nombre_cliente').value = `${nombre} ${apellido}`;
  document.getElementById('hidden-correo').value = email;
  document.getElementById('hidden-telefono').value = tel;
  document.getElementById('hidden-fecha').value = fechaStr;
  document.getElementById('hidden-hora').value = horaStr;
  document.getElementById('hidden-fecha_reserva').value = `${fechaStr} ${horaStr}`;

  // Enviar el formulario
  document.getElementById('reserva-form').submit();
}

// ─── REINICIAR ────────────────────────────────────────────────────────────────
function restart() {
  state = { step: 1, dayIndex: null, time: null, payment: 'persona' };

  document.getElementById('inp-nombre').value   = '';
  document.getElementById('inp-apellido').value = '';
  document.getElementById('inp-email').value    = '';
  document.getElementById('inp-tel').value      = '';

  document.querySelectorAll('.payment-option').forEach(p => p.classList.remove('selected'));
  document.querySelector('[data-pay="persona"]').classList.add('selected');

  document.getElementById('time-grid').classList.add('d-none');
  document.getElementById('time-placeholder').classList.remove('d-none');
  document.getElementById('stepper').classList.remove('d-none');

  init();
  goStep(1);
}

// ─── ARRANQUE ─────────────────────────────────────────────────────────────────
init();

