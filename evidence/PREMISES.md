# Explicit restricted-rank premises

The compact checker assumes these 110 bounds; `verify.py --mode full` establishes all of them before running it. The published replay checks the original Wang bounds; it does not silently substitute the strengthened values. The campaign has eleven upgrades in its dependency chain (nine are needed, see `docs/RESTRICTED_CHAIN.md`): 70: 13 → 14, 206: 14 → 15, 313: 16 → 17, 423: 17 → 18, 444: 17 → 18, 486: 18 → 19, 487: 18 → 19, 488: 18 → 19, 490: 18 → 19, 491: 18 → 19, 494: 19 → 20. Some upgrades are intermediate dependencies rather than direct compact premises.

| Catalog index | Assumed bound | Published bound | Source of assumed value |
|---:|---:|---:|---|
| 3 | 9 | 9 | published Wang certificate |
| 10 | 12 | 12 | published Wang certificate |
| 11 | 12 | 12 | published Wang certificate |
| 14 | 12 | 12 | published Wang certificate |
| 17 | 14 | 14 | published Wang certificate |
| 23 | 12 | 12 | published Wang certificate |
| 29 | 15 | 15 | published Wang certificate |
| 31 | 15 | 15 | published Wang certificate |
| 35 | 15 | 15 | published Wang certificate |
| 55 | 14 | 14 | published Wang certificate |
| 63 | 14 | 14 | published Wang certificate |
| 65 | 15 | 15 | published Wang certificate |
| 69 | 15 | 15 | published Wang certificate |
| 70 | 14 | 13 | strengthened in this campaign |
| 72 | 15 | 15 | published Wang certificate |
| 80 | 15 | 15 | published Wang certificate |
| 93 | 15 | 15 | published Wang certificate |
| 95 | 15 | 15 | published Wang certificate |
| 96 | 16 | 16 | published Wang certificate |
| 101 | 15 | 15 | published Wang certificate |
| 103 | 15 | 15 | published Wang certificate |
| 111 | 14 | 14 | published Wang certificate |
| 112 | 15 | 15 | published Wang certificate |
| 118 | 15 | 15 | published Wang certificate |
| 119 | 14 | 14 | published Wang certificate |
| 144 | 15 | 15 | published Wang certificate |
| 150 | 16 | 16 | published Wang certificate |
| 152 | 16 | 16 | published Wang certificate |
| 156 | 16 | 16 | published Wang certificate |
| 157 | 15 | 15 | published Wang certificate |
| 158 | 15 | 15 | published Wang certificate |
| 187 | 15 | 15 | published Wang certificate |
| 190 | 15 | 15 | published Wang certificate |
| 194 | 16 | 16 | published Wang certificate |
| 201 | 16 | 16 | published Wang certificate |
| 220 | 15 | 15 | published Wang certificate |
| 231 | 15 | 15 | published Wang certificate |
| 248 | 14 | 14 | published Wang certificate |
| 250 | 15 | 15 | published Wang certificate |
| 251 | 16 | 16 | published Wang certificate |
| 253 | 16 | 16 | published Wang certificate |
| 255 | 16 | 16 | published Wang certificate |
| 261 | 16 | 16 | published Wang certificate |
| 262 | 17 | 17 | published Wang certificate |
| 264 | 16 | 16 | published Wang certificate |
| 267 | 16 | 16 | published Wang certificate |
| 269 | 16 | 16 | published Wang certificate |
| 270 | 15 | 15 | published Wang certificate |
| 274 | 16 | 16 | published Wang certificate |
| 276 | 16 | 16 | published Wang certificate |
| 278 | 16 | 16 | published Wang certificate |
| 279 | 17 | 17 | published Wang certificate |
| 281 | 16 | 16 | published Wang certificate |
| 282 | 17 | 17 | published Wang certificate |
| 283 | 16 | 16 | published Wang certificate |
| 284 | 17 | 17 | published Wang certificate |
| 287 | 17 | 17 | published Wang certificate |
| 289 | 17 | 17 | published Wang certificate |
| 290 | 17 | 17 | published Wang certificate |
| 292 | 16 | 16 | published Wang certificate |
| 295 | 17 | 17 | published Wang certificate |
| 298 | 16 | 16 | published Wang certificate |
| 309 | 17 | 17 | published Wang certificate |
| 315 | 17 | 17 | published Wang certificate |
| 318 | 17 | 17 | published Wang certificate |
| 324 | 16 | 16 | published Wang certificate |
| 332 | 16 | 16 | published Wang certificate |
| 353 | 17 | 17 | published Wang certificate |
| 355 | 17 | 17 | published Wang certificate |
| 356 | 17 | 17 | published Wang certificate |
| 363 | 17 | 17 | published Wang certificate |
| 366 | 17 | 17 | published Wang certificate |
| 371 | 17 | 17 | published Wang certificate |
| 410 | 15 | 15 | published Wang certificate |
| 412 | 17 | 17 | published Wang certificate |
| 414 | 17 | 17 | published Wang certificate |
| 416 | 17 | 17 | published Wang certificate |
| 417 | 17 | 17 | published Wang certificate |
| 419 | 17 | 17 | published Wang certificate |
| 423 | 18 | 17 | strengthened in this campaign |
| 425 | 18 | 18 | published Wang certificate |
| 426 | 18 | 18 | published Wang certificate |
| 427 | 17 | 17 | published Wang certificate |
| 428 | 17 | 17 | published Wang certificate |
| 433 | 17 | 17 | published Wang certificate |
| 435 | 17 | 17 | published Wang certificate |
| 437 | 17 | 17 | published Wang certificate |
| 450 | 18 | 18 | published Wang certificate |
| 451 | 18 | 18 | published Wang certificate |
| 452 | 18 | 18 | published Wang certificate |
| 453 | 18 | 18 | published Wang certificate |
| 454 | 18 | 18 | published Wang certificate |
| 455 | 18 | 18 | published Wang certificate |
| 457 | 18 | 18 | published Wang certificate |
| 458 | 18 | 18 | published Wang certificate |
| 462 | 18 | 18 | published Wang certificate |
| 466 | 18 | 18 | published Wang certificate |
| 469 | 18 | 18 | published Wang certificate |
| 470 | 18 | 18 | published Wang certificate |
| 479 | 18 | 18 | published Wang certificate |
| 480 | 18 | 18 | published Wang certificate |
| 481 | 18 | 18 | published Wang certificate |
| 484 | 18 | 18 | published Wang certificate |
| 485 | 18 | 18 | published Wang certificate |
| 486 | 19 | 18 | strengthened in this campaign |
| 488 | 19 | 18 | strengthened in this campaign |
| 492 | 19 | 19 | published Wang certificate |
| 493 | 19 | 19 | published Wang certificate |
| 494 | 20 | 19 | strengthened in this campaign |
| 495 | 20 | 20 | published Wang certificate |
