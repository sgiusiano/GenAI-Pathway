"""Tests para la configuración de la aplicación."""

from licitaciones.config import Settings


class TestSettings:
    """Tests para Settings."""

    def test_default_values(self) -> None:
        """Verifica que los valores por defecto se carguen correctamente."""
        settings = Settings(_env_file=None)

        assert (
            settings.database_url
            == "postgresql://postgres:postgres@localhost:5432/catalogo_servelec"
        )
        assert settings.postgres_user == "postgres"
        assert settings.postgres_db == "catalogo_servelec"
        assert settings.openai_api_key == ""
        assert settings.google_api_key == ""

    def test_env_override(self, monkeypatch) -> None:
        """Verifica que las variables de entorno sobreescriban los defaults."""
        monkeypatch.setenv("POSTGRES_USER", "test_user")
        monkeypatch.setenv("POSTGRES_DB", "test_db")

        settings = Settings(_env_file=None)

        assert settings.postgres_user == "test_user"
        assert settings.postgres_db == "test_db"
