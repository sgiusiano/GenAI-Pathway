# LiciBot - Extractor de Licitaciones Eléctricas

Sistema para procesar documentos PDF de licitaciones eléctricas, extraer productos y especificaciones técnicas, y matchearlos contra un catálogo de productos.

## Estructura del Proyecto

```
licitaciones/
├── pyproject.toml              # Configuración UV
├── Dockerfile                  # Container para la aplicación
├── docker-compose.yml          # PostgreSQL + App
├── .env.example                # Variables de entorno
│
├── src/licitaciones/           # Backend (Python CLI)
│   ├── app.py                  # Punto de entrada CLI
│   ├── app_context.py          # Factory de dependencias (DI)
│   ├── config.py               # Configuración (pydantic-settings)
│   ├── logger.py               # Configuración de logging
│   ├── domain/
│   │   ├── db_models.py        # Modelos BD (normalizados)
│   │   ├── extraction_models.py # Modelos extracción (jerárquicos)
│   │   └── enums.py            # Enumeraciones
│   ├── extraction/
│   │   ├── protocols.py        # Interfaces (Protocols)
│   │   ├── product_extractor.py # Extracción con Gemini (file upload)
│   │   ├── properties_extractor.py # Estructuración con OpenAI
│   │   ├── extraction_pipeline.py # Orquestador
│   │   └── prompts.py          # Prompts LLM
│   ├── matching/
│   │   └── matcher.py          # Matching (placeholder)
│   └── db/
│       ├── connection.py       # Pool de conexiones
│       ├── init.py             # Inicialización BD
│       ├── catalog.py          # Carga de catálogo CSV
│       └── migrations/         # Scripts SQL
│
├── frontend/                   # Frontend (React + Vite)
│   ├── src/
│   │   ├── components/         # Componentes UI
│   │   ├── pages/              # Páginas (Upload, History, Detail, Matching)
│   │   ├── services/           # Servicios mock (API simulada)
│   │   ├── stores/             # Estado global (Zustand)
│   │   └── types/              # Tipos TypeScript
│   └── public/                 # Assets estáticos
│
├── data/
│   └── catalog/                # CSVs del catálogo SERVELEC
│
├── file_to_test/               # PDFs para procesar (gitignored)
│
└── tests/
```

## Requisitos

### Backend
- Python 3.11+
- Docker (para PostgreSQL)
- UV (gestor de paquetes)

### Frontend
- Node.js 18+
- npm

## Instalación

1. **Clonar el repositorio**

2. **Instalar UV** (si no está instalado):

   MacOS/LINUx

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   Windows
   ```bash
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Instalar dependencias**:
   ```bash
   uv sync
   ```

4. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   # Editar .env con tus API keys:
   # - GOOGLE_API_KEY (Gemini)
   # - OPENAI_API_KEY
   ```

5. **Iniciar servicios** (solo para desarrollo local):
   ```bash
   docker compose up -d postgres
   ```

6. **Instalar frontend**:
   ```bash
   cd frontend
   npm install
   ```

## Frontend (LiciBot UI)

El frontend es una aplicación React con datos mock (sin API real por ahora).

### Stack
- React 18 + TypeScript
- Vite (bundler)
- Tailwind CSS v4
- TanStack Query (server state)
- Zustand (client state)
- React Router v6
- Lucide React (iconos)
- Sonner (toasts)

### Ejecutar en desarrollo
```bash
cd frontend
npm run dev
```
Abre http://localhost:5173

### Build para producción
```bash
cd frontend
npm run build
```
Los archivos se generan en `frontend/dist/`

### Funcionalidades
- **Upload**: Subir PDFs con rango de páginas opcional
- **Historial**: Ver extracciones anteriores
- **Detalle**: Ver especificaciones y items extraídos
- **Matching**: Ver productos del catálogo que matchean

## Uso (Backend CLI)

### Opción 1: Ejecutar con Docker (recomendado)

1. **Colocar el PDF en `file_to_test/`**:
   ```bash
   mkdir -p file_to_test
   cp /path/to/licitacion.pdf file_to_test/
   ```

2. **Ejecutar con Docker Compose**:
   ```bash
   docker compose run app --pdf /app/file_to_test/licitacion.pdf
   ```

   Esto automáticamente:
   - Inicia PostgreSQL si no está corriendo
   - Crea las tablas si no existen
   - Procesa el PDF y extrae los productos

### Opción 2: Ejecutar localmente

1. **Iniciar PostgreSQL**:
   ```bash
   docker compose up -d postgres
   ```

2. **Colocar el PDF en `file_to_test/`**:
   ```bash
   mkdir -p file_to_test
   cp /path/to/licitacion.pdf file_to_test/
   ```

3. **Ejecutar el procesamiento**:
   ```bash
   uv run python -m licitaciones.app --pdf "./file_to_test/licitacion.pdf"
   ```

### Reiniciar la base de datos

Si necesitás recrear la BD desde cero (después de cambios en el schema):

```bash
docker compose down -v
docker compose up -d
```

## Arquitectura

### Flujo de Extracción

```
PDF → [Gemini: file upload] → Texto → [OpenAI: structured output] → LicitacionCompleta
```

1. **GeminiProductExtractor**: Sube el PDF a Gemini y extrae texto no estructurado
2. **OpenAIPropertiesExtractor**: Convierte a modelos Pydantic estructurados

### Dependency Injection

Todas las dependencias se crean en `ApplicationContext`:

```python
ctx = ApplicationContext()
# ctx.db_connection
# ctx.extraction_pipeline
# ctx.settings
```

## Desarrollo

### Formatear código
```bash
uv run ruff check --fix .
uv run ruff format .
```

### Correr tests
```bash
uv run pytest
```

## CI/CD

El proyecto usa GitLab CI con los siguientes stages:

- **lint**: `ruff check` y `ruff format --check`
- **test**: `pytest`
- **build**: Valida `docker-compose.yml`

Los jobs corren automáticamente en cada push a `main`.

## Convenciones

- **Package Manager**: UV (no pip/poetry)
- **Formateo**: Ruff
- **Type Hints**: Obligatorios en todas las funciones
- **Arquitectura**: Dependency Injection, Protocols para interfaces
- **Logging**: Usar `get_logger(__name__)` de `licitaciones.logger`
