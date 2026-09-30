# Header-only dataset templates

These files have column headers and **zero data rows**. They are contracts/examples for T005/T031, not datasets claimed collected or validated. [Schema](../../docs/06_SCHEMA.md) and [data lifecycle](../../docs/18_DATA_PROVENANCE.md) own full types/relationships.

| Family | Template files |
|---|---|
| Material | [Catalog](material_catalog.csv), [observations](material_observations.csv) |
| Price | [Observations](price_observations.csv) |
| Recycler | [Directory export](recyclers.csv) |
| Transaction | [Transactions](transactions.csv) |
| Traceability | [Events](traceability.csv) |
| Collector | [Minimal pseudonymized profiles](collectors.csv) |
| AI/ML Training | [Licensed asset metadata](ai_training.csv) |
| Shared lineage | [Sources](sources.csv), [field assertions](field_lineage.csv) |

UTF-8; comma delimiter with proper CSV quoting; UTC ISO times; integer paise/grams; explicit currency/unit; empty optional fields mean null, not zero/false. JSON arrays in list columns must be valid quoted JSON. Boolean values are true/false with null where unknown. Stable UUID foreign keys must resolve in the versioned export; pseudonyms replace internal collector IDs consistently. Registry CSV is a flattened view; authorizations/materials/operational fields remain normalized and individually sourced in the DB.

The traceability CSV is an index; its manifest also includes the canonical event payload JSON needed to verify hashes. A hash column alone cannot reconstruct evidence. Media may be represented by authorized references/checksums, never private permanent public links. Every export has a schema/version/source/count/checksum manifest and a completed [data card](../../docs/templates/DATA_CARD.md). Training assets are not redistributed unless permitted; metadata can document a permitted download workflow instead.
