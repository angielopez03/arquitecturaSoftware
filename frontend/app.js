/*
 * Cliente asincrono de la API de diagnostico (RA2).
 *
 * La pagina nunca se recarga: todo se resuelve con fetch y se pinta en el DOM.
 * El selector de especies se llena desde GET /api/v1/especies (RF5): este
 * archivo no contiene ni un solo nombre de especie escrito a mano.
 */
const urlParams = new URLSearchParams(window.location.search);
const API = urlParams.get("api") || "http://localhost:5000/api/v1";

const form = document.getElementById("formulario");
const selectEspecie = document.getElementById("especie");
const ayudaRangos = document.getElementById("ayuda-rangos");
const boton = document.getElementById("boton");

const bloqueError = document.getElementById("error");
const errorTitulo = document.getElementById("error-titulo");
const errorMensaje = document.getElementById("error-mensaje");
const errorCodigo = document.getElementById("error-codigo");

const bloqueResultado = document.getElementById("resultado");
const estadoDiv = document.getElementById("estado");
const tablaParametros = document.getElementById("tabla-parametros");
const recomendacionesDiv = document.getElementById("recomendaciones");

let catalogoEspecies = [];

// ---------------------------------------------------------------- utilidades

function ocultar(el) { el.classList.add("oculto"); }
function mostrar(el) { el.classList.remove("oculto"); }

function mostrarError(titulo, mensaje, codigo) {
  ocultar(bloqueResultado);
  errorTitulo.textContent = titulo;
  errorMensaje.textContent = mensaje;
  errorCodigo.textContent = codigo ? `codigo: ${codigo}` : "";
  mostrar(bloqueError);
}

// ------------------------------------------------- RF5: poblar el selector

async function cargarEspecies() {
  try {
    const res = await fetch(`${API}/especies`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    catalogoEspecies = await res.json();

    selectEspecie.innerHTML = '<option value="">Seleccione una especie</option>';
    for (const especie of catalogoEspecies) {
      const opcion = document.createElement("option");
      opcion.value = especie.nombre;
      opcion.textContent = especie.nombre;
      selectEspecie.appendChild(opcion);
    }
  } catch (e) {
    selectEspecie.innerHTML = '<option value="">No se pudieron cargar</option>';
    mostrarError(
      "No hay conexion con el servicio",
      "No se pudo obtener la lista de especies. Verifique que el backend este ejecutandose en el puerto 5000.",
      null
    );
  }
}

// Al elegir especie, mostrar sus rangos de referencia
selectEspecie.addEventListener("change", () => {
  const especie = catalogoEspecies.find((e) => e.nombre === selectEspecie.value);
  if (!especie) { ayudaRangos.textContent = ""; return; }
  const partes = Object.entries(especie.rangos).map(
    ([nombre, r]) => `${nombre} ${r.min}-${r.max} ${r.unidad}`
  );
  ayudaRangos.textContent = `Rangos de referencia: ${partes.join(" | ")}`;
});

// ------------------------------------------------ RA2: consulta asincrona

form.addEventListener("submit", async (evento) => {
  evento.preventDefault();          // sin esto la pagina se recargaria
  ocultar(bloqueError);
  ocultar(bloqueResultado);
  boton.disabled = true;
  boton.textContent = "Consultando...";

  const cuerpo = {
    especie: selectEspecie.value,
    humedad: document.getElementById("humedad").value,
    luz: document.getElementById("luz").value,
    temperatura: document.getElementById("temperatura").value,
  };

  try {
    const res = await fetch(`${API}/diagnosticos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo),
    });
    const datos = await res.json();

    if (!res.ok) {
      // RF6: el cuerpo de error es uniforme, asi que se lee siempre igual
      const campo = datos.detalle?.campo ? ` (campo: ${datos.detalle.campo})` : "";
      mostrarError(
        res.status === 404 ? "Especie no soportada" : "Datos invalidos",
        (datos.mensaje || "La peticion no pudo procesarse.") + campo,
        datos.error
      );
      return;
    }

    pintarDiagnostico(datos);
  } catch (e) {
    mostrarError(
      "No hay conexion con el servicio",
      "No se pudo contactar la API. Verifique que el backend este ejecutandose.",
      null
    );
  } finally {
    boton.disabled = false;
    boton.textContent = "Diagnosticar";
  }
});

// ------------------------------------------------------------ presentacion

function pintarDiagnostico(d) {
  estadoDiv.textContent = d.estado;
  estadoDiv.className = `estado ${d.estado}`;

  tablaParametros.innerHTML = "";
  for (const p of d.parametros) {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${p.nombre}</td>
      <td>${p.valor} ${p.unidad}</td>
      <td>${p.rangoOptimo[0]} - ${p.rangoOptimo[1]} ${p.unidad}</td>
      <td><span class="nivel ${p.estado}">${p.estado}</span></td>`;
    tablaParametros.appendChild(fila);
  }

  recomendacionesDiv.innerHTML = "";
  if (d.recomendaciones.length > 0) {
    const titulo = document.createElement("h2");
    titulo.textContent = "Recomendaciones";
    const lista = document.createElement("ul");
    for (const r of d.recomendaciones) {
      const item = document.createElement("li");
      item.textContent = r;
      lista.appendChild(item);
    }
    recomendacionesDiv.append(titulo, lista);
  }

  mostrar(bloqueResultado);
}

cargarEspecies();
