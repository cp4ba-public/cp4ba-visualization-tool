#!/usr/bin/env python3
"""Fix data structure issues in dependencies file."""

import json
import sys
from pathlib import Path

def fix_data_structure(input_file: str, output_file: str = None):
    """Fix data structure issues."""
    if output_file is None:
        output_file = input_file + ".fixed"
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    fixed_count = 0
    
    for i, item in enumerate(data.get("data", [])):
        # Check if item needs fixing
        needs_fix = False
        
        # Fix missing Capability, app, module
        if "reference" in item:
            ref = item["reference"]
            parts = ref.split("/")
            
            if len(parts) != 3:
                # Simple reference format - convert to full format
                needs_fix = True
                
                # Derive fields from reference
                simple_ref = ref
                
                # Try to parse hyphenated format
                if "-" in simple_ref:
                    parts = simple_ref.split("-", 1)
                    addon_id = parts[0]
                    app_name = simple_ref
                else:
                    addon_id = simple_ref
                    app_name = simple_ref
                
                # Set fields
                if "Capability" not in item:
                    item["Capability"] = addon_id
                if "app" not in item:
                    item["app"] = app_name
                if "module" not in item:
                    item["module"] = "main"
                
                # Update reference
                item["reference"] = f"{item['Capability']}/{item['app']}/{item['module']}"
                
                print(f"Fixed item {i}: '{simple_ref}' → '{item['reference']}'")
                fixed_count += 1
    
    # Save fixed data
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nFixed {fixed_count} items")
    print(f"Output saved to: {output_file}")
    
    if fixed_count > 0:
        print(f"\nReview the changes, then:")
        print(f"  mv {output_file} {input_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fix_data.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    fix_data_structure(input_file, output_file)

