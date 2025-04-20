# 🧩 Estructura de Modelos del Sistema Delphi

Este modelo de base de datos implementa un sistema de evaluación de aplicaciones informáticas usando el **método Delphi** dentro del contexto de la **Universidad de la Isla de la Juventud (UIJ)**. Está completamente preparado para gestión de rondas, participantes activos, evaluaciones múltiples por aplicación, análisis estadístico avanzado y extensiones futuras como algoritmos de regresión para predecir la calidad de las soluciones evaluadas.

---

## 📦 `Application` (Aplicación)

- **Función:** Representa una aplicación informática concreta que será sometida al proceso de evaluación. Puede tratarse de una tesis, un software académico, administrativo o una herramienta informática usada en la UIJ.
- **Campos Clave:**
  - `name`: Nombre de la aplicación (obligatorio).
  - `description`: Descripción detallada (opcional).
  - `created_at`: Fecha de registro en el sistema.
- **Relaciones:**
  - `evaluations`: Una aplicación puede ser evaluada múltiples veces por distintos usuarios en distintas rondas.
  - `rounds`: Está asociada a una o varias rondas del método Delphi (1:N).

---

## 👤 `User` (Usuario)

- **Función:** Representa a cualquier persona que interactúa con el sistema, con distintos roles: `administrador`, `evaluador`, `desarrollador` o `invitado`.
- **Campos Clave:**
  - `username`: Nombre de usuario único.
  - `email`: Correo electrónico de contacto.
  - `password`: Contraseña encriptada.
  - `role`: Rol del usuario en el sistema.
  - `is_active`: Estado activo/inactivo para permitir el control de acceso.
  - `created_at`: Fecha de creación del usuario.
- **Relaciones:**
  - `evaluations`: Lista de evaluaciones realizadas (1:N con `EvaluationResult`).
  - `round_assocs`: Asociación con rondas para controlar presencia activa (1:N con `RoundParticipant`).

---

## 🔁 `EvaluationRound` (Ronda de Evaluación)

- **Función:** Representa cada iteración del proceso Delphi para una aplicación. Cada ronda busca reducir la variabilidad y lograr consenso entre los expertos.
- **Campos Clave:**
  - `number`: Número secuencial de la ronda (Ej. Ronda 1, 2, 3...).
  - `application_id`: Referencia a la aplicación que se está evaluando.
  - `deadline`: Fecha límite para completar la ronda.
  - `created_at`: Fecha de inicio de la ronda.
- **Relaciones:**
  - `results`: Evaluaciones individuales realizadas en esta ronda (1:N con `EvaluationResult`).
  - `participants`: Lista de usuarios invitados y activos en esta ronda (1:N con `RoundParticipant`).

---

## 📊 `EvaluationResult` (Resultado de Evaluación)

- **Función:** Contiene los resultados estadísticos de una evaluación realizada por un experto sobre una aplicación en una ronda específica.
- **Campos Clave:**
  - `application_id`: ID de la aplicación evaluada.
  - `evaluator_id`: ID del evaluador (usuario).
  - `round_id`: ID de la ronda en que se realizó esta evaluación.
  - **Métricas estadísticas**:
    - `mean_score`: Promedio de las puntuaciones otorgadas.
    - `std_dev`: Desviación estándar.
    - `min_score`: Puntuación mínima otorgada.
    - `max_score`: Puntuación máxima otorgada.
    - `range_score`: Rango (diferencia entre máxima y mínima).
    - `median_score`: Mediana de las puntuaciones.
    - `mode_score`: Moda (valor más frecuente).
  - `justification`: Texto libre con observaciones cualitativas del evaluador.
  - `submitted_at`: Marca de tiempo de envío.

---

## 👥 `RoundParticipant` (Participante de Ronda)

- **Función:** Gestiona la inscripción y presencia activa de un usuario en una ronda específica. Solo participantes activos pueden enviar evaluaciones.
- **Campos Clave:**
  - `user_id`: ID del usuario invitado.
  - `round_id`: ID de la ronda.
  - `invited_at`: Fecha de invitación a la ronda.
  - `joined_at`: Fecha de conexión inicial (inicio de sesión en la ronda).
  - `last_ping`: Última señal de actividad (heartbeat).
  - `left_at`: Fecha de salida o desconexión.
- **Propiedades y Métodos:**
  - `is_active`: Devuelve `True` si el usuario está conectado y dentro del umbral de actividad configurado.
  - `mark_joined()`, `ping()`, `mark_left()`: Métodos para actualizar estado de conexión.
- **Relaciones:**
  - `user`: Relación inversa con `User`.
  - `round`: Relación inversa con `EvaluationRound`.

---

## 🔗 Relaciones Clave del Sistema

| Modelo Origen      | Relación →               | Modelo Destino         |
|--------------------|--------------------------|-------------------------|
| Application        | 1 → N `evaluations`      | EvaluationResult        |
| Application        | 1 → N `rounds`           | EvaluationRound         |
| User               | 1 → N `evaluations`      | EvaluationResult        |
| User               | 1 → N `round_assocs`     | RoundParticipant        |
| EvaluationRound    | 1 → N `results`          | EvaluationResult        |
| EvaluationRound    | 1 → N `participants`     | RoundParticipant        |

---

## 🔍 Observaciones Técnicas Avanzadas

- **Control de presencia:** Solo usuarios con sesión activa (`RoundParticipant.is_active == True`) pueden enviar `EvaluationResult`.
- **Análisis dinámico:** Permite ver evolución de consenso por ronda, por usuario y por aplicación.
- **Preparado para regresión:** Con métricas cuantitativas y cualitativas para entrenar modelos que predigan la calidad del software.
- **Extensible:** Fácil de agregar modelos como `Question`, `Answer` o `PredictiveModel` para análisis más fino.