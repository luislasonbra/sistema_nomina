# 🇩🇴 Sistema de Nómina RD

Sistema completo de gestión de nómina para empresas en República Dominicana, desarrollado en un único archivo HTML5 con Bootstrap 5. No requiere instalación ni servidor — basta con abrir el archivo en cualquier navegador moderno.

---

## Inicio Rápido

1. Descarga el archivo `nomina.html`
2. Ábrelo en cualquier navegador moderno (Chrome, Firefox, Edge)
3. ¡Listo! El sistema carga con datos de ejemplo para explorar

> **Los datos se guardan automáticamente** en el `localStorage` del navegador. No se necesita base de datos ni conexión a internet.

---

## Módulos del Sistema

### 1. Empleados
Gestión completa del personal de la empresa.

| Funcionalidad | Detalle |
|---|---|
| Registro | Nombres, cédula, email, teléfono, dirección, fecha de ingreso |
| Clasificación | Tipo de empleado: Fijo, Por Hora, Temporal |
| Organización | Asignación a departamento y cargo |
| Estado | Activo / Inactivo / Suspendido |
| Búsqueda | Filtro en tiempo real por nombre, cédula o email |
| Paginación | 10 empleados por página |

**CRUD:** Crear · Leer · Actualizar · Eliminar

---

### 2. Departamentos
Organización de las áreas de la empresa.

- Nombre, código y descripción
- Vista lateral con cargos y cantidad de empleados por departamento
- Validación: no se puede eliminar un departamento con empleados asignados

**CRUD:** Crear · Leer · Actualizar · Eliminar

---

### 3. Cargos
Catálogo de posiciones por departamento.

- Nombre del cargo y nivel jerárquico (Operativo, Técnico, Supervisorio, Gerencial, Directivo)
- Rango salarial: salario base y máximo
- Vinculado a un departamento
- Validación: no se puede eliminar un cargo con empleados asignados

**CRUD:** Crear · Leer · Actualizar · Eliminar

---

### 4. Períodos de Nómina
Control de los ciclos de pago.

- Tipos: Mensual, Quincenal, Semanal
- Fechas de inicio y fin, días laborables
- Estados: Abierto → Procesado → Cerrado
- Acceso directo para procesar la nómina desde la tarjeta del período

**CRUD:** Crear · Leer · Actualizar · Eliminar

---

### 5. Nómina
Módulo central de cálculo y procesamiento de pagos.

#### Pestaña: Procesar Nómina
- Selección de período y filtro por departamento
- Cálculo automático proporcional por días laborables
- Campo de bonificaciones individuales por empleado
- Selección múltiple con checkbox (procesar todos o seleccionados)
- Totales en tiempo real: Bruto · Descuentos · Neto

#### Pestaña: Historial
- Registro de todas las nóminas procesadas
- Total de empleados, bruto y neto por período

#### Pestaña: Recibo de Pago
- Generación de recibo individual por empleado y período
- Detalle de ingresos y cada deducción aplicada
- Función de impresión directa

---

### 6. Deducciones (Tipos Generales)
Catálogo de deducciones que aplican a la nómina.

| Deducción | Tipo | Valor por defecto |
|---|---|---|
| AFP Empleado | Porcentaje | 2.87% |
| SFS Empleado | Porcentaje | 3.04% |
| ISR | Escala progresiva | Automático |
| Préstamo Empresa | Monto fijo | RD$2,000 |

- Las deducciones marcadas como **Obligatorias** se aplican automáticamente a todos los empleados elegibles
- Las deducciones **No Obligatorias** están disponibles para asignación individual
- Calculadora interactiva: ingresa un salario y ve el desglose completo en tiempo real

**CRUD:** Crear · Leer · Actualizar · Eliminar

---

### 7. Deducciones por Empleado *(módulo individual)*
Asignación de descuentos específicos por persona.

