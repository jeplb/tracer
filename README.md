# GUI tools

Web-based tools for designing fluorescent probes and planning FACS sorting queries for pooled biobank sample retrieval using the TRACER system.

**Reference:** [Berleant et al. (2025)](https://doi.org/10.1101/2024.04.12.24305660) - "TRACER enables tracking and retrieval of samples in large biobanks using DNA barcodes"

---

## Overview

This repository contains two standalone HTML applications:

| Tool | File | Purpose |
|------|------|---------|
| **Probe designer** | `probe_designer.html` | Design fluorescent DNA probes for sample retrieval |
| **Query planner** | `query_planner.html` | Plan optimized multi-round FACS sorting strategies |

Both tools run entirely in the browser with no server required. Simply open the HTML files directly.

---

## Probe designer

### Purpose

Design fluorescent DNA probes that bind to barcoded samples for retrieval via flow cytometry. The tool generates probe sequences in IDT-compatible format for ordering.

### Probe architecture

The probe designer supports two modes:

#### Standard mode (no amplifier)
```
Probe: (marker + TT) × 3 + barcode_rc

Example:
AGACGAGGCCCTAGATT AGACGAGGCCCTAGATT AGACGAGGCCCTAGATT TATAAGCGGGAGATTC
└──── marker ────┘  └──── marker ────┘  └──── marker ────┘  └─ barcode_rc ─┘
                TT                  TT                  TT
```

#### Amplifier mode (3× signal)
Two oligos are generated:

**Preamplifier probe** (binds to barcode on sample):
```
(splint) × 3 + barcode_rc    [NO TT spacers]

Example:
CGTACACTTACACAT CGTACACTTACACAT CGTACACTTACACAT TATAAGCGGGAGATTC
└─── splint ───┘ └─── splint ───┘ └─── splint ───┘ └─ barcode_rc ─┘
```

**Amplifier** (binds to preamplifier, carries fluorophore):
```
splint_rc + (TT + marker) × 3

Example:
ATGTGTAAGTGTACG TT AGACGAGGCCCTAGA TT AGACGAGGCCCTAGA TT AGACGAGGCCCTAGA
└── splint_rc ─┘    └─── marker ───┘    └─── marker ───┘    └─── marker ───┘
```

### Supported fluorophores

| Name | Prefix | Excitation/Emission |
|------|--------|---------------------|
| Atto 425 | `at425_` | Blue |
| Atto 488 | `at488_` | Green |
| Atto 565 | `at565_` | Orange |
| Alexa Fluor 647 | `af647_` | Red |
| Alexa Fluor 750 | `af750_` | Near-IR |

### Usage

#### Step 1: Load barcode library

Upload a CSV or TSV file with your barcode sequences:

```
Barcode	Sequence
bc_uid_seq0	TATGAGGACGAATCTCCCGCTTATA
bc_uid_seq1	GAGTAATGTCCTCACGCAATTGCCA
bc_uid_seq2	AGCGCCGTGGTTATCGGCGAGGGCA
```

**Requirements:**
- Must have columns named "Barcode" and "Sequence" (case-insensitive)
- Sequences must be at least 15 bp (truncated to 15 bp reverse complement)
- Valid nucleotides: A, T, G, C, N, *
- Duplicate barcode IDs are automatically skipped

#### Step 2: Select barcode and fluorophore

**Single selection mode:**
1. Type in the search box to filter by barcode ID or sequence
2. Select from the autocomplete dropdown
3. Choose a fluorophore from the dropdown

**Bulk selection mode:**
1. Click "Bulk selection mode" button
2. Use checkboxes to select multiple barcodes
3. Filter the list using the search box
4. "Select all" adds all visible (filtered) barcodes

#### Step 3: Configure amplifier (optional)

Check "Use amplifier" to generate preamplifier + amplifier pairs for 3× signal amplification. The amplifier oligo is shared per fluorophore and only added once.

#### Step 4: Add to list and export

1. Click "Add probe" (single) or "Add selected probes" (bulk)
2. Review probes in the list
3. Set optional project name prefix
4. Click "Export for IDT" to download the order file

### Example workflow

**Goal:** Design probes for 3 barcodes (bc001, bc002, bc003) using AF647 fluorophore with amplification.

1. Upload your barcode library CSV
2. Select "Alexa Fluor 647 (AF647)" from fluorophore dropdown
3. Check "Use amplifier"
4. Click "Bulk selection mode"
5. Type "bc00" in filter to narrow results
6. Check boxes for bc001, bc002, bc003
7. Click "Add selected probes"
8. Enter "experiment1" as project name
9. Click "Export for IDT"

**Output file:** `experiment1_2025_01_21_IDT_export.csv`
```
af647_bc001_branch2	CGGTTGCACCCTGTGCGGTTGCACCCTGTGCGGTTGCACCCTGTGTATAAGCGGGAGATTC	100nm
af647_bc002_branch2	CGGTTGCACCCTGTGCGGTTGCACCCTGTGCGGTTGCACCCTGTGCAATTGCGTGAGGACA	100nm
af647_bc003_branch2	CGGTTGCACCCTGTGCGGTTGCACCCTGTGCGGTTGCACCCTGTGTGCCCTCGCCGATAAC	100nm
af647_branch2	CACAGGGTGCAACCGTTCGGTAGCTCATATAT TTCGGTAGCTCATATAT TTCGGTAGCTCATATAT	100nm
```

---

## Query planner

### Purpose

Plan optimized FACS sorting strategies for retrieving samples based on metadata queries. The planner:

- Builds complex Boolean queries (AND/OR combinations)
- Determines required probe barcodes for each condition
- Optimizes range queries using shared digit barcodes
- Handles negative gating for "NOT" conditions
- Plans multi-round sorting when channels are limited

### Barcode encoding system

The planner uses a mixed-radix encoding system where metadata values map to combinations of barcode sequences:

| Field | Type | Encoding |
|-------|------|----------|
| Age | Numeric | Mixed-radix (×25, ×5, ×1 digits) |
| Vaccinated | Boolean | Single barcode (Y) or none (N) |
| Symptomatic | Boolean | Single barcode (Y) or none (N) |
| City | Categorical | Combinatorial (3 barcodes per city) |
| Flight number | Categorical | Combinatorial (3 barcodes per flight) |
| Flight year | Numeric | Mixed-radix (×10, ×1 digits) |
| Flight month | Numeric | Mixed-radix (×3, ×1 digits) |

### Query building

#### Condition types

| Operator | Example | Gating |
|----------|---------|--------|
| `=` (equals) | City = Chicago | Positive: gate on barcode+ |
| `≠` (not equals) | Vaccinated ≠ Yes | Negative: gate on barcode− |
| `in range` | Month BETWEEN June AND August | Optimized: uses shared barcodes |

#### Logic structure

- **OR groups:** Conditions within a group are combined with OR
- **AND between groups:** Groups are combined with AND

```
(Symptomatic = Yes OR Vaccinated ≠ Yes)
  AND
Flight month BETWEEN June AND August
  AND
City = Chicago
  AND
Flight year = 2020
```

### Range query optimization

When querying a range of values, the planner identifies shared digit barcodes to reduce probe count:

**Example:** Flight month June–August (values 6, 7, 8)

| Month | Barcodes |
|-------|----------|
| June (6) | `bc_flight_month_x3_seq2`, `bc_flight_month_x1_seq0` |
| July (7) | `bc_flight_month_x3_seq2`, `bc_flight_month_x1_seq1` |
| August (8) | `bc_flight_month_x3_seq2`, `bc_flight_month_x1_seq2` |

**Optimization:** All three months share `bc_flight_month_x3_seq2`. Instead of needing 6 barcodes, only 1 is required!

### Negative gating

For "NOT" conditions, the planner uses negative gating (selecting barcode-negative population):

- **"Vaccinated ≠ Yes"** → Gate on `bc_vax_seq0` **negative** (−)
- This selects samples that do NOT have the vaccination barcode

### Multi-round planning

When the total probe count exceeds available FACS channels, the planner splits the query across multiple rounds:

**Round 1:** Sort on first set of conditions (e.g., city + year)
**Round 2:** Re-sort the collected pool on remaining conditions (e.g., month + symptoms)

The planner uses a greedy bin-packing algorithm to minimize rounds.

### Usage

#### Step 1: Configure FACS channels

Select the number of fluorophore channels available per sorting round (default: 5).

#### Step 2: Build query

1. Click "+ Add OR group" to start
2. Add conditions using the dropdowns:
   - Select field (Age, City, Vaccinated, etc.)
   - Select operator (=, ≠, in range)
   - Select value(s)
3. Add multiple conditions within a group for OR logic
4. Add multiple groups for AND logic

#### Step 3: Generate sorting plan

Click "Generate sorting plan" to see:

- **Summary:** Total rounds, probes, and channels needed
- **Per-round details:** Which conditions, probes, and gating strategy
- **Optimizations applied:** Range optimization, negative gating
- **Warnings:** Channel overflow if a single condition exceeds available channels

### Example workflow

**Goal:** Retrieve samples matching:
```
(symptomatic OR NOT vaccinated)
  AND flight_city = Chicago
  AND 6 ≤ arrival_month ≤ 8
  AND arrival_year = 2020
```

1. Click "Load example query" to populate this exact query
2. Set channels to 5
3. Click "Generate sorting plan"

**Result:**
```
Round 1 (5/5 channels):
  Probes: +bc_symptomatic_seq0, −bc_vax_seq0, +bc_flight_month_x3_seq2

Round 2 (5/5 channels):
  Probes: +bc_city_seq4, +bc_city_seq3, +bc_city_seq0,
          +bc_flight_year_x10_seq2, +bc_flight_year_x1_seq0

Round 3 (remaining conditions if needed)
```

**Optimizations:**
- Range query (months 6–8) reduced from 6 barcodes to 1 shared barcode
- "NOT vaccinated" uses negative gating instead of positive

### Interpreting the output

#### Probe chips

| Color | Symbol | Meaning |
|-------|--------|---------|
| Green | + | Positive gating (select barcode+ cells) |
| Red | − | Negative gating (select barcode− cells) |

#### Gating strategy

Each row shows:
- **Field name** being queried
- **Barcode logic** (e.g., `bc_city_seq4 AND bc_city_seq3 AND bc_city_seq0`)
- **Notes** about optimizations applied

#### Warnings

- **Channel overflow (red header):** A single condition requires more channels than available. Increase channel count or simplify the query.
- **Multi-round info:** Query requires sequential sorting rounds.

---

## File formats

### Barcode library (input)

CSV or TSV with required columns:

```csv
Barcode,Sequence
bc_uid_001,ATGCATGCATGCATGCATGCATGCA
bc_uid_002,GCTAGCTAGCTAGCTAGCTAGCTAG
```

### IDT export (output)

Tab-separated values for ordering from IDT:

```
probe_id	sequence	scale
at488_bc_uid_001	AGACGAGGCCCTAGATTAGACGAGGCCCTAGATTAGACGAGGCCCTAGATTTGCATGCATGCATGCA	100nm
```

---

## Technical notes

### Sequence processing

- **Reverse complement:** Barcodes are reverse-complemented and truncated to 15 bp for probe binding
- **Uppercase normalization:** All sequences are converted to uppercase
- **Validation:** Only A, T, G, C, N, * characters allowed; minimum 15 bp length

### Security

- All input is HTML-escaped to prevent XSS attacks
- No data is sent to any server; everything runs locally in the browser
- No cookies or local storage used

### Browser compatibility

Tested on modern browsers (Chrome, Firefox, Safari, Edge). No external dependencies required.

---

## Troubleshooting

### Probe designer

**"Barcode ID not found"**
- Ensure the barcode ID exactly matches one in your uploaded library
- Try searching by partial sequence instead

**"Sequence too short"**
- Barcodes must be at least 15 bp for the reverse complement truncation

**Amplifier not appearing**
- The amplifier oligo is only added once per fluorophore
- Check if it's already in the list from a previous probe

### Query planner

**"No probes required"**
- All conditions specify absence of markers (e.g., "vaccinated = No")
- Add at least one positive condition

**"Channel overflow"**
- A single condition (e.g., City = Chicago) requires more probes than available channels
- Increase channels per round or use multiple conditions that share barcodes

**Range optimization not applied**
- Not all ranges have shared digit barcodes
- The planner will use all necessary barcodes and note "complex gating"

---

## License

See repository license file.
