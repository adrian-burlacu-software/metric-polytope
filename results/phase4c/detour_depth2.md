# Derivation depth with all moves (lift, radial 1–3, uncapped gluing)

code_version `4d88d762fc827dea`, git `97ba6b6bb7b320f74f8eca728fc9b2b6b4fe83c5`

| n | orbits | vertex-only: ∞ | vertex-only histogram | detours: ∞ | detour histogram | max detour depth | last move used (detour, finite) |
|---|---|---|---|---|---|---|---|
| 4 | 1 | 0 | 0:1 | 0 | 0:1 | 0 | {} |
| 5 | 2 | 0 | 0:2 | 0 | 0:2 | 0 | {} |
| 6 | 3 | 0 | 0:3 | 0 | 0:3 | 0 | {} |
| 7 | 13 | 1 | 0:11, 1:1 | 0 | 0:11, 1:2 | 1 | {'lift': 2} |
| 8 | 533 | 380 | 0:108, 1:45 | 266 | 0:108, 1:85, 2:54, 3:19, 4:1 | 4 | {'glue': 15, 'lift': 138, 'radial': 6} |
