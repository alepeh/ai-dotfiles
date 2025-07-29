# AI Dotfiles

Universal AI Tool Configuration Management System

## Overview

AI Dotfiles provides a centralized way to manage configurations for multiple AI-powered development tools. Instead of maintaining separate configurations for Claude Code, Cursor, Continue.dev, and other AI tools, you define your services once and automatically generate tool-specific configurations.

## Key Features

- **Universal Service Definitions**: Configure services like Obsidian, GitHub, filesystem access once
- **Agent Profiles**: Pre-built specialist agents (architect, note-manager, code-reviewer, etc.)
- **Tool Adapters**: Automatic configuration generation for different AI tools
- **Sub-Agent Support**: Tools like Claude Code get specialized sub-agents automatically
- **Simple CLI**: Easy configuration management and synchronization

## Quick Start

### Installation

```bash
# Clone or download the ai-dotfiles repository
git clone https://github.com/your-username/ai-dotfiles.git
cd ai-dotfiles

# Run the installation script
./install.sh
```

### Basic Configuration

```bash
# Configure your services
ai-dotfiles config set obsidian.vault_path "~/Documents/MyVault"  
ai-dotfiles config set github.api_token "ghp_your_token_here"
ai-dotfiles config set filesystem.allowed_paths "~/Projects,~/Documents"

# Install configurations for your tools
ai-dotfiles install claude-code
ai-dotfiles install cursor
ai-dotfiles install continue

# Or sync to all tools at once
ai-dotfiles sync
```

## Available Services

- **obsidian**: Note-taking and knowledge management
- **github**: Repository management and code collaboration  
- **filesystem**: Local file system access
- **mermaid**: Diagram generation
- **confluence**: Team documentation platform

View all services: `ai-dotfiles list services`

## Available Agent Profiles

All profiles are pre-installed and automatically available:

- **software-architect**: C4 model architecture documentation specialist
- **note-manager**: Personal knowledge management specialist
- **code-reviewer**: Code quality and security review specialist
- **data-scientist**: Data analysis and machine learning specialist
- **technical-writer**: Technical documentation specialist

View all profiles: `ai-dotfiles list profiles`

## Supported Tools

- **claude-code**: MCP server configuration + sub-agent generation
- **cursor**: IDE configuration with agents and context providers
- **continue**: VS Code extension with slash commands and context providers

View all tools: `ai-dotfiles list tools`

## CLI Reference

### Configuration Management
```bash
# Show current configuration
ai-dotfiles config show

# Set configuration values
ai-dotfiles config set <key> <value>
ai-dotfiles config set obsidian.vault_path "~/Documents/Vault"
ai-dotfiles config set github.api_token "ghp_token"

# Get configuration values
ai-dotfiles config get obsidian.vault_path
```

### Tool Installation
```bash
# Install for specific tool
ai-dotfiles install claude-code
ai-dotfiles install cursor
ai-dotfiles install continue

# Sync to all supported tools
ai-dotfiles sync

# Test installation (output to directory)
ai-dotfiles install claude-code --output-dir ./test-output
```

### Information Commands
```bash
# List available items
ai-dotfiles list services
ai-dotfiles list profiles
ai-dotfiles list tools

# Show help
ai-dotfiles --help
```

## License

MIT License - see LICENSE file for details