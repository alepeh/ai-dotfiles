#!/usr/bin/env python3
"""
Claude Code Adapter
Transforms universal service configurations into Claude Code MCP config and sub-agents
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any

class ClaudeCodeAdapter:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.services_dir = config_dir / "services"
        self.profiles_dir = config_dir / "profiles"
        
    def load_user_config(self) -> Dict[str, Any]:
        """Load user's service parameter configuration"""
        config_file = self.config_dir / "config.yaml"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def load_service_definition(self, service_name: str) -> Dict[str, Any]:
        """Load a service definition YAML file"""
        service_file = self.services_dir / f"{service_name}.yaml"
        if not service_file.exists():
            raise FileNotFoundError(f"Service definition not found: {service_name}")
        
        with open(service_file, 'r') as f:
            return yaml.safe_load(f)
    
    def load_profile(self, profile_name: str) -> Dict[str, Any]:
        """Load an agent profile YAML file"""
        profile_file = self.profiles_dir / f"{profile_name}.yaml"
        if not profile_file.exists():
            raise FileNotFoundError(f"Profile not found: {profile_name}")
        
        with open(profile_file, 'r') as f:
            return yaml.safe_load(f)
    
    def substitute_parameters(self, text: str, params: Dict[str, str]) -> str:
        """Substitute {param} placeholders in text with actual values"""
        for param, value in params.items():
            text = text.replace(f"{{{param}}}", str(value))
        return text
    
    def generate_mcp_config(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Claude Code MCP server configuration"""
        mcp_config = {"mcpServers": {}}
        
        # Get all services that have configurations
        for service_name, service_params in user_config.items():
            if service_name == "meta":  # Skip meta configuration
                continue
                
            try:
                service_def = self.load_service_definition(service_name)
                
                # Use MCP adapter if available
                if "mcp" in service_def["adapters"]:
                    mcp_adapter = service_def["adapters"]["mcp"]
                    
                    # Substitute parameters in command args
                    args = []
                    for arg in mcp_adapter["args"]:
                        args.append(self.substitute_parameters(arg, service_params))
                    
                    # Substitute parameters in environment variables
                    env = {}
                    for key, value in mcp_adapter.get("env", {}).items():
                        env[key] = self.substitute_parameters(value, service_params)
                    
                    mcp_config["mcpServers"][service_name] = {
                        "command": mcp_adapter["command"],
                        "args": args
                    }
                    
                    if env:
                        mcp_config["mcpServers"][service_name]["env"] = env
                        
            except FileNotFoundError:
                print(f"Warning: Service definition not found for {service_name}")
                continue
        
        return mcp_config
    
    def generate_sub_agent(self, profile_name: str, available_services: List[str]) -> str:
        """Generate Claude Code sub-agent markdown file"""
        profile = self.load_profile(profile_name)
        
        # Filter available services based on profile requirements
        required_services = profile.get("services", {}).get("required", [])
        optional_services = profile.get("services", {}).get("optional", [])
        
        # Only include services that are actually available/configured
        agent_services = []
        for service in required_services:
            if service in available_services:
                agent_services.append(service)
        
        for service in optional_services:
            if service in available_services:
                agent_services.append(service)
        
        # Generate markdown content
        frontmatter = {
            "name": profile["name"],
            "description": profile["description"]
        }
        
        if agent_services:
            frontmatter["tools"] = agent_services
        
        # Create YAML frontmatter
        yaml_content = yaml.dump(frontmatter, default_flow_style=False).strip()
        
        # Create full markdown content
        markdown = f"""---
{yaml_content}
---

{profile["system_prompt"]}
"""
        
        # Add service-specific information if available
        if agent_services:
            markdown += f"\n\nAvailable tools provide access to:\n"
            for service in agent_services:
                try:
                    service_def = self.load_service_definition(service)
                    markdown += f"- {service_def['description']}\n"
                except FileNotFoundError:
                    markdown += f"- {service} integration\n"
        
        return markdown
    
    def install_claude_code_config(self, output_dir: Path = None):
        """Install complete Claude Code configuration"""
        user_config = self.load_user_config()
        
        # Generate MCP configuration
        mcp_config = self.generate_mcp_config(user_config)
        
        # Determine Claude config location
        if output_dir:
            claude_config_path = output_dir / "claude_desktop_config.json"
            agents_dir = output_dir / ".claude" / "agents"
        else:
            # Default Claude Code config location
            home = Path.home()
            if os.name == 'nt':  # Windows
                claude_config_dir = home / "AppData" / "Roaming" / "Claude"
            elif os.uname().sysname == 'Darwin':  # macOS
                claude_config_dir = home / "Library" / "Application Support" / "Claude"
            else:  # Linux
                claude_config_dir = home / ".config" / "Claude"
            
            claude_config_path = claude_config_dir / "claude_desktop_config.json"
            agents_dir = home / ".claude" / "agents"
        
        # Ensure directories exist
        claude_config_path.parent.mkdir(parents=True, exist_ok=True)
        agents_dir.mkdir(parents=True, exist_ok=True)
        
        # Write MCP configuration
        # If config already exists, merge with existing
        existing_config = {}
        if claude_config_path.exists():
            with open(claude_config_path, 'r') as f:
                existing_config = json.load(f)
        
        # Merge MCP servers
        if "mcpServers" not in existing_config:
            existing_config["mcpServers"] = {}
        
        existing_config["mcpServers"].update(mcp_config["mcpServers"])
        
        with open(claude_config_path, 'w') as f:
            json.dump(existing_config, f, indent=2)
        
        print(f"✓ Updated Claude Code MCP config: {claude_config_path}")
        
        # Generate all available profiles as sub-agents
        available_services = list(user_config.keys())
        if "meta" in available_services:
            available_services.remove("meta")
        
        profile_files = list(self.profiles_dir.glob("*.yaml"))
        for profile_file in profile_files:
            profile_name = profile_file.stem
            
            try:
                agent_content = self.generate_sub_agent(profile_name, available_services)
                agent_file = agents_dir / f"{profile_name}.md"
                
                with open(agent_file, 'w') as f:
                    f.write(agent_content)
                
                print(f"✓ Generated sub-agent: {agent_file}")
                
            except Exception as e:
                print(f"✗ Failed to generate {profile_name}: {e}")

def main():
    """CLI entry point for Claude Code adapter"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python claude_code.py <config_dir> [output_dir]")
        sys.exit(1)
    
    config_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    adapter = ClaudeCodeAdapter(config_dir)
    adapter.install_claude_code_config(output_dir)

if __name__ == "__main__":
    main()