Este módulo resuelve el caso en que **no todos los empleados tienen los mismos descuentos**: préstamos, embargos, cooperativas, seguros voluntarios, etc.

#### Flujo de uso:
1. Selecciona un empleado de la lista izquierda
2. Haz clic en **Agregar**
3. Elige un tipo del catálogo o escribe un nombre personalizado
4. Define si es monto fijo o porcentaje
5. (Opcional) establece fechas de inicio/fin y número de cuotas

#### Funcionalidades:
- **Vista por empleado**: cuántas deducciones activas tiene cada uno
- **Activar / Desactivar**: pausa una deducción sin eliminarla (historial conservado)
- **Reactivar**: vuelve a activar una deducción pausada
- **Vigencia**: fecha de fin y número de cuotas configurables
- **Observaciones**: notas internas por asignación
- Las deducciones individuales activas **se incluyen automáticamente** en el cálculo de nómina y en el recibo de pago

**CRUD:** Crear · Leer · Actualizar · Eliminar · Desactivar · Reactivar

---

### 8. Reportes
Vistas analíticas del estado de la nómina.

| Reporte | Contenido |
|---|---|
| Resumen General | Empleados activos, masa salarial, salario promedio, barras de distribución por estado |
| Por Departamento | Empleados, salario promedio, total y porcentaje de la masa salarial |
| Por Empleado | Cargo, salario, deducciones mensuales y neto; con búsqueda en tiempo real |

---

## Cálculo del ISR (Impuesto sobre la Renta)

El sistema aplica la escala progresiva vigente en República Dominicana:

| Renta Anual | Tasa |
|---|---|
| Hasta RD$416,220 | Exento |
| RD$416,220 – RD$624,329 | 15% |
| RD$624,329 – RD$867,123 | 20% |
| Más de RD$867,123 | 25% |

El ISR se calcula anualizado y se divide entre 12 para el descuento mensual.

---

## Almacenamiento de Datos

Toda la información se almacena en el `localStorage` del navegador bajo la clave `payroll_db`.

```
localStorage['payroll_db'] = {
  empleados, departamentos, cargos,
  periodos, deducciones, nominas,
  asignaciones, nextId
}
```

> Los datos son locales al navegador y dispositivo. Para respaldo, exporta el contenido del `localStorage` manualmente o agrega un módulo de exportación a JSON/Excel según necesidad.

---

## Tecnologías Utilizadas

| Tecnología | Versión | Uso |
|---|---|---|
| HTML5 | — | Estructura |
| Bootstrap | 5.3.2 | Layout y componentes UI |
| Bootstrap Icons | 1.11.3 | Iconografía |
| Syne (Google Fonts) | — | Tipografía de títulos |
| DM Sans (Google Fonts) | — | Tipografía de cuerpo |
| JavaScript (ES6+) | — | Lógica y CRUD |
| localStorage API | — | Persistencia de datos |

Sin dependencias de backend. Sin base de datos externa. Sin frameworks JS.

---

## Estructura del Proyecto

```
nomina.html          ← Archivo único, todo incluido
README.md            ← Este documento
```

---

## Requisitos

- Navegador moderno con soporte para ES6+ y localStorage
- Conexión a internet solo en la primera carga (para cargar Bootstrap y fuentes desde CDN)
- Para uso offline: descarga Bootstrap, Bootstrap Icons y las fuentes localmente y actualiza los `<link>` del archivo

---

## Datos de Ejemplo Precargados

Al iniciar por primera vez el sistema carga automáticamente:

- **5 departamentos**: Administración, Ventas, Tecnología, Operaciones, RRHH
- **8 cargos** distribuidos entre departamentos
- **7 empleados** activos con salarios reales de referencia
- **3 períodos**: Enero y Febrero 2025 (cerrados), Marzo 2025 (abierto)
- **4 tipos de deducciones**: AFP, SFS, ISR, Préstamo Empresa

---

## Licencia

Uso libre para fines educativos y empresariales internos.
