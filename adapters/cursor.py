#!/usr/bin/env python3
"""
Cursor IDE Adapter
Transforms universal service configurations into Cursor IDE configuration
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any

class CursorAdapter:
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
    
    def generate_cursor_config(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Cursor IDE configuration"""
        cursor_config = {
            "cursor.aiConfig": {
                "knowledgeSources": [],
                "contextProviders": [],
                "agents": {}
            }
        }
        
        # Configure knowledge sources
        for service_name, service_params in user_config.items():
            if service_name == "meta":
                continue
                
            try:
                service_def = self.load_service_definition(service_name)
                
                # Handle different service types for Cursor
                if service_def["type"] == "knowledge-management":
                    # Add as knowledge source
                    if service_name == "obsidian" and "vault_path" in service_params:
                        cursor_config["cursor.aiConfig"]["knowledgeSources"].append({
                            "type": "obsidian",
                            "path": service_params["vault_path"],
                            "indexingEnabled": True
                        })
                
                elif service_def["type"] == "code-repository":
                    # Add as context provider
                    if service_name == "github" and "api_token" in service_params:
                        cursor_config["cursor.aiConfig"]["contextProviders"].append({
                            "name": "github",
                            "config": {
                                "token": service_params["api_token"],
                                "repositories": ["*"]
                            }
                        })
                
            except FileNotFoundError:
                print(f"Warning: Service definition not found for {service_name}")
                continue
        
        # Generate agent configurations
        available_services = [s for s in user_config.keys() if s != "meta"]
        profile_files = list(self.profiles_dir.glob("*.yaml"))
        
        for profile_file in profile_files:
            profile_name = profile_file.stem
            
            try:
                profile = self.load_profile(profile_name)
                
                # Filter services for this agent
                required_services = profile.get("services", {}).get("required", [])
                optional_services = profile.get("services", {}).get("optional", [])
                
                agent_services = []
                for service in required_services + optional_services:
                    if service in available_services:
                        agent_services.append(service)
                
                # Create agent configuration
                cursor_config["cursor.aiConfig"]["agents"][profile_name] = {
                    "name": profile["name"],
                    "description": profile["description"],
                    "systemPrompt": profile["system_prompt"],
                    "tools": agent_services
                }
                
            except Exception as e:
                print(f"Warning: Failed to load profile {profile_name}: {e}")
        
        return cursor_config
    
    def install_cursor_config(self, output_dir: Path = None):
        """Install Cursor IDE configuration"""
        user_config = self.load_user_config()
        cursor_config = self.generate_cursor_config(user_config)
        
        # Determine Cursor config location
        if output_dir:
            cursor_config_path = output_dir / "cursor_settings.json"
        else:
            # Default Cursor config locations
            home = Path.home()
            if os.name == 'nt':  # Windows
                cursor_config_dir = home / "AppData" / "Roaming" / "Cursor" / "User"
            elif os.uname().sysname == 'Darwin':  # macOS
                cursor_config_dir = home / "Library" / "Application Support" / "Cursor" / "User"
            else:  # Linux
                cursor_config_dir = home / ".config" / "Cursor" / "User"
            
            cursor_config_path = cursor_config_dir / "settings.json"
        
        # Ensure directory exists
        cursor_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Merge with existing configuration
        existing_config = {}
        if cursor_config_path.exists():
            with open(cursor_config_path, 'r') as f:
                existing_config = json.load(f)
        
        # Merge configurations
        existing_config.update(cursor_config)
        
        with open(cursor_config_path, 'w') as f:
            json.dump(existing_config, f, indent=2)
        
        print(f"✓ Updated Cursor configuration: {cursor_config_path}")

def main():
    """CLI entry point for Cursor adapter"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cursor.py <config_dir> [output_dir]")
        sys.exit(1)
    
    config_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    adapter = CursorAdapter(config_dir)
    adapter.install_cursor_config(output_dir)

if __name__ == "__main__":
    main()