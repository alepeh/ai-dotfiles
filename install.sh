#!/bin/bash
# AI Dotfiles Installation Script
# Sets up the Universal AI Tool Configuration Management System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/.ai-dotfiles"
REPO_URL="https://github.com/your-username/ai-dotfiles.git"  # Update with actual repo

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is available and setup virtual environment
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    local venv_dir="$INSTALL_DIR/venv"
    if [[ ! -d "$venv_dir" ]]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv "$venv_dir"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source "$venv_dir/bin/activate"
    
    # Upgrade pip in virtual environment
    python -m pip install --upgrade pip
    
    # Check if PyYAML is available
    if ! python -c "import yaml" 2>/dev/null; then
        print_warning "PyYAML not found. Installing..."
        pip install pyyaml
    fi
}

# Install ai-dotfiles
install_ai_dotfiles() {
    print_status "Installing AI Dotfiles to $INSTALL_DIR"
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    
    # If we're running from the repo directory, copy files
    if [[ -f "ai-dotfiles" && -d "services" && -d "profiles" ]]; then
        print_status "Installing from local directory"
        cp -r . "$INSTALL_DIR/"
    else
        print_error "Installation files not found. Please run from the ai-dotfiles directory."
        exit 1
    fi
    
    # Make CLI script executable and update it to use virtual environment
    chmod +x "$INSTALL_DIR/ai-dotfiles"
    
    # Update the CLI script to use the virtual environment
    if [[ -f "$INSTALL_DIR/ai-dotfiles" ]]; then
        # Create a wrapper script that activates the virtual environment
        local wrapper_script="$INSTALL_DIR/ai-dotfiles-wrapper"
        cat > "$wrapper_script" << 'EOF'
#!/bin/bash
# AI Dotfiles wrapper script that activates virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
exec python "$SCRIPT_DIR/ai-dotfiles" "$@"
EOF
        chmod +x "$wrapper_script"
        mv "$wrapper_script" "$INSTALL_DIR/ai-dotfiles"
    fi
    
    print_success "AI Dotfiles installed to $INSTALL_DIR"
}

# Create symlink for global access
create_symlink() {
    local bin_dir="$HOME/.local/bin"
    mkdir -p "$bin_dir"
    
    if [[ -L "$bin_dir/ai-dotfiles" ]]; then
        rm "$bin_dir/ai-dotfiles"
    fi
    
    ln -s "$INSTALL_DIR/ai-dotfiles" "$bin_dir/ai-dotfiles"
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_warning "~/.local/bin is not in your PATH"
        echo "Add this line to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
    
    print_success "AI Dotfiles CLI available as 'ai-dotfiles'"
}

# Create initial configuration
create_initial_config() {
    local config_file="$INSTALL_DIR/config.yaml"
    
    if [[ ! -f "$config_file" ]]; then
        print_status "Creating initial configuration template"
        
        cat > "$config_file" << 'EOF'
# AI Dotfiles Configuration
# Configure your services by setting the required parameters

# Example service configurations:
# obsidian:
#   vault_path: "~/Documents/MyVault"
#   api_key: "your_api_key_here"  # Optional, for REST API access
#   host: "localhost"             # Optional
#   port: 27123                   # Optional

# github:
#   api_token: "ghp_your_token_here"
#   default_org: "your-org"       # Optional

# filesystem:
#   allowed_paths: "~/Projects,~/Documents"

# confluence:
#   base_url: "https://your-company.atlassian.net"
#   api_token: "your_confluence_token"
#   space_key: "DEV"              # Optional

# mermaid:
#   output_dir: "./diagrams"      # Optional
#   theme: "default"              # Optional
EOF
        
        print_success "Created configuration template at $config_file"
        print_status "Edit this file to configure your services"
    else
        print_status "Configuration file already exists at $config_file"
    fi
}

# Show next steps
show_next_steps() {
    echo
    print_success "Installation completed!"
    echo
    echo "Next steps:"
    echo "1. Edit your configuration: $INSTALL_DIR/config.yaml"
    echo "2. Configure your services:"
    echo "   ai-dotfiles config set obsidian.vault_path ~/Documents/MyVault"
    echo "   ai-dotfiles config set github.api_token ghp_your_token_here"
    echo "3. Install configurations for your tools:"
    echo "   ai-dotfiles install claude-code"
    echo "   ai-dotfiles install cursor"
    echo "   ai-dotfiles install continue"
    echo "4. Or sync to all tools at once:"
    echo "   ai-dotfiles sync"
    echo
    echo "Available commands:"
    echo "   ai-dotfiles list services    # Show available services"
    echo "   ai-dotfiles list profiles    # Show available agent profiles"
    echo "   ai-dotfiles config show      # Show current configuration"
    echo "   ai-dotfiles --help           # Show all commands"
}

# Main installation process
main() {
    echo "AI Dotfiles - Universal AI Tool Configuration Management"
    echo "======================================================="
    echo
    
    check_python
    install_ai_dotfiles
    create_symlink
    create_initial_config
    show_next_steps
}

main "$@"