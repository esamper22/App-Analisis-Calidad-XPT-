# Guía Profesional para Ejecutar la Aplicación Flask

Aquí tienen ☺ Raydel, Luis! la guía definitiva, clara y profesional para correr su aplicación Flask :) en **dos modos**:  
- **Desarrollo** (para trabajar en los talleres o durante la tesis)  
- **Despliegue** (para la ejecución final o producción)

---

## 1. Preparativos Previos

Antes de ejecutar la app, asegúrate de:

- Tener instalado Python 3.8+  
- Tener un entorno virtual creado y activado  
- Haber instalado las dependencias necesarias (Flask, Flask-Migrate, etc.)  
- Configurar las variables de entorno en un archivo `.env`

---

## 2. Estructura Básica de Configuración

La app usa dos configuraciones principales:

| Modo        | Configuración usada           | Base de datos                    | Uso principal                  |
|-------------|------------------------------|---------------------------------|-------------------------------|
| Desarrollo  | `ConfiguracionDesarrollo`     | SQLite local (`desarrollo.db`)   | Talleres, pruebas, desarrollo  |
| Despliegue  | `ConfiguracionDespliegue`     | PostgreSQL u otra base externa   | Ejecución final, producción    |

---

## 3. Cómo activar el entorno virtual

En la terminal, desde la carpeta raíz del proyecto:

- **Windows (PowerShell):**

  ```
  .\venv\Scripts\Activate
  ```

- **Linux/macOS:**

  ```
  source venv/bin/activate
  ```

---

## 4. Variables de entorno necesarias

Crea un archivo `.env` en la raíz con las variables:

```
# Para desarrollo
FLASK_ENV=development
FLASK_APP=app:crear_app

# Para despliegue (ajustar según tu base de datos)
SQLALCHEMY_DATABASE_URI=postgresql://usuario:contraseña@localhost:5432/tu_basedatos
SECRET_KEY=tu_clave_secreta
TOKEN_ACCESO=tu_token_de_acceso
```

---

## 5. Ejecutar la aplicación en modo Desarrollo

Este modo usa SQLite y activa el debug para facilitar el desarrollo.

```
set FLASK_ENV=development         # Windows CMD
$env:FLASK_ENV="development"      # PowerShell
export FLASK_ENV=development       # Linux/macOS

flask --app app:crear_app run
```

- La app correrá en `http://localhost:5000`  
- Cambios en el código se recargan automáticamente (hot reload)  
- Ideal para talleres y pruebas

---

## 6. Ejecutar la aplicación en modo Despliegue (Producción)

Este modo usa la configuración para producción (PostgreSQL, sin debug).

```
set FLASK_ENV=production           # Windows CMD
$env:FLASK_ENV="production"        # PowerShell
export FLASK_ENV=production         # Linux/macOS

flask --app app:crear_app run --host=0.0.0.0 --port=8000
```

- La app estará accesible desde la red en el puerto 8000  
- Debug está desactivado para seguridad  
- Usa la base de datos configurada en `SQLALCHEMY_DATABASE_URI`  
- Ideal para la entrega final o despliegue real

---

## 7. Migraciones de Base de Datos

Antes de correr la app, asegúrate de aplicar migraciones para crear o actualizar tablas.

```
flask --app app:crear_app db migrate -m "Mensaje de migración"
flask --app app:crear_app db upgrade
```

---

## 8. Resumen rápido de comandos

| Acción                     | Comando ejemplo                                         |
|----------------------------|--------------------------------------------------------|
| Activar entorno virtual    | `.\venv\Scripts\Activate.ps1` (Win) / `source venv/bin/activate` (Linux/macOS) |
| Ejecutar en desarrollo     | `flask --app app:crear_app run`                        |
| Ejecutar en producción     | `flask --app app:crear_app run --host=0.0.0.0 --port=8000` |
| Crear migración            | `flask --app app:crear_app db migrate -m "mensaje"`    |
| Aplicar migración          | `flask --app app:crear_app db upgrade`                  |

---

## 9. Consejos finales

- Siempre activa el entorno virtual antes de trabajar.  
- Usa el modo desarrollo para programar y probar.  
- Usa el modo despliegue para la entrega o producción.  
- Mantén tus variables de entorno seguras y fuera del repositorio.  
- Consulta la documentación oficial de Flask para dudas avanzadas.