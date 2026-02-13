# domain/services/sql_validator_service.py
"""
Servicio de dominio para validar queries SQL generadas por LLM
Previene inyección SQL y asegura que solo se ejecuten queries seguras
"""

import re
from dataclasses import dataclass


@dataclass
class SQLValidationResult:
    """Resultado de la validación de SQL"""

    es_valido: bool
    errores: list[str]
    advertencias: list[str]


class SQLValidatorService:
    """
    Servicio que valida queries SQL para prevenir inyección SQL
    y asegurar que solo se ejecuten queries de lectura seguras
    """

    # Comandos SQL peligrosos que NO se permiten
    COMANDOS_PROHIBIDOS = {
        "DROP",
        "DELETE",
        "TRUNCATE",
        "INSERT",
        "UPDATE",
        "ALTER",
        "CREATE",
        "GRANT",
        "REVOKE",
        "EXEC",
        "EXECUTE",
        "CALL",
        "MERGE",
        "REPLACE",
    }

    # Tablas permitidas
    TABLAS_PERMITIDAS = {
        "productos",
        "accesorios",
        "alarmas",
        "tipos_alarma",
        "alimentacion",
        "aparatos_medida",
        "ensayos",
        "tipos_ensayo",
        "especificaciones",
        "gabinete",
        "garantia",
        "salida",
        "senalizaciones",
    }

    def validar(self, sql: str) -> SQLValidationResult:
        """
        Valida que el SQL sea seguro para ejecutar

        Args:
            sql: Query SQL a validar

        Returns:
            SQLValidationResult con el resultado de la validación
        """
        errores = []
        advertencias = []

        # Normalizar SQL (a mayúsculas para comparaciones)
        sql_upper = sql.upper()

        # 1. Verificar que sea una query SELECT
        if not sql_upper.strip().startswith("SELECT"):
            errores.append("Solo se permiten queries SELECT")

        # 2. Buscar comandos prohibidos
        for comando in self.COMANDOS_PROHIBIDOS:
            # Buscar el comando como palabra completa
            pattern = r"\b" + comando + r"\b"
            if re.search(pattern, sql_upper):
                errores.append(f"Comando prohibido detectado: {comando}")

        # 3. Verificar que no haya punto y coma múltiples (múltiples statements)
        if sql.count(";") > 1:
            errores.append("No se permiten múltiples statements SQL")

        # 4. Verificar que no haya comentarios maliciosos
        if "--" in sql or "/*" in sql or "*/" in sql:
            advertencias.append("Se detectaron comentarios SQL, verificar que no sean maliciosos")

        # 5. Verificar tablas usadas
        tablas_encontradas = self._extraer_tablas(sql)
        tablas_no_permitidas = tablas_encontradas - self.TABLAS_PERMITIDAS
        if tablas_no_permitidas:
            errores.append(f"Tablas no permitidas: {', '.join(tablas_no_permitidas)}")

        # 6. Verificar límite de resultados (opcional pero recomendado)
        if "LIMIT" not in sql_upper:
            advertencias.append("Query sin LIMIT, podría retornar muchos resultados")

        # 7. Verificar longitud de la query
        if len(sql) > 50000:  # 50KB
            errores.append("Query demasiado larga")

        es_valido = len(errores) == 0

        return SQLValidationResult(es_valido=es_valido, errores=errores, advertencias=advertencias)

    def _extraer_tablas(self, sql: str) -> set[str]:
        """
        Extrae los nombres de tablas de la query SQL

        Este es un método simplificado que busca patrones comunes.
        Para producción, considera usar un parser SQL real como sqlparse.
        """
        tablas = set()
        sql_upper = sql.upper()

        # Patrones para encontrar tablas
        patterns = [
            r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            r"JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            r"INNER\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            r"LEFT\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            r"RIGHT\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            r"OUTER\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, sql_upper)
            for match in matches:
                tabla = match.group(1).lower()
                tablas.add(tabla)

        return tablas


# Ejemplos de uso
if __name__ == "__main__":
    validator = SQLValidatorService()

    # ✅ SQL VÁLIDO
    sql_valido = """
    SELECT * FROM (
        SELECT DISTINCT p.*,
            similarity(p.tipo, 'Rectificador') AS score
        FROM productos p
        LEFT JOIN alimentacion a ON p.id = a.producto_id
    ) q
    WHERE q.score > 0.5
    ORDER BY score DESC
    LIMIT 10
    """

    resultado = validator.validar(sql_valido)
    print(f"SQL válido: {resultado.es_valido}")
    print(f"Errores: {resultado.errores}")
    print(f"Advertencias: {resultado.advertencias}")

    print("\n" + "=" * 50 + "\n")

    # ❌ SQL PELIGROSO
    sql_peligroso = "SELECT * FROM productos; DROP TABLE productos;"

    resultado = validator.validar(sql_peligroso)
    print(f"SQL válido: {resultado.es_valido}")
    print(f"Errores: {resultado.errores}")

    print("\n" + "=" * 50 + "\n")

    # ❌ TABLA NO PERMITIDA
    sql_tabla_mala = "SELECT * FROM usuarios WHERE id = 1"

    resultado = validator.validar(sql_tabla_mala)
    print(f"SQL válido: {resultado.es_valido}")
    print(f"Errores: {resultado.errores}")

    print("\n" + "=" * 50 + "\n")

    # ❌ COMANDO PROHIBIDO
    sql_delete = "DELETE FROM productos WHERE id = 1"

    resultado = validator.validar(sql_delete)
    print(f"SQL válido: {resultado.es_valido}")
    print(f"Errores: {resultado.errores}")


"""
Salida esperada:

SQL válido: True
Errores: []
Advertencias: []

==================================================

SQL válido: False
Errores: ['No se permiten múltiples statements SQL', 'Comando prohibido detectado: DROP']

==================================================

SQL válido: False
Errores: ['Tablas no permitidas: usuarios']

==================================================

SQL válido: False
Errores: ['Solo se permiten queries SELECT', 'Comando prohibido detectado: DELETE']
"""
