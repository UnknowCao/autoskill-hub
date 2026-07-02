# Raw Data JSON Schema

## Extraction Mechanism

The DXL exporter performs two passes:
1. **Attribute Discovery**: Iterates all `AttrDef` in the module, builds a whitelist of safe (non-DXL) object attributes.
2. **Object Export**: For each non-deleted object, exports all non-empty attributes present in the whitelist.

The exact attribute set depends on the module's schema — different DOORS modules have different attributes.

## JSON Structure

```json
[
  {
    "id": "REQ-001",
    "abs_ref": 12345,
    "attrs": {
      "Object Heading": "Requirement Title",
      "Object Text": "The system shall...",
      "Object_Status": "Released",
      "Object_Type": "Requirement",
      "Variant": "All",
      "AllocTestAuthority": "SwT",
      ...
    }
  }
]
```

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | DOORS object identifier (e.g. `"REQ-001"`) |
| `abs_ref` | number | Absolute Number (unique within module) |
| `attrs` | object | Key-value map of all non-empty, non-DXL attributes |

### Common Attribute Names (module-dependent)

> **Note**: The table below lists commonly observed attributes. The actual attribute set is
> determined dynamically by each module's `AttrDef` schema — it is neither fixed nor exhaustive.
> Different DOORS modules will expose different attribute names and value sets.

| Attribute | Known Values | Notes |
|-----------|-------------|-------|
| `Object Heading` | Free text | Section/requirement heading |
| `Object Text` | Free text | Main content body |
| `Object_Status` | `Released` · `Draft` · `In Review` · `Rejected` · `Obsolete` | Lifecycle status; exact values are project-defined |
| `Object_Type` | `Requirement` · `Heading` · `Information` · `Note` | Object classification |
| `Variant` | `All` · project-specific variant names | Variant applicability |
| `AllocTestAuthority` | `SwT` · `HwT` · `SysT` · `(empty)` | Test responsibility allocation |
| `Absolute Number` | Integer string | Also available as top-level `abs_ref` |

### Important Notes

- Attributes with empty values are **omitted** from the JSON (sparse format).
- DXL-computed attributes are **excluded** for safety and performance.
- Attribute names are **case-sensitive** and may contain spaces/underscores.
