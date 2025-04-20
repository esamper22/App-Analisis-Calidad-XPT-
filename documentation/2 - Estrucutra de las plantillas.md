templates/
├── base.html             # Plantilla base con bloques comunes (cabecera, navbar, pie)
├── landing.html          # Página de inicio / landing page
├── auth/
│   ├── login.html        # Formulario de inicio de sesión
│   ├── register.html     # (opcional) Registro de usuarios
│   └── password_reset.html
├── dashboard/
│   ├── expert.html       # Panel de expertos
│   ├── admin.html        # Panel de admin (superadmin)
│   ├── shared/
│   │   ├── sidebar.html  # Barra lateral compartida
│   │   └── header.html   # Cabecera interna común al dashboard
│   └── partials/
│       ├── stats_card.html   # Tarjeta de estadísticas reutilizable
│       └── activity_feed.html# Feed de actividad
├── rounds/
│   ├── list.html         # Listado de rondas
│   ├── detail.html       # Detalle de una ronda (participantes, resultados)
│   └── create.html       # Formulario para crear/editr ronda
├── applications/
│   ├── list.html         # Listado de aplicaciones
│   └── detail.html       # Detalle de aplicación y evaluaciones
└── components/
    ├── alerts.html       # Included: mensajes flash
    └── modals.html       # Included: diálogos modales comunes