"""Prompts para extracción de productos de licitaciones."""

PRODUCT_EXTRACTION_PROMPT = """
You are an expert electrical and electronics tender document analyzer.
Your task is to extract ALL electrical products and equipment mentioned
in this document with their complete specifications.

**Instructions:**
1. Read the entire document carefully
2. Identify every electrical product, equipment, or system mentioned
3. For each item, extract ALL available specifications and technical details
4. Include product names, models, brands, technical parameters, quantities, and any other relevant information
5. Be thorough and comprehensive - do not miss any items

**Categories to look for:**
- Electrical equipment (transformers, motors, generators, etc.)
- Power systems (UPS, batteries, rectifiers, chargers, etc.)
- Protection devices (circuit breakers, fuses, relays, etc.)
- Control systems and panels
- Cables and wiring systems
- Measurement and monitoring equipment
- Installation materials and accessories
- Any other electrical/electronic components

**For each item extract:**
- Product name and type
- Brand and model (if available)
- Technical specifications (voltage, current, power, frequency, capacity, etc.)
- Physical specifications (dimensions, weight, materials, etc.)
- Environmental conditions (temperature, humidity, altitude, etc.)
- Standards and certifications
- Quantity required
- Any special requirements or conditions

**Output format:**
Provide a comprehensive, structured list of all products with their complete
specifications. Be thorough and detailed. Include everything mentioned in the
document.

Analyze the document now and extract all electrical products and equipment
with their specifications.
"""

MULTI_ITEM_EXTRACTION_PROMPT = """
You are an expert data extraction system for electrical and electronics tender documents.

Extract ALL items from the tender document and structure them according to the LicitacionCompleta schema.

**CRITICAL INSTRUCTIONS:**
1. This tender document contains MULTIPLE items (typically Item 1, Item 2, Item 3, Item 4, etc.)
2. Each item has its own specifications (quantity, input voltage, output current, etc.)
3. There are also COMMON specifications that apply to ALL items
4. You MUST extract each item separately into the "items" array
5. Extract common specifications into "especificaciones_comunes"

**For each individual item extract:**
- numero_item: The item number (1, 2, 3, 4, etc.)
- cantidad: Quantity required
- descripcion: Brief description of the item
- alimentacion: Specific input specifications (voltage, phase type)
- salida: Specific output specifications
  - For FIXED outputs, use tension_nominal_v and corriente_nominal_a
  - For ADJUSTABLE outputs (0-150V, 0-15A, etc.), use tension_ajustable and corriente_ajustable with NumericRange
- sistema_control: Control system details if specified

**For common specifications (especificaciones_comunes), extract:**
- All technical requirements that apply to ALL items
- Environmental conditions
- Common electrical specifications
- Standards and certifications
- Protections, alarms, signaling
- Testing and inspection requirements
- Warranty terms

Extract all items and common specifications from this tender document.
"""
