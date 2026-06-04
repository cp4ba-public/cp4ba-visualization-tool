#!/usr/bin/env python3
"""
Fix Kubernetes kind naming in dependencies data.
Converts all kinds to proper PascalCase format.
Compatible with Python 3.6+
"""

import json
import sys
from pathlib import Path
from typing import Tuple  # For Python 3.6+ compatibility


# Mapping of incorrect kinds to correct PascalCase
KIND_CORRECTIONS = {
    # Lowercase to PascalCase
    "configmap": "ConfigMap",
    "secret": "Secret",
    "service": "Service",
    "deployment": "Deployment",
    "statefulset": "StatefulSet",
    "replicaset": "ReplicaSet",
    "pod": "Pod",
    "job": "Job",
    "cronjob": "CronJob",
    "persistentvolumeclaim": "PersistentVolumeClaim",
    "networkpolicy": "NetworkPolicy",
    "route": "Route",
    "certificate": "Certificate",
    "cluster": "Cluster",
    "etcdcluster": "EtcdCluster",
    "rolebinding": "RoleBinding",
    "serviceaccount": "ServiceAccount",
    "zenextension": "ZenExtension",
    
    # Partial PascalCase to correct PascalCase
    "Configmap": "ConfigMap",
    "Statefulset": "StatefulSet",
    "Replicaset": "ReplicaSet",
    "Persistentvolumeclaim": "PersistentVolumeClaim",
    "Rolebinding": "RoleBinding",
    "Serviceaccount": "ServiceAccount",
    "Zenextension": "ZenExtension",
    "Etcdcluster": "EtcdCluster",
    "Elasticsearchcluster": "ElasticsearchCluster",
    
    # Plural to singular
    "deployments": "Deployment",
    
    # Abbreviations to full names
    "pvc": "PersistentVolumeClaim",
    "sts": "StatefulSet",
    "cm": "ConfigMap",
    "svc": "Service",
    
    # Case corrections
    "horizontalpodautoscaler": "HorizontalPodAutoscaler",
    "zenextension": "ZenExtension",
    "foundationdbcluster": "FoundationDBCluster",
    
    # Special cases
    "wxd": "WXD",  # Keep as-is (custom resource)
}


def fix_kind_name(kind):
    # type: (str) -> Tuple[str, bool]
    """
    Fix kind name to proper PascalCase.
    Returns: (corrected_kind, was_changed)
    """
    if kind in KIND_CORRECTIONS:
        return KIND_CORRECTIONS[kind], True
    
    # Already correct
    return kind, False


def fix_kinds_in_file(input_file, output_file=None, dry_run=False):
    # type: (str, str, bool) -> bool
    """Fix all kind names in dependencies file."""
    
    if output_file is None:
        output_file = input_file + ".kinds_fixed"
    
    print("Reading: {}".format(input_file))
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except IOError:
        print("ERROR: File not found: {}".format(input_file))
        return False
    except json.JSONDecodeError as e:
        print("ERROR: Invalid JSON: {}".format(e))
        return False
    except ValueError as e:  # Python 3.6 compatibility
        print("ERROR: Invalid JSON: {}".format(e))
        return False
    
    if "data" not in data:
        print("ERROR: No 'data' field in JSON")
        return False
    
    total_objects = 0
    fixed_count = 0
    kind_changes = {}
    
    print("\nProcessing items...")
    print("-" * 70)
    
    for i, item in enumerate(data["data"]):
        if "k8s_objects" not in item:
            continue
        
        for obj in item["k8s_objects"]:
            if "kind" not in obj:
                continue
            
            total_objects += 1
            original_kind = obj["kind"]
            corrected_kind, was_changed = fix_kind_name(original_kind)
            
            if was_changed:
                obj["kind"] = corrected_kind
                fixed_count += 1
                
                # Track changes
                if original_kind not in kind_changes:
                    kind_changes[original_kind] = {
                        "corrected_to": corrected_kind,
                        "count": 0
                    }
                kind_changes[original_kind]["count"] += 1
    
    print("-" * 70)
    print("\nSummary:")
    print("  Total k8s objects: {}".format(total_objects))
    print("  Fixed objects:     {}".format(fixed_count))
    print("  Unchanged:         {}".format(total_objects - fixed_count))
    
    if kind_changes:
        print("\nKind Corrections Made:")
        for original in sorted(kind_changes.keys()):
            info = kind_changes[original]
            print("  '{}' -> '{}' ({} occurrences)".format(
                original, info['corrected_to'], info['count']))
    
    if dry_run:
        print("\nDRY RUN - No changes saved")
        return True
    
    # Save fixed data
    print("\nSaving to: {}".format(output_file))
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("\n✅ Done! Fixed {} kind names".format(fixed_count))
    
    if output_file != input_file:
        print("\nTo apply changes:")
        print("  mv {} {}".format(output_file, input_file))
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix Kubernetes kind naming in dependencies data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes)
  python3 fix_kinds.py public/data/dependencies_5.3.0.json --dry-run
  
  # Fix and save to new file
  python3 fix_kinds.py public/data/dependencies_5.3.0.json
  
  # Fix in place
  python3 fix_kinds.py public/data/dependencies_5.3.0.json --in-place
        """
    )
    
    parser.add_argument('input_file', help='Input JSON file')
    parser.add_argument('--output', '-o', help='Output file (default: input_file.kinds_fixed)')
    parser.add_argument('--in-place', '-i', action='store_true',
                       help='Modify file in place (backup created)')
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help='Preview changes without saving')
    
    args = parser.parse_args()
    
    # Determine output file
    if args.in_place:
        # Create backup
        backup_file = args.input_file + ".backup2"
        import shutil
        shutil.copy2(args.input_file, backup_file)
        print("Backup created: {}".format(backup_file))
        output_file = args.input_file
    else:
        output_file = args.output
    
    # Run fix
    success = fix_kinds_in_file(args.input_file, output_file, args.dry_run)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

