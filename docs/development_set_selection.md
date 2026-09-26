# Development Set Selection for Round 3

## Selection Criteria

Cases were stratified across five dimensions from the 100-case audit:

1. **Graph scale** (non_copy_ops): xsmall (<1000), small (1000-1999), medium (2000-9999), large (10000-24999), xlarge (>=25000)
2. **DAG depth**: shallow (<10), moderate (10-100), deep (100-300), very deep (>300)
3. **Width** (max concurrent ops): narrow, moderate, wide, ultra-wide
4. **Comm/Compute ratio**: low (<10), moderate (10-20), high (20-30), extreme (>30)
5. **PIPE workload balance**: PIPE_M or PIPE_V dominant vs balanced

## Selected 15 Cases

| Case | Scale | Ops | Depth | Width | Components | Comm/Comp | Pipe M:V | Rationale |
|------|-------|-----|-------|-------|------------|-----------|----------|-----------|
| 001  | small | 1001 | 2 | 200 | 200 | 6.22 | 232k:30k | Mandatory; wide-shallow baseline |
| 019  | xsmall | 766 | 78 | 57 | 31 | 18.36 | 48k:40k | Mandatory; regression gate; moderate depth |
| 005  | medium | 4209 | 137 | 196 | 1 | 38.41 | 64k:61k | Mandatory; chain-like; extreme comm/comp |
| 050  | medium | 4781 | 185 | 134 | 23 | 24.71 | 52k:133k | Mandatory; V-dominant pipe; diverse |
| 025  | large | 23997 | 5 | 5332 | 2666 | 8.99 | 4.7M:1.2M | Mandatory; ultra-wide; M-dominant |
| 085  | large | 19993 | 449 | 324 | 1 | 9.33 | 2.6M:1.7M | Mandatory; deep; complex components |
| 014  | xlarge | 38666 | 123 | 15921 | 1340 | 9.20 | 17M:1.7M | Max scale; extreme width; many components |
| 035  | medium | 4237 | 332 | 224 | 16 | 23.79 | 62k:144k | Deep; V-dominant; high fan_out=14 |
| 047  | med-large | 13988 | 459 | 196 | 1 | 18.12 | 154k:259k | Deepest chain; V-dominant pipe |
| 054  | med-large | 16133 | 353 | 324 | 24 | 16.49 | 574k:441k | Deep+wide; multi-component |
| 060  | medium | 6086 | 40 | 1977 | 89 | 17.66 | 720k:274k | Ultra-wide medium; many components |
| 069  | small | 1074 | 45 | 144 | 1 | 36.98 | 17k:15k | Extreme comm/comp; small chain |
| 087  | xlarge | 28666 | 381 | 3066 | 196 | 11.96 | 3.6M:883k | Large deep+wide; moderate comm/comp |
| 093  | xsmall | 901 | 3 | 276 | 69 | 11.49 | 74k:12k | Ultra-shallow; multi-component |
| 100  | small | 1654 | 51 | 187 | 43 | 25.19 | 63k:102k | High fan_out=14; V-dominant |

## Scale Distribution
- xsmall: 2 cases (019, 093)
- small: 3 cases (001, 069, 100)
- medium: 5 cases (005, 050, 035, 054, 060)
- large: 2 cases (025, 085)
- xlarge: 3 cases (014, 047, 087)

## Regression Gates
- case_019: P1/N2, P1/N4, P2/N2, P3/N2 (4 regressions in v2)
- case_019: all problem/core combinations must not degrade beyond v1 results
- Additionally monitor: case_050 (had large v2 improvement), case_085 (mixed)

## Coverage Check
- Depth range: 2 (001) to 459 (047) — full spectrum
- Width range: 57 (019) to 15921 (014) — full spectrum
- Comm/Comp range: 6.22 (001) to 38.41 (005) — full spectrum
- Components: 1 (005) to 2666 (025) — full spectrum
- PIPE balance: M-only, V-dominant, balanced — all covered