# BizLaunch AI Assistant 🚀

Asistente inteligente multi-agente para ayudar a emprendedores a lanzar su negocio en Córdoba, Argentina.

## Características

- **Multi-Agente**: 6 agentes especializados (Supervisor, AskClarify, Location, Market, Legal, Report)
- **Arquitectura Supervisor-First**: El supervisor controla el flujo completo desde el punto de entrada
- **Herramientas MCP**: 5 herramientas con **APIs reales** para análisis de locales, mercado y regulaciones
- **Serper API Integration**: 3 tools usando Serper (Search para propiedades/demografía, Places para competidores)
- **RAG Legal**: Consulta documentos legales con ChromaDB persistente
- **Estimación de Costos**: El Report Agent calcula financials basándose en datos recopilados (sin tool adicional)
- **APIs Integradas**: Serper (Search + Places), OpenStreetMap (Overpass + Nominatim)
- **Estado Avanzado**: Tracking completo de iteraciones, agentes completados, tool calls y errores
- **Persistencia**: ChromaDB persistente + MemorySaver de LangGraph para mantener contexto
- **Multilenguaje**: Responde en el idioma del usuario (español, inglés, etc.)
- **LangSmith Integration**: Trazabilidad completa de llamadas LLM para debugging
- **UI Simple**: Interfaz Streamlit tipo chat

## Arquitectura

### Flujo Supervisor-First

```
Entry Point → Supervisor (routing inteligente)
                ↓
      ┌─────────┴─────────┐
      ↓                   ↓
  AskClarify         Agents (Location/Market/Legal)
      ↓                   ↓
  Supervisor ←────────────┘
      ↓
  Report Agent
      ↓
     END
```

### Agentes Especializados

```
BizLaunch AI
├── Supervisor Agent (punto de entrada, routing inteligente con contexto completo)
├── AskClarify Agent (valida queries y pide aclaraciones)
├── Location Agent (busca locales y analiza ubicaciones con tools)
├── Market Agent (analiza demografía y competencia con tools)
├── Legal Agent (consulta regulaciones vía RAG, genera análisis detallado)
└── Report Agent (genera informe ejecutivo estructurado en markdown)
```

### Herramientas MCP (Integradas con APIs Reales)

1. `search_properties` - Busca locales comerciales con **Serper Search API** (real listings from any source)
2. `analyze_location` - Analiza tráfico y ubicación con **Nominatim + Overpass API**
3. `get_demographics` - Busca datos demográficos con **Serper Search API** (LLM interprets results)
4. `search_competitors` - Busca competidores con **Serper Places API** (Google Maps data)
5. `query_regulations` - Consulta RAG con docs legales

**Nota**: Los costos financieros son estimados por el Report Agent basándose en los datos recopilados (tamaño de propiedades, tipo de negocio, ubicación) usando fórmulas de mercado de Córdoba, sin necesidad de un tool adicional.

## Instalación

### Requisitos

- Python 3.11+
- UV (gestor de paquetes)
- API Key de OpenAI

### Setup

1. Clonar el repositorio:
```bash
cd challenge-module-11
```

2. Instalar dependencias con UV:
```bash
uv sync
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env y configurar:
# - OPENAI_API_KEY (requerido)
# - FOURSQUARE_API_KEY (opcional, mejora búsqueda de competidores)
# - CHROMA_PERSIST_PATH (opcional, default: data/chroma_db)
# - LANGCHAIN_TRACING_V2=true (opcional, para LangSmith)
# - LANGCHAIN_API_KEY (opcional, para LangSmith)
```

**APIs Externas:**
- **Serper API**: **REQUERIDO** para funcionalidad completa
  - Free tier: 2,500 búsquedas gratis para empezar
  - Luego: $1 por 1000 búsquedas (muy económico)
  - Sign up: https://serper.dev/
  - Usado por 3 herramientas:
    - `search_properties` → Serper Search (busca en La Voz, MercadoLibre, ZonaProp, etc.)
    - `get_demographics` → Serper Search (busca datos de censo, estadísticas)
    - `search_competitors` → Serper Places (datos de Google Maps con ratings reales)
- **OpenStreetMap**: No requiere API key (free & open source)
  - Usado solo por `analyze_location` para análisis de amenities

4. Ejecutar la aplicación:
```bash
uv run streamlit run src/bizlaunch/streamlit_app.py
```

## Uso

### Ejemplos de Consultas

- "Quiero abrir una cafetería en Nueva Córdoba con presupuesto de $600.000/mes"
- "Necesito analizar el mercado para un restaurant en el Centro"
- "Qué trámites necesito para abrir un comercio en Córdoba?"
- "Cuánto cuesta montar una tienda de ropa de 100m²?"

### Flujo de Trabajo

1. Usuario ingresa su consulta en el chat
2. **Supervisor** (punto de entrada) evalúa el estado y decide routing
3. **AskClarify Agent** valida la consulta (si es necesario)
4. **Supervisor** coordina la ejecución de agentes especializados:
   - **Location Agent**: Busca locales usando herramientas MCP
   - **Market Agent**: Analiza demografía y competencia
   - **Legal Agent**: Consulta RAG, genera análisis legal detallado
