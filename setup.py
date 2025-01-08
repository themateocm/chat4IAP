#!/usr/bin/env python3

import os
import sys
import argparse
from typing import Dict, Optional
from dotenv import load_dotenv

def load_env(env_path: str = '.env') -> Dict[str, str]:
    """Load environment variables from .env file"""
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def save_env(env_vars: Dict[str, str], env_path: str = '.env') -> None:
    """Save environment variables to .env file, preserving comments"""
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
        
    # Get existing comments and empty lines
    comments = [line for line in lines if line.strip().startswith('#') or not line.strip()]
    
    # Create new content with variables
    content = []
    for line in comments:
        content.append(line.rstrip('\n'))
    
    # Add variables
    for key, value in sorted(env_vars.items()):
        content.append(f'{key}={value}')
    
    # Write back to file
    with open(env_path, 'w') as f:
        f.write('\n'.join(content) + '\n')

def get_template_vars(template_path: str = '.env.template') -> Dict[str, Optional[str]]:
    """Get variables from template file with their descriptions"""
    template_vars = {}
    current_comment = []
    
    with open(template_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                current_comment.append(line[1:].strip())
            elif line:
                try:
                    key = line.split('=')[0].strip()
                    template_vars[key] = ' '.join(current_comment) if current_comment else None
                    current_comment = []
                except ValueError:
                    continue
    return template_vars

def main():
    parser = argparse.ArgumentParser(description='Manage environment variables for SimpleChat')
    parser.add_argument('action', choices=['view', 'set', 'list'], help='Action to perform')
    parser.add_argument('--var', help='Variable name for set action')
    parser.add_argument('--value', help='Value for set action')
    parser.add_argument('--env-file', default='.env', help='Path to .env file')
    parser.add_argument('--template-file', default='.env.template', help='Path to .env.template file')
    
    args = parser.parse_args()
    
    # Create .env from template if it doesn't exist
    if not os.path.exists(args.env_file) and os.path.exists(args.template_file):
        print(f"Creating {args.env_file} from template...")
        with open(args.template_file, 'r') as src, open(args.env_file, 'w') as dst:
            dst.write(src.read())
    
    # Load current environment variables
    env_vars = load_env(args.env_file)
    template_vars = get_template_vars(args.template_file)
    
    if args.action == 'view':
        # Display current environment variables with descriptions
        print("\nCurrent Environment Variables:")
        print("-" * 50)
        for key, value in sorted(env_vars.items()):
            desc = template_vars.get(key, '')
            if desc:
                print(f"\n# {desc}")
            print(f"{key}={value}")
    
    elif args.action == 'list':
        # Display all available variables from template with descriptions
        print("\nAvailable Environment Variables:")
        print("-" * 50)
        for key, desc in sorted(template_vars.items()):
            current_value = env_vars.get(key, 'Not set')
            print(f"\n{key}:")
            if desc:
                print(f"Description: {desc}")
            print(f"Current value: {current_value}")
    
    elif args.action == 'set':
        if not args.var:
            print("Error: --var is required for set action")
            sys.exit(1)
            
        if args.var not in template_vars:
            print(f"Warning: {args.var} is not defined in {args.template_file}")
            confirm = input("Do you want to continue? (y/N): ")
            if confirm.lower() != 'y':
                sys.exit(0)
        
        if args.value is None:
            # Interactive mode
            desc = template_vars.get(args.var)
            if desc:
                print(f"\nDescription: {desc}")
            current = env_vars.get(args.var, '')
            if current:
                print(f"Current value: {current}")
            value = input(f"Enter value for {args.var}: ")
        else:
            value = args.value
        
        env_vars[args.var] = value
        save_env(env_vars, args.env_file)
        print(f"\nUpdated {args.var} in {args.env_file}")

if __name__ == '__main__':
    main()
