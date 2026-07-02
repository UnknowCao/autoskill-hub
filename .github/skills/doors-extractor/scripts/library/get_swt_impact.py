import json
import sys
import os

def process_data(input_file, output_file):
    print(f"Loading raw data from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {input_file}.")
        sys.exit(1)

    extracted_reqs = []
    
    print(f"Processing {len(data)} objects...")
    
    for obj in data:
        attrs = obj.get("attrs", {})
        
        # Filter for AllocTestAuthority == "SwT"
        alloc_auth = attrs.get("AllocTestAuthority")
        
        if alloc_auth == "SwT":
            # Map valid attributes to a cleaner structure
            req_item = {
                "id": obj.get("id"),
                "absolute_number": attrs.get("Absolute Number"),
                "heading": attrs.get("Object Heading", ""),
                "text": attrs.get("Object Text", ""),
                "status": attrs.get("Object_Status"),
                "type": attrs.get("Object_Type"),
                "variant": attrs.get("Variant"),
                "alloc_test_authority": alloc_auth
            }
            extracted_reqs.append(req_item)

    # Save processed data
    out_dir = os.path.dirname(output_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_reqs, f, indent=4, ensure_ascii=False)
    
    # Summary
    print(f"\n--- Summary ---")
    print(f"Total objects:    {len(data)}")
    print(f"SwT allocated:    {len(extracted_reqs)}")
    print(f"Output file:      {output_file}")
    
    # AllocTestAuthority distribution
    from collections import Counter
    alloc_dist = Counter(obj.get("attrs", {}).get("AllocTestAuthority", "(empty)") for obj in data)
    print(f"\nAllocTestAuthority distribution:")
    for alloc, count in alloc_dist.most_common():
        print(f"  {alloc:<20} {count:>6}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: cmd /c \"python {os.path.basename(sys.argv[0])} <input_json> <output_json>\"")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    process_data(input_path, output_path)
