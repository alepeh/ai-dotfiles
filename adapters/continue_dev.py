#!/usr/bin/env python3
"""
Continue.dev Adapter
Transforms universal service configurations into Continue.dev configuration
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any

class ContinueAdapter:
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
    
    def generate_continue_config(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Continue.dev configuration"""
        continue_config = {
            "models": [],
            "customCommands": [],
            "contextProviders": [],
            "slashCommands": []
        }
        
        # Configure context providers
        for service_name, service_params in user_config.items():
            if service_name == "meta":
                continue
                
            try:
                service_def = self.load_service_definition(service_name)
                
                # Handle different service types for Continue
                if service_def["type"] == "knowledge-management":
                    if service_name == "obsidian" and "vault_path" in service_params:
                        continue_config["contextProviders"].append({
                            "name": "obsidian",
                            "params": {
                                "vault": service_params["vault_path"]
                            }
                        })
                
                elif service_def["type"] == "code-repository":
                    if service_name == "github" and "api_token" in service_params:
                        continue_config["contextProviders"].append({
                            "name": "github",
                            "params": {
                                "token": service_params["api_token"],
                                "repo": service_params.get("default_repo", "")
                            }
                        })
                
                elif service_def["type"] == "file-access":
                    if service_name == "filesystem" and "allowed_paths" in service_params:
                        continue_config["contextProviders"].append({
                            "name": "filesystem",
                            "params": {
                                "dirs": service_params["allowed_paths"].split(",")
                            }
                        })
                
            except FileNotFoundError:
                print(f"Warning: Service definition not found for {service_name}")
                continue
        
        # Generate slash commands for each profile
        available_services = [s for s in user_config.keys() if s != "meta"]
        profile_files = list(self.profiles_dir.glob("*.yaml"))
        
        for profile_file in profile_files:
            profile_name = profile_file.stem
            
            try:
                profile = self.load_profile(profile_name)
                
                # Create slash command for this agent
                continue_config["slashCommands"].append({
                    "name": profile_name.replace("-", ""),
                    "description": profile["description"],
                    "run": f"Act as a {profile['description']}. {profile['system_prompt'][:200]}..."
                })
                
            except Exception as e:
                print(f"Warning: Failed to load profile {profile_name}: {e}")
        
        return continue_config
    
    def install_continue_config(self, output_dir: Path = None):
        """Install Continue.dev configuration"""
        user_config = self.load_user_config()
        continue_config = self.generate_continue_config(user_config)
        
        # Determine Continue config location
        if output_dir:
            continue_config_path = output_dir / "continue_config.json"
        else:
            # Default Continue config location
            home = Path.home()
            continue_config_dir = home / ".continue"
            continue_config_path = continue_config_dir / "config.json"
        
        # Ensure directory exists
        continue_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Merge with existing configuration
        existing_config = {}
        if continue_config_path.exists():
            with open(continue_config_path, 'r') as f:
                existing_config = json.load(f)
        
        # Merge configurations (preserve existing models, add our additions)
        for key, value in continue_config.items():
            if key in existing_config and isinstance(existing_config[key], list):
                # Remove existing items with same names to avoid duplicates
                if key == "slashCommands":
                    existing_names = {cmd.get("name") for cmd in existing_config[key]}
                    new_commands = [cmd for cmd in value if cmd.get("name") not in existing_names]
                    existing_config[key].extend(new_commands)
                elif key == "contextProviders":
                    existing_names = {cp.get("name") for cp in existing_config[key]}
                    new_providers = [cp for cp in value if cp.get("name") not in existing_names]
                    existing_config[key].extend(new_providers)
                else:
                    existing_config[key].extend(value)
            else:
                existing_config[key] = value
        
        with open(continue_config_path, 'w') as f:
            json.dump(existing_config, f, indent=2)
        
        print(f"✓ Updated Continue.dev configuration: {continue_config_path}")

def main():
    """CLI entry point for Continue adapter"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python continue.py <config_dir> [output_dir]")
        sys.exit(1)
    
    config_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    adapter = ContinueAdapter(config_dir)
    adapter.install_continue_config(output_dir)

if __name__ == "__main__":
    main()