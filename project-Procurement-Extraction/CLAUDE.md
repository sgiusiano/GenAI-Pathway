This document contains important guidelines and conventions for working with this Python project. Please follow these instructions carefully when making any changes or additions to the codebase.

## 🔧 Development Tools

### Package Management - UV
- **Always use `uv` for executing Python commands and managing dependencies**
- Never use `pip`, `python`, or `poetry` directly
- Examples:
  ```bash
  # Install dependencies
  uv sync --all-packages --all-groups
  
  # Run scripts
  uv run python script.py
  
  # Add a dependency
  uv add package-name
  
  # Add a dev dependency
  uv add --dev package-name
  ```

### Testing - Poe
- **Always run tests using Poe through UV**
- Command: `uv run poe test`
- Before committing any changes, ensure all tests pass
- When adding new features, include appropriate tests

### Type Checking - MANDATORY
- **ALWAYS run type checking after EVERY code change**
- Command: `uv run ty check .`
- **NEVER skip type checking - it is MANDATORY**
- If type checking fails, fix the issues before proceeding

### Linting & Formatting - Ruff
- **Always run Ruff after EVERY edit**
- Commands:
  ```bash
  # Format code
  uv run ruff format .

  # Lint and fix
  uv run ruff check . --fix

  # Run both format and lint
  uv run ruff format . && uv run ruff check . --fix
  ```
- Never commit code without running Ruff first
- If Ruff suggests fixes, apply them before proceeding

## 🏗️ Architecture Principles

### Dependency Injection
- **NEVER instantiate a class inside another class**
- Exception: Basic types (str, int, list, dict, etc.) and simple data classes
- All dependencies should be injected through constructors
- Example of what NOT to do:
  ```python
  # ❌ BAD
  class UserService:
      def __init__(self):
          self.db = DatabaseConnection()  # NO! Don't instantiate here
          self.cache = RedisCache()       # NO! Don't instantiate here
  ```
- Example of what TO DO:
  ```python
  # ✅ GOOD
  class UserService:
      def __init__(self, db: DatabaseConnection, cache: RedisCache):
          self.db = db      # Injected dependency
          self.cache = cache  # Injected dependency
  ```

### Composition Over Inheritance
- **AVOID inheritance - Always prefer composition**
- Instead of extending classes, inject the functionality you need
- Use protocols/interfaces for defining contracts
- Example of what NOT to do:
  ```python
  # ❌ BAD - Using inheritance
  class EmailService(BaseNotificationService):
      def send(self, message: str):
          # Inheriting complexity and coupling
          super().send(message)
          # Email specific logic
  
  class SMSService(BaseNotificationService):
      def send(self, message: str):
          # Inheriting complexity and coupling
          super().send(message)
          # SMS specific logic
  ```
- Example of what TO DO:
  ```python
  # ✅ GOOD - Using composition
  from typing import Protocol
  
  class MessageSender(Protocol):
      def send(self, recipient: str, message: str) -> bool:
          ...
  
  class EmailClient:
      def send_email(self, to: str, body: str) -> bool:
          # Email sending logic
          return True
  
  class SMSClient:
      def send_sms(self, phone: str, text: str) -> bool:
          # SMS sending logic
          return True
  
  class NotificationService:
      def __init__(self, email_client: EmailClient, sms_client: SMSClient):
          self.email_client = email_client  # Composed, not inherited
          self.sms_client = sms_client      # Composed, not inherited
      
      def notify_via_email(self, recipient: str, message: str) -> bool:
          return self.email_client.send_email(recipient, message)
      
      def notify_via_sms(self, phone: str, message: str) -> bool:
          return self.sms_client.send_sms(phone, message)
  ```

### Application Context Pattern
- **Use `app_context.py` as the application factory**
- The ApplicationContext is responsible for creating ALL dependencies
- It should NOT receive any dependencies in its constructor
- All configuration, connections, and services are created internally
- The ApplicationContext should:
  1. Load configuration from environment/files
  2. Create all service instances with proper dependencies
  3. Wire everything together

## 🔄 Workflow

When making changes to this project:

1. **Before starting work:**
   ```bash
   uv sync  # Ensure dependencies are up to date
   ```

2. **After EVERY code edit (MANDATORY - DO NOT SKIP):**
   ```bash
   # STEP 1: Type check (MANDATORY)
   uv run ty check .

   # STEP 2: Format and lint (MANDATORY)
   uv run ruff format . && uv run ruff check . --fix
   ```

3. **Before committing (MANDATORY CHECKLIST):**
   ```bash
   # 1. Run type checking
   uv run ty check .

   # 2. Format and lint
   uv run ruff format . && uv run ruff check . --fix
   ```

   **⚠️ IMPORTANT: NEVER commit without completing BOTH steps above**

## 🎯 Code Standards

### Imports
- **NEVER use relative imports** - Always use absolute imports with package names
- Example of what NOT to do:
  ```python
  # ❌ BAD - Relative imports
  from .models import User
  from ..services import EmailService
  from . import utils
  ```
- Example of what TO DO:
  ```python
  # ✅ GOOD - Absolute imports with package names
  from src.merchant_metadata_scraper.models import MerchantOffer
  from src.merchant_metadata_scraper.services import EmailService
  from src.merchant_metadata_scraper import utils
  ```

### Type Hints
- Always use type hints for function parameters and return values
- Use `from typing import` for complex types
- Example:
  ```python
  from typing import List, Optional, Dict

  def process_users(users: List[User], filters: Optional[Dict[str, str]] = None) -> List[User]:
      ...
  ```

### Protocols and Interfaces
- Use `Protocol` from typing to define interfaces
- This enables better composition and testing
- Example:
  ```python
  from typing import Protocol
  
  class Repository(Protocol):
      def get(self, id: str) -> Optional[Entity]:
          ...
      
      def save(self, entity: Entity) -> None:
          ...
  ```

### Error Handling
- Use specific exceptions rather than generic Exception
- Always include helpful error messages
- Consider using custom exceptions for domain-specific errors

### Logging
- Use structured logging (preferably with `structlog` or similar)
- Include relevant context in log messages
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)

### Configuration
- Never hardcode configuration values
- Use environment variables or configuration files
- Centralize configuration in a config module

## 🚫 What NOT to Do

1. **Don't use direct instantiation** - Always use dependency injection
2. **Don't use inheritance** - Always prefer composition
3. **Don't use relative imports** - Always use absolute imports with package names
4. **Don't commit without running type checking** - MUST run `uv run ty check .`
5. **Don't commit without running Ruff** - Code must be formatted and linted
6. **Don't use pip/poetry commands** - Always use `uv`
7. **Don't hardcode values** - Use configuration
8. **Don't catch generic exceptions** - Be specific
9. **Don't forget type hints** - They're required
10. **Don't commit automatically** - Only commit when explicitly asked by the user

## 📝 Additional Notes

- When in doubt, prioritize clarity over cleverness
- Write tests for new functionality
- Document complex logic with clear comments
- Keep functions small and focused (Single Responsibility Principle)
- Use meaningful variable and function names
- Favor composition over inheritance for flexibility and testability
- Use Protocols to define contracts between components

Remember: The goal is maintainable, testable, and scalable code. Following these guidelines ensures consistency across the project and makes it easier for everyone to contribute.