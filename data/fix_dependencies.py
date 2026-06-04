#!/usr/bin/env python3
"""
Comprehensive fix for dependencies data structure.
Handles both 1-part and 2-part reference formats.
"""

import json
import sys
from pathlib import Path


def fix_reference_format(item, index):
    """Fix reference format and add missing fields."""
    if "reference" not in item:
        print(f"  Item {index}: No reference field, skipping")
        return False
    
    ref = item["reference"]
    parts = ref.split("/")
    
    # Already correct format (3 parts)
    if len(parts) == 3:
        # Ensure fields match reference
        if "Capability" not in item:
            item["Capability"] = parts[0]
        if "app" not in item:
            item["app"] = parts[1]
        if "module" not in item:
            item["module"] = parts[2]
        return False
    
    # 2-part format: "Capability/app" → "Capability/app/main"
    elif len(parts) == 2:
        addon_id = parts[0]
        app_name = parts[1]
        module_name = "main"  # Default module
        
        item["Capability"] = addon_id
        item["app"] = app_name
        item["module"] = module_name
        item["reference"] = f"{addon_id}/{app_name}/{module_name}"
        
        print(f"  Item {index}: Fixed 2-part reference")
        print(f"    Before: {ref}")
        print(f"    After:  {item['reference']}")
        return True
    
    # 1-part format: "simple-name" → "simple-name/simple-name/main"
    elif len(parts) == 1:
        simple_ref = ref
        
        # Try to extract addon_id from hyphenated name
        if "-" in simple_ref:
            addon_id = simple_ref.split("-")[0]
        else:
            addon_id = simple_ref
        
        app_name = simple_ref
        module_name = "main"
        
        item["Capability"] = addon_id
        item["app"] = app_name
        item["module"] = module_name
        item["reference"] = f"{addon_id}/{app_name}/{module_name}"
        
        print(f"  Item {index}: Fixed 1-part reference")
        print(f"    Before: {ref}")
        print(f"    After:  {item['reference']}")
        return True
    
    # Invalid format (more than 3 parts)
    else:
        print(f"  Item {index}: WARNING - Invalid reference with {len(parts)} parts: {ref}")
        return False


def fix_dependencies_file(input_file: str, output_file: str = None, dry_run: bool = False):
    """Fix all items in dependencies file."""
    
    if output_file is None:
        output_file = input_file + ".fixed"
    
    print(f"Reading: {input_file}")
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {input_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")
        return False
    
    if "data" not in data:
        print("ERROR: No 'data' field in JSON")
        return False
    
    total_items = len(data["data"])
    fixed_count = 0
    
    print(f"\nProcessing {total_items} items...")
    print("-" * 60)
    
    for i, item in enumerate(data["data"]):
        if fix_reference_format(item, i):
            fixed_count += 1
    
    print("-" * 60)
    print(f"\nSummary:")
    print(f"  Total items: {total_items}")
    print(f"  Fixed items: {fixed_count}")
    print(f"  Unchanged:   {total_items - fixed_count}")
    
    if dry_run:
        print(f"\nDRY RUN - No changes saved")
        return True
    
    # Save fixed data
    print(f"\nSaving to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Done! Fixed {fixed_count} items")
    
    if output_file != input_file:
        print(f"\nTo apply changes:")
        print(f"  mv {output_file} {input_file}")
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix dependencies data structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes)
  python3 fix_dependencies.py public/data/dependencies_5.3.0.json --dry-run
  
  # Fix and save to new file
  python3 fix_dependencies.py public/data/dependencies_5.3.0.json
  
  # Fix in place
  python3 fix_dependencies.py public/data/dependencies_5.3.0.json --in-place
        """
    )
    
    parser.add_argument('input_file', help='Input JSON file')
    parser.add_argument('--output', '-o', help='Output file (default: input_file.fixed)')
    parser.add_argument('--in-place', '-i', action='store_true', 
                       help='Modify file in place (backup created)')
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help='Preview changes without saving')
    
    args = parser.parse_args()
    
    # Determine output file
    if args.in_place:
        # Create backup
        backup_file = args.input_file + ".backup"
        import shutil
        shutil.copy2(args.input_file, backup_file)
        print(f"Backup created: {backup_file}")
        output_file = args.input_file
    else:
        output_file = args.output
    
    # Run fix
    success = fix_dependencies_file(args.input_file, output_file, args.dry_run)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

