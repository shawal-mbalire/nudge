set shell := ["bash", "-uc"]

# --- Global Commands ---

# Install project-wide and system-wide dependencies
deps:
    sha deps
    @echo "Installing module dependencies..."

test:
    @echo "Running tests..."