5. **Supervisor** monitorea progreso y evita loops
6. **Report Agent**: Consolida todos los análisis y genera informe ejecutivo estructurado
7. Usuario recibe reporte profesional en markdown con:
   - Resumen ejecutivo
   - Análisis de ubicaciones (con precios y características)
   - Análisis de mercado
   - Requisitos legales completos (sin resumir)
   - Overview financiero
   - Recomendaciones y plan de acción

## Estructura del Proyecto

```
challenge-module-11/
├── src/
│   └── bizlaunch/
│       ├── agents/              # 6 agentes especializados
│       │   ├── supervisor.py         # Routing inteligente con estado completo
│       │   ├── ask_clarify_agent.py  # Validación de queries
│       │   ├── location_agent.py     # Búsqueda de locales
│       │   ├── market_agent.py       # Análisis de mercado
│       │   ├── legal_agent.py        # RAG → Análisis legal detallado
│       │   └── report_agent.py       # Informe ejecutivo estructurado
│       ├── tools/               # Herramientas MCP y RAG
│       │   ├── mcp_tools.py          # 5 herramientas activas con APIs reales
│       │   ├── api_config.py         # Config para Serper + OpenStreetMap
│       │   └── rag.py                # ChromaDB persistente
│       ├── state.py             # Estado avanzado con Annotated
│       ├── graph.py             # LangGraph workflow supervisor-first
│       ├── app_context.py       # Dependency injection
│       └── streamlit_app.py     # UI
├── data/
│   ├── legal_docs/              # Documentos legales (PDFs)
│   └── chroma_db/               # ChromaDB persistente (generado)
├── pyproject.toml
├── .env.example
└── .gitignore
```

## Tecnologías

- **LangChain/LangGraph**: Orquestación de agentes multi-step
- **OpenAI**: LLM (gpt-4o-mini) con streaming
- **ChromaDB**: Vector store persistente para RAG
- **Sentence Transformers**: Embeddings locales (all-MiniLM-L6-v2)
- **Serper API**: Google Search + Places API (propiedades, demografía, competidores)
- **OpenStreetMap APIs**: Overpass API + Nominatim (geocoding, análisis de ubicación)
- **LangSmith**: Observabilidad y debugging de LLM calls
- **Streamlit**: UI web tipo chat
- **UV**: Gestor de dependencias rápido

## Mejoras Implementadas

### Estado Avanzado
- **Tracking completo**: Iteraciones, agentes completados, tool calls, errores
- **Annotated types**: Reducers personalizados (`add_messages`, `merge_dict`, `merge_set`)
- **Loop prevention**: Max 5 iteraciones con guards en cada nodo
- **Message history**: Audit trail completo de la conversación

### Arquitectura Supervisor-First
- **Entry point unificado**: Supervisor controla todo el flujo
- **Routing inteligente**: Contexto completo (estado, mensajes, tool calls) para decisiones
- **Prevención de loops**: No ruta a agentes ya completados o al último ejecutado
- **Clean separation**: Cada agente es una clase independiente (SRP)

### RAG Optimizado
- **ChromaDB persistente**: Se carga instantáneamente, no re-procesa PDFs
- **Two-step analysis**: Legal Agent usa RAG → Genera análisis detallado
- **Configuración flexible**: Path persistente via env var

### Reportes Mejorados
- **Estructura profesional**: Markdown rico con emojis y secciones claras
- **Sin resumir**: Legal y Location incluyen TODOS los detalles
- **Actionable**: Plan de acción con timelines concretos

### Multilenguaje
- **Language-aware**: Todos los agentes responden en el idioma del usuario
- **Prompts en inglés**: Mejor performance del LLM
- **RAG en español**: Documentos legales originales

### Observabilidad
- **LangSmith integration**: Trazabilidad completa de LLM calls
- **Tool call tracking**: Registro de todas las herramientas usadas
- **Error handling**: Mensajes informativos en caso de fallas

## Limitaciones (POC)

- **Serper free tier**: 100 búsquedas/mes (luego $1/1000 búsquedas), fallback a OSM sin límites
- Scraping de La Voz depende de la estructura del sitio (puede cambiar)
- **Sin base de datos**: Persistencia en memoria con MemorySaver
- **Sin autenticación** de usuarios
- **Sin validaciones exhaustivas** en inputs
- Enfoque en **arquitectura multi-agente** sobre producción

## Mejoras Futuras

- Integrar más APIs con precios reales (MercadoLibre, ZonaProp, Properati)
- APIs gubernamentales (AFIP, INDEC Data Commons completo)
- Base de datos PostgreSQL para conversaciones
- Autenticación y multi-tenancy
- Más documentos legales actualizados
- Tests automatizados (pytest)
- CI/CD pipeline
- Deploy en producción (Railway, Render)
- Streaming de respuestas en UI
- Feedback de usuarios
- Cache de API calls para reducir latencia

## Licencia

MIT

## Autor

Santiago Ariel Giusiano
