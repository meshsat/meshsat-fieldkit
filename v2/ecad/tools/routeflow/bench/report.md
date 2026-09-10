# Freerouting quality programme: experiment report (generated 2026-09-10 16:43)
236 rows (191 configuration keys); verdicts recomputed at report time from the stored metrics.

A verdict marked * was measured over 6 hard DRC types, not the 15 the finish refuses on (`hardset.py`): it is not evidence of a clean board.
Rows are grouped by BOARD; the phase each row ran under is its own column. Before 10 September 2026 the baseline was keyed by phase, and 63 of these rows carried a stored verdict of UNMEASURABLE ("no baseline for C6", "for B15") after their route had already been paid for; they are graded here from the metrics that were stored all along.

### A (56 experiment rows; baseline: 132 router vias, 10693.5 mm, 2051 segments)

| config | phase | pre-route | jar | verdict | Q | router vias | length mm | segments | detour med / p90 | pairs > 1 mm | raw hard / open | stub closed | autoroute min | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fr19_plain | A21 | ed1aeb | 1.9.0 | MET* | 0.828 | 95 | 10428.5 | 1795 | 1.177 / 1.365 | 1 | 0 / 0 | 0 of 0 | 0.0 | 647 |
| fr24_fanout | A21 | dd55ef | 2.4.1 | REGRESSION* | 1.194 | 183 | 10748.2 | 2040 | 1.22 / 1.458 | 1 | 0 / 1 | 1 of 1 | 0.0 | 444 |
| fr24_fanout | A21 | 363243 | 2.4.1 | REGRESSION* | 1.194 | 183 | 10749.0 | 2041 | 1.22 / 1.458 | 1 | 0 / 1 | 1 of 1 | 0.0 | 434 |
| fr24_fanout | A21 | ed1aeb | 2.4.1 | REGRESSION* | 1.194 | 183 | 10749.0 | 2041 | 1.22 / 1.458 | 1 | 0 / 1 | 1 of 1 | 0.0 | 512 |
| fr24_base | A21 | f10081 | 2.4.1 | INELIGIBLE | - | 131 | 10752.2 | 1894 | 1.191 / 1.472 | 1 | - / - | - of - | 0.0 | 468 |
| fr24_fanout | A21 | f10081 | 2.4.1 | INELIGIBLE | - | 183 | 10743.7 | 2029 | 1.22 / 1.458 | 1 | - / - | - of - | 0.0 | 481 |
| fr24_via200 | A21 | f10081 | 2.4.1 | INELIGIBLE | - | 68 | 11149.5 | 1934 | 1.222 / 1.597 | 1 | - / - | - of - | 0.0 | 549 |
| pref_hvhv | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 106 | 10805.6 | 1803 | 1.245 / 1.525 | 0 | - / - | - of - | 0.0 | 100 |
| pref_vhvh | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 110 | 10796.0 | 1771 | 1.213 / 1.691 | 1 | - / - | - of - | 0.0 | 100 |
| ripup400 | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 119 | 10488.6 | 1967 | 1.181 / 1.802 | 1 | - / - | - of - | 0.0 | 107 |
| base | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 65 | 10450.9 | 1941 | 1.181 / 1.889 | 1 | - / - | - of - | 1.24 | 131 |
| via200 | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 51 | 11455.3 | 1988 | 1.25 / 2.184 | 1 | - / - | - of - | 1.13 | 126 |
| via100 | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 55 | 10661.6 | 1920 | 1.241 / 1.853 | 1 | - / - | - of - | 1.36 | 139 |
| via200_ripup200 | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 54 | 11261.9 | 2058 | 1.274 / 2.094 | 1 | - / - | - of - | 0.0 | 119 |
| via200_pref_hvhv | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 59 | 10932.4 | 1911 | 1.217 / 1.75 | 1 | - / - | - of - | 1.23 | 129 |
| planevia20 | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 60 | 10444.1 | 1921 | 1.181 / 1.882 | 1 | - / - | - of - | 1.5 | 147 |
| ripup200 | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 100 | 10372.8 | 1911 | 1.181 / 1.767 | 1 | - / - | - of - | 1.6 | 153 |
| via400 | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 41 | 11358.9 | 2000 | 1.237 / 2.184 | 1 | - / - | - of - | 1.98 | 176 |
| via400_pref_hvhv | A21 | ecb64d | 1.9.0 | INELIGIBLE | - | 49 | 11227.0 | 1967 | 1.221 / 1.855 | 1 | - / - | - of - | 1.83 | 163 |
| fr19_via200 | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 51 | 11455.6 | 1989 | 1.25 / 2.184 | 1 | 0 / 5 | 1 of 1 | 0.0 | 99 |
| fr19_base | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 71 | 10560.1 | 1998 | 1.193 / 1.889 | 1 | 0 / 6 | 2 of 2 | 0.0 | 100 |
| fr24_base | A21 | 363243 | 2.4.1 | INELIGIBLE | - | 132 | 10752.0 | 1897 | 1.191 / 1.472 | 1 | 0 / 3 | 1 of 1 | 0.0 | 427 |
| fr24_via200 | A21 | 363243 | 2.4.1 | INELIGIBLE | - | 69 | 11153.2 | 1954 | 1.222 / 1.597 | 1 | 0 / 5 | 2 of 2 | 0.0 | 503 |
| pref_hvhv | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 106 | 10805.6 | 1803 | 1.245 / 1.525 | 0 | 0 / 2 | 0 of 0 | 0.0 | 74 |
| ripup400 | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 119 | 10497.2 | 1971 | 1.181 / 1.802 | 1 | 0 / 3 | 1 of 1 | 0.0 | 79 |
| pref_vhvh | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 110 | 10795.2 | 1773 | 1.213 / 1.691 | 1 | 0 / 3 | 1 of 1 | 0.0 | 77 |
| via200 | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 51 | 11453.9 | 1990 | 1.25 / 2.184 | 1 | 0 / 5 | 1 of 1 | 0.0 | 101 |
| via200_ripup200 | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 54 | 11262.2 | 2059 | 1.274 / 2.094 | 1 | 0 / 5 | 1 of 1 | 0.0 | 91 |
| via400 | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 44 | 11378.2 | 2019 | 1.237 / 2.184 | 1 | 0 / 7 | 3 of 3 | 1.47 | 137 |
| ripup200 | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 103 | 10468.5 | 1958 | 1.181 / 1.767 | 1 | 0 / 4 | 2 of 2 | 1.15 | 119 |
| base | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 71 | 10560.1 | 1998 | 1.193 / 1.889 | 1 | 0 / 6 | 2 of 2 | 0.0 | 99 |
| via100 | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 60 | 10780.3 | 2015 | 1.249 / 1.853 | 1 | 0 / 8 | 3 of 3 | 1.03 | 110 |
| planevia20 | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 62 | 10575.9 | 1992 | 1.201 / 1.882 | 1 | 0 / 8 | 3 of 3 | 1.02 | 109 |
| via400_pref_hvhv | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 51 | 11343.3 | 2015 | 1.221 / 1.855 | 1 | 0 / 5 | 2 of 2 | 1.34 | 128 |
| via200_pref_hvhv | A21 | 363243 | 1.9.0 | INELIGIBLE | - | 62 | 11072.2 | 1970 | 1.217 / 1.75 | 1 | 0 / 5 | 2 of 2 | 0.0 | 101 |
| fr19_via200 | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 51 | 11454.2 | 1990 | 1.25 / 2.184 | 1 | 0 / 5 | 1 of 1 | 0.0 | 103 |
| fr19_base | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 71 | 10560.9 | 1998 | 1.193 / 1.889 | 1 | 0 / 6 | 2 of 2 | 0.0 | 102 |
| fr24_base | A21 | dd55ef | 2.4.1 | INELIGIBLE | - | 132 | 10752.2 | 1898 | 1.191 / 1.472 | 1 | 0 / 3 | 1 of 1 | 0.0 | 414 |
| fr24_via200 | A21 | dd55ef | 2.4.1 | INELIGIBLE | - | 69 | 11152.9 | 1951 | 1.222 / 1.597 | 1 | 0 / 5 | 2 of 2 | 0.0 | 497 |
| pref_hvhv | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 106 | 10805.1 | 1801 | 1.245 / 1.525 | 0 | 0 / 2 | 0 of 0 | 0.0 | 74 |
| ripup400 | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 119 | 10495.6 | 1970 | 1.181 / 1.802 | 1 | 0 / 3 | 1 of 1 | 0.0 | 81 |
| pref_vhvh | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 110 | 10796.0 | 1773 | 1.213 / 1.691 | 1 | 0 / 3 | 1 of 1 | 0.0 | 77 |
| via200 | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 51 | 11455.5 | 1989 | 1.25 / 2.184 | 1 | 0 / 5 | 1 of 1 | 0.0 | 100 |
| base | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 65 | 10451.5 | 1943 | 1.181 / 1.889 | 1 | 0 / 6 | 1 of 2 | 0.0 | 101 |
| via200_ripup200 | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 54 | 11262.7 | 2060 | 1.274 / 2.094 | 1 | 0 / 5 | 1 of 1 | 0.0 | 90 |
| via400 | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 44 | 11375.3 | 2030 | 1.237 / 2.184 | 1 | 0 / 7 | 3 of 3 | 1.41 | 132 |
| ripup200 | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 103 | 10473.5 | 1939 | 1.181 / 1.767 | 1 | 0 / 4 | 2 of 2 | 1.11 | 115 |
| via100 | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 60 | 10780.3 | 2015 | 1.249 / 1.853 | 1 | 0 / 8 | 3 of 3 | 0.0 | 108 |
| planevia20 | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 62 | 10575.2 | 2005 | 1.201 / 1.882 | 1 | 0 / 8 | 3 of 3 | 1.01 | 108 |
| via400_pref_hvhv | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 51 | 11343.3 | 2015 | 1.221 / 1.855 | 1 | 0 / 5 | 2 of 2 | 1.35 | 130 |
| via200_pref_hvhv | A21 | dd55ef | 1.9.0 | INELIGIBLE | - | 62 | 11072.3 | 1972 | 1.217 / 1.75 | 1 | 0 / 5 | 2 of 2 | 0.0 | 103 |
| fr19_via200 | A21 | ed1aeb | 1.9.0 | INELIGIBLE | - | 51 | 11455.6 | 1989 | 1.25 / 2.184 | 1 | 0 / 5 | 1 of 1 | 1.07 | 119 |
| fr19_base | A21 | ed1aeb | 1.9.0 | INELIGIBLE | - | 71 | 10560.9 | 1998 | 1.193 / 1.889 | 1 | 0 / 6 | 2 of 2 | 1.13 | 121 |
| fr24_plain | A21 | ed1aeb | 2.4.1 | INELIGIBLE | - | 130 | 10659.4 | 1884 | 1.205 / 1.379 | 0 | 0 / 3 | 2 of 2 | 0.0 | 366 |
| fr24_base | A21 | ed1aeb | 2.4.1 | INELIGIBLE | - | 132 | 10752.4 | 1897 | 1.191 / 1.472 | 1 | 0 / 3 | 1 of 1 | 0.0 | 472 |
| fr24_via200 | A21 | ed1aeb | 2.4.1 | INELIGIBLE | - | 69 | 11152.3 | 1949 | 1.222 / 1.597 | 1 | 0 / 5 | 2 of 2 | 0.0 | 575 |

### B (56 experiment rows; baseline: 270 router vias, 24674.7 mm, 4046 segments)

| config | phase | pre-route | jar | verdict | Q | router vias | length mm | segments | detour med / p90 | pairs > 1 mm | raw hard / open | stub closed | autoroute min | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fr19_plain | B14 | cbd9c5 | 1.9.0 | REGRESSION* | - | 266 | 24766.7 | 3787 | 1.152 / 1.377 | 13 | 0 / 0 | 0 of 0 | 4.46 | 433 |
| via200_pref_hvhv | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 124 | 25659.6 | 3741 | 1.194 / 1.478 | 13 | 28 / 2 | 1 of 2 | 6.26 | 526 |
| planevia20 | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 188 | 24729.1 | 3980 | 1.143 / 1.51 | 11 | 13 / 3 | 3 of 3 | 5.67 | 502 |
| base | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 188 | 24731.0 | 3981 | 1.143 / 1.51 | 11 | 12 / 3 | 3 of 3 | 5.89 | 522 |
| fr19_base | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 188 | 24729.2 | 3982 | 1.143 / 1.51 | 11 | 12 / 3 | 3 of 3 | 6.07 | 542 |
| via100 | B14 | cbd9c5 | 1.9.0 | NO_SESSION | - | - | - | - | - / - | - | - / - | - of - | - | 818 |
| ripup200 | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 208 | 24292.0 | 3805 | 1.127 / 1.46 | 12 | 0 / 1 | 0 of 1 | 9.44 | 733 |
| ripup400 | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 248 | 24348.4 | 4103 | 1.133 / 1.502 | 13 | 0 / 4 | 3 of 4 | 6.79 | 578 |
| pref_vhvh | B14 | cbd9c5 | 1.9.0 | NO_SESSION | - | - | - | - | - / - | - | - / - | - of - | - | 972 |
| fr19_via200 | B14 | cbd9c5 | 1.9.0 | NO_SESSION | - | - | - | - | - / - | - | - / - | - of - | - | 1085 |
| pref_hvhv | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 213 | 24641.3 | 3875 | 1.167 / 1.403 | 12 | 0 / 4 | 3 of 4 | 9.74 | 743 |
| fr19_via200 | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 135 | 26454.0 | 4053 | 1.211 / 1.566 | 10 | 6 / 2 | 1 of 2 | 15.49 | 1074 |
| via200_ripup200 | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 129 | 26428.5 | 3916 | 1.213 / 1.575 | 10 | 15 / 3 | 2 of 3 | 10.27 | 774 |
| via400 | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 113 | 27355.9 | 3940 | 1.183 / 1.621 | 11 | 6 / 1 | 1 of 1 | 19.48 | 1334 |
| via400_pref_hvhv | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 97 | 26719.6 | 3767 | 1.21 / 1.675 | 12 | 3 / 3 | 2 of 3 | 21.24 | 1424 |
| fr24_base | B14 | cbd9c5 | 2.4.1 | INELIGIBLE | - | 318 | 23761.2 | 3954 | 1.139 / 1.39 | 12 | 0 / 16 | 10 of 15 | 0.0 | 1567 |
| via200 | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 112 | 25862.1 | 3733 | 1.188 / 1.617 | 10 | 3 / 3 | 0 of 3 | 30.28 | 1982 |
| fr19_planes_via200 | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 106 | 25297.6 | 3640 | 1.202 / 1.616 | 8 | 10 / 25 | 21 of 25 | 7.98 | 582 |
| fr24_fanout | B15 | c44e9c | 2.4.1 | INELIGIBLE | - | 344 | 23882.7 | 3913 | 1.132 / 1.342 | 11 | 0 / 11 | 11 of 11 | 0.0 | 1882 |
| fr24_base | B15 | c44e9c | 2.4.1 | INELIGIBLE | - | 329 | 24197.0 | 3863 | 1.143 / 1.346 | 12 | 0 / 14 | 14 of 14 | 0.0 | 1815 |
| fr24_fanout | B14 | cbd9c5 | 2.4.1 | INELIGIBLE | - | 380 | 23773.9 | 4177 | 1.134 / 1.353 | 11 | 0 / 25 | 20 of 25 | 0.0 | 2263 |
| fr24_via200 | B15 | c44e9c | 2.4.1 | INELIGIBLE | - | 185 | 25340.8 | 3757 | 1.18 / 1.479 | 12 | 0 / 11 | 10 of 11 | 0.0 | 2763 |
| fr19_planes | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 184 | 23074.6 | 3493 | 1.136 / 1.463 | 11 | 24 / 32 | 32 of 32 | 7.15 | 484 |
| fr24_via200 | B14 | cbd9c5 | 2.4.1 | INELIGIBLE | - | 169 | 24722.1 | 3874 | 1.149 / 1.439 | 10 | 26 / 21 | 13 of 20 | 0.0 | 3881 |
| base | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 170 | 24382.9 | 3748 | 1.147 / 1.433 | 11 | 43 / 1 | 1 of 1 | 6.36 | 521 |
| fr19_base | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 170 | 24496.8 | 3962 | 1.152 / 1.45 | 11 | 42 / 1 | 1 of 1 | 6.43 | 526 |
| planevia20 | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 170 | 24381.9 | 3747 | 1.147 / 1.433 | 11 | 42 / 1 | 1 of 1 | 6.32 | 522 |
| fr24_planes | B15 | c44e9c | 2.4.1 | INELIGIBLE | - | 315 | 22752.7 | 3470 | 1.141 / 1.339 | 9 | 0 / 37 | 35 of 37 | 0.0 | 3965 |
| ripup200 | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 220 | 24380.9 | 3872 | 1.144 / 1.518 | 10 | 13 / 0 | 0 of 0 | 8.81 | 683 |
| via200_ripup200 | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 152 | 26502.6 | 3837 | 1.206 / 1.664 | 11 | 3 / 0 | 0 of 0 | 10.65 | 787 |
| via100 | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 139 | 25385.9 | 3814 | 1.16 / 1.461 | 10 | 0 / 4 | 3 of 4 | 9.64 | 722 |
| pref_vhvh | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 210 | 24807.1 | 3474 | 1.167 / 1.39 | 10 | 0 / 5 | 4 of 5 | 14.62 | 954 |
| ripup400 | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 245 | 24478.3 | 4163 | 1.151 / 1.491 | 11 | 12 / 2 | 1 of 2 | 18.55 | 1194 |
| via200_pref_hvhv | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 134 | 25366.1 | 3919 | 1.181 / 1.553 | 13 | 29 / 4 | 4 of 4 | 22.57 | 1481 |
| via400 | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 110 | 27391.0 | 3872 | 1.249 / 1.646 | 10 | 6 / 4 | 3 of 4 | 24.07 | 1586 |
| via400_pref_hvhv | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 114 | 26194.3 | 3700 | 1.22 / 1.597 | 10 | 4 / 3 | 2 of 3 | 28.11 | 1820 |
| via200 | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 138 | 26458.3 | 4061 | 1.21 / 1.579 | 10 | 6 / 3 | 2 of 3 | 26.82 | 1758 |
| pref_hvhv | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 210 | 24322.2 | 3674 | 1.164 / 1.397 | 13 | 0 / 3 | 3 of 3 | 38.46 | 2439 |
| inj_base | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 170 | 24387.4 | 3750 | 1.147 / 1.436 | 11 | 42 / 1 | 1 of 1 | 6.6 | 545 |
| inj_via200 | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 138 | 26458.3 | 4061 | 1.21 / 1.579 | 10 | 6 / 3 | 2 of 3 | 26.94 | 1764 |
| inj24_base | B15 | c44e9c | 2.4.1 | INELIGIBLE | - | 329 | 24204.8 | 3880 | 1.143 / 1.346 | 12 | 0 / 14 | 14 of 14 | 0.0 | 1666 |
| inj24_via200 | B15 | c44e9c | 2.4.1 | INELIGIBLE | - | 183 | 25249.9 | 3737 | 1.181 / 1.479 | 12 | 0 / 11 | 9 of 11 | 0.0 | 2550 |
| no_layer_rules | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 169 | 37777.8 | 4353 | 1.466 / 2.534 | 13 | 10 / 0 | 0 of 0 | 47.28 | 2994 |
| fr19_plain | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 263 | 24394.9 | 3818 | 1.144 / 1.363 | 13 | 13 / 1 | 1 of 1 | 5.24 | 472 |
| fr19_base | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 170 | 24386.4 | 3746 | 1.147 / 1.436 | 11 | 42 / 1 | 1 of 1 | 7.23 | 580 |
| fr19_base | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 188 | 24730.2 | 3983 | 1.143 / 1.51 | 11 | 12 / 3 | 3 of 3 | 6.2 | 544 |
| fr24_plain | B15 | c44e9c | 2.4.1 | INELIGIBLE | - | 328 | 24403.1 | 3819 | 1.161 / 1.356 | 12 | 0 / 10 | 10 of 10 | 0.0 | 1408 |
| fr24_base | B14 | cbd9c5 | 2.4.1 | INELIGIBLE | - | 318 | 23761.9 | 3957 | 1.139 / 1.39 | 12 | 0 / 16 | 10 of 15 | 0.0 | 1531 |
| fr19_via200 | B14 | cbd9c5 | 1.9.0 | INELIGIBLE | - | 112 | 25863.4 | 3734 | 1.188 / 1.617 | 10 | 3 / 3 | 0 of 3 | 30.06 | 1965 |
| fr19_via200 | B15 | c44e9c | 1.9.0 | INELIGIBLE | - | 138 | 26458.3 | 4061 | 1.21 / 1.579 | 10 | 6 / 3 | 2 of 3 | 28.17 | 1839 |
| fr24_fanout | B15 | c44e9c | 2.4.1 | INELIGIBLE | - | 343 | 23879.8 | 3906 | 1.132 / 1.342 | 11 | 0 / 11 | 11 of 11 | 0.0 | 1806 |
| fr24_plain | B14 | cbd9c5 | 2.4.1 | INELIGIBLE | - | 324 | 24598.9 | 3823 | 1.177 / 1.369 | 11 | 0 / 14 | 10 of 14 | 0.0 | 1734 |
| fr24_base | B15 | c44e9c | 2.4.1 | INELIGIBLE | - | 329 | 24200.7 | 3874 | 1.143 / 1.346 | 12 | 0 / 14 | 14 of 14 | 0.0 | 1912 |
| fr24_fanout | B14 | cbd9c5 | 2.4.1 | INELIGIBLE | - | 380 | 23773.8 | 4178 | 1.134 / 1.353 | 11 | 0 / 25 | 20 of 25 | 0.0 | 2380 |
| fr24_via200 | B15 | c44e9c | 2.4.1 | INELIGIBLE | - | 185 | 25340.4 | 3757 | 1.18 / 1.479 | 12 | 0 / 11 | 10 of 11 | 0.0 | 2792 |
| fr24_via200 | B14 | cbd9c5 | 2.4.1 | INELIGIBLE | - | 168 | 24721.2 | 3875 | 1.147 / 1.439 | 11 | 25 / 21 | 13 of 20 | 0.0 | 3763 |

### C (31 experiment rows; baseline: 272 router vias, 21436.4 mm, 2015 segments)

| config | phase | pre-route | jar | verdict | Q | router vias | length mm | segments | detour med / p90 | pairs > 1 mm | raw hard / open | stub closed | autoroute min | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fr19_plain | C6 | f61ffe | 1.9.0 | MET* | 0.816 | 217 | 16121.5 | 1927 | 1.155 / 1.423 | 0 | 0 / 2 | 2 of 2 | 9.02 | 568 |
| pref_vhvh | C6 | 50d65e | 1.9.0 | MET* | 0.864 | 223 | 16861.1 | 2196 | 1.207 / 1.623 | 0 | 0 / 0 | 0 of 0 | 13.32 | 8799 |
| fr24_planes | C6 | f61ffe | 2.4.1 | MET* | 0.898 | 240 | 15769.5 | 2381 | 1.161 / 1.351 | 0 | 0 / 1 | 1 of 1 | 0.0 | 1124 |
| fr24_base | C6 | f61ffe | 2.4.1 | MET* | 0.898 | 240 | 15768.5 | 2383 | 1.161 / 1.351 | 0 | 0 / 1 | 1 of 1 | 0.0 | 1096 |
| via200 | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 195 | 12505.5 | 1929 | 1.142 / 1.576 | 0 | 0 / 28 | 1 of 28 | 0.0 | 4291 |
| fr24_fanout | C6 | 50d65e | 2.4.1 | INELIGIBLE | - | 291 | 13980.2 | 2374 | 1.147 / 1.456 | 0 | 0 / 20 | 2 of 20 | 0.0 | 4832 |
| via400 | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 167 | 13357.5 | 1751 | 1.143 / 1.645 | 0 | 0 / 30 | 0 of 30 | 0.0 | 4316 |
| ripup400 | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 297 | 15089.6 | 2576 | 1.184 / 1.777 | 0 | 0 / 17 | 2 of 17 | 0.0 | 4385 |
| via400_pref_hvhv | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 173 | 14057.3 | 1568 | 1.148 / 1.459 | 0 | 0 / 35 | 5 of 35 | 0.0 | 4509 |
| base | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 214 | 13245.2 | 2151 | 1.15 / 1.564 | 0 | 0 / 23 | 2 of 23 | 0.0 | 4565 |
| planevia20 | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 214 | 13247.9 | 2152 | 1.15 / 1.564 | 0 | 0 / 23 | 3 of 23 | 0.0 | 4554 |
| via100 | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 300 | 15549.2 | 2775 | 1.19 / 1.675 | 0 | 0 / 16 | 3 of 16 | 0.0 | 4686 |
| ripup200 | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 265 | 13830.2 | 2319 | 1.164 / 1.683 | 0 | 0 / 26 | 2 of 26 | 0.0 | 4766 |
| via200_ripup200 | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 217 | 13629.5 | 2204 | 1.184 / 1.728 | 0 | 0 / 21 | 1 of 21 | 0.0 | 5181 |
| via200_pref_hvhv | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 242 | 15138.6 | 2087 | 1.184 / 1.588 | 0 | 0 / 28 | 3 of 28 | 0.0 | 5213 |
| pref_hvhv | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 236 | 13216.2 | 1570 | 1.195 / 1.695 | 0 | 0 / 33 | 2 of 33 | 0.0 | 5500 |
| fr24_via200 | C6 | 50d65e | 2.4.1 | INELIGIBLE | - | 199 | 11830.3 | 1800 | 1.137 / 1.395 | 0 | 0 / 34 | 2 of 34 | 0.0 | 6789 |
| fr24_base | C6 | 50d65e | 2.4.1 | INELIGIBLE | - | 294 | 13788.1 | 2372 | 1.171 / 1.566 | 0 | 0 / 21 | 0 of 21 | 0.0 | 7563 |
| fr19_base | C6 | f61ffe | 1.9.0 | INELIGIBLE | - | 187 | 15628.0 | 2030 | 1.154 / 1.383 | 0 | 0 / 2 | 1 of 2 | 8.12 | 510 |
| fr19_planes_via200 | C6 | f61ffe | 1.9.0 | INELIGIBLE | - | 125 | 14690.1 | 1798 | 1.187 / 1.566 | 0 | 0 / 6 | 0 of 3 | 13.21 | 817 |
| fr19_planes | C6 | f61ffe | 1.9.0 | INELIGIBLE | - | 172 | 14236.0 | 2001 | 1.161 / 1.414 | 0 | 0 / 6 | 2 of 4 | 15.39 | 950 |
| fr19_base | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 214 | 13244.1 | 2154 | 1.146 / 1.564 | 0 | 0 / 23 | 2 of 23 | 0.0 | 4433 |
| fr19_via200 | C6 | 50d65e | 1.9.0 | INELIGIBLE | - | 195 | 12508.3 | 1930 | 1.143 / 1.576 | 0 | 0 / 28 | 1 of 28 | 0.0 | 4314 |
| fr24_planes | C6 | f61ffe | 2.4.1 | INELIGIBLE | - | 248 | 15125.8 | 2542 | 1.172 / 1.387 | 0 | 1 / 4 | 3 of 3 | 0.0 | 2215 |
| fr19_planes_via200 | C6 | f61ffe | 1.9.0 | INELIGIBLE | - | 116 | 15763.2 | 1713 | 1.145 / 1.382 | 0 | 0 / 3 | 1 of 3 | 9.6 | 598 |
| fr19_base | C6 | f61ffe | 1.9.0 | INELIGIBLE | - | 134 | 14757.2 | 1884 | 1.125 / 1.316 | 0 | 0 / 3 | 1 of 3 | 14.63 | 898 |
| fr19_planes | C6 | f61ffe | 1.9.0 | INELIGIBLE | - | 134 | 14756.0 | 1883 | 1.125 / 1.316 | 0 | 0 / 3 | 1 of 3 | 15.47 | 948 |
| fr24_via200 | C6 | f61ffe | 2.4.1 | INELIGIBLE | - | 157 | 15654.4 | 1969 | 1.171 / 1.363 | 0 | 0 / 6 | 3 of 6 | 0.0 | 1947 |
| fr24_plain | C6 | f61ffe | 2.4.1 | INELIGIBLE | - | 274 | 15681.5 | 2340 | 1.159 / 1.369 | 0 | 0 / 2 | 1 of 2 | 0.0 | 1120 |
| fr19_plain | C6 | 4e9480 | 1.9.0 | INELIGIBLE | - | 196 | 14302.8 | 2053 | 1.17 / 1.405 | 0 | 0 / 17 | 10 of 17 | 0.0 | 4124 |
| fr19_plain_p100 | C6 | 4e9480 | 1.9.0 | INELIGIBLE | - | 194 | 14658.2 | 2130 | 1.172 / 1.403 | 0 | 0 / 10 | 5 of 10 | 0.0 | 4926 |

### D (24 experiment rows; baseline: 90 router vias, 3617.6 mm, 958 segments)

| config | phase | pre-route | jar | verdict | Q | router vias | length mm | segments | detour med / p90 | pairs > 1 mm | raw hard / open | stub closed | autoroute min | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pref_vhvh | D7 | b9817b | 1.9.0 | MET* | 0.811 | 61 | 3558.1 | 846 | 1.197 / 1.449 | 0 | 0 / 0 | 0 of 0 | 1.99 | 132 |
| base | D7 | b9817b | 1.9.0 | MET* | 0.811 | 54 | 3747.8 | 961 | 1.247 / 1.68 | 0 | 0 / 1 | 1 of 1 | 1.98 | 131 |
| planevia20 | D7 | b9817b | 1.9.0 | MET* | 0.811 | 54 | 3747.8 | 961 | 1.247 / 1.68 | 0 | 0 / 1 | 1 of 1 | 1.94 | 129 |
| fr19_base | D7 | b9817b | 1.9.0 | MET* | 0.811 | 54 | 3747.8 | 961 | 1.247 / 1.68 | 0 | 0 / 1 | 1 of 1 | 1.51 | 101 |
| fr19_base | D7 | b9817b | 1.9.0 | MET* | 0.811 | 54 | 3747.8 | 961 | 1.247 / 1.68 | 0 | 0 / 1 | 1 of 1 | 1.8 | 120 |
| ripup200 | D7 | b9817b | 1.9.0 | MET* | 0.821 | 58 | 3623.8 | 950 | 1.226 / 1.721 | 0 | 0 / 1 | 1 of 1 | 0.0 | 27 |
| pref_hvhv | D7 | b9817b | 1.9.0 | MET* | 0.840 | 62 | 3526.6 | 972 | 1.207 / 1.481 | 0 | 0 / 1 | 1 of 1 | 1.86 | 124 |
| fr19_plain | D7 | b9817b | 1.9.0 | MET* | 0.887 | 72 | 3547.7 | 923 | 1.217 / 1.509 | 0 | 0 / 0 | 0 of 0 | 0.0 | 29 |
| ripup400 | D7 | b9817b | 1.9.0 | MET* | 0.932 | 76 | 3646.2 | 994 | 1.227 / 1.59 | 0 | 0 / 0 | 0 of 0 | 0.0 | 35 |
| fr24_base | D7 | b9817b | 2.4.1 | MET* | 0.978 | 89 | 3377.8 | 974 | 1.197 / 1.415 | 0 | 0 / 4 | 4 of 4 | 0.0 | 131 |
| fr24_base | D7 | b9817b | 2.4.1 | MET* | 0.978 | 89 | 3377.8 | 974 | 1.197 / 1.415 | 0 | 0 / 4 | 4 of 4 | 0.0 | 139 |
| fr24_fanout | D7 | b9817b | 2.4.1 | MET* | 0.986 | 92 | 3385.9 | 929 | 1.186 / 1.441 | 0 | 0 / 3 | 3 of 3 | 0.0 | 95 |
| fr24_fanout | D7 | b9817b | 2.4.1 | MET* | 0.986 | 92 | 3385.9 | 929 | 1.186 / 1.441 | 0 | 0 / 3 | 3 of 3 | 0.0 | 94 |
| via400_pref_hvhv | D7 | b9817b | 1.9.0 | REGRESSION* | 0.715 | 31 | 4074.6 | 981 | 1.338 / 1.862 | 0 | 0 / 0 | 0 of 0 | 1.86 | 123 |
| via100 | D7 | b9817b | 1.9.0 | REGRESSION* | 0.802 | 50 | 3850.2 | 980 | 1.29 / 1.628 | 0 | 0 / 1 | 1 of 1 | 0.0 | 58 |
| via200_ripup200 | D7 | b9817b | 1.9.0 | REGRESSION* | 0.828 | 53 | 3936.0 | 991 | 1.252 / 1.736 | 0 | 0 / 0 | 0 of 0 | 0.0 | 59 |
| fr24_via200 | D7 | b9817b | 2.4.1 | INELIGIBLE | - | 50 | 3856.3 | 973 | 1.225 / 1.804 | 0 | 0 / 3 | 3 of 3 | 0.0 | 157 |
| via200_pref_hvhv | D7 | b9817b | 1.9.0 | INELIGIBLE | - | 42 | 3824.1 | 892 | 1.309 / 1.579 | 0 | 0 / 1 | 0 of 1 | 1.18 | 83 |
| via200 | D7 | b9817b | 1.9.0 | INELIGIBLE | - | 44 | 4010.4 | 1032 | 1.301 / 2.082 | 0 | 0 / 2 | 1 of 2 | 2.32 | 151 |
| via400 | D7 | b9817b | 1.9.0 | INELIGIBLE | - | 42 | 4235.4 | 959 | 1.348 / 2.193 | 0 | 3 / 1 | 1 of 1 | 2.48 | 161 |
| fr19_via200 | D7 | b9817b | 1.9.0 | INELIGIBLE | - | 44 | 4010.7 | 1034 | 1.301 / 2.082 | 0 | 0 / 2 | 1 of 2 | 1.85 | 121 |
| fr24_plain | D7 | b9817b | 2.4.1 | INELIGIBLE | - | 83 | 3490.4 | 958 | 1.209 / 1.491 | 0 | 0 / 2 | 2 of 2 | 0.0 | 134 |
| fr19_via200 | D7 | b9817b | 1.9.0 | INELIGIBLE | - | 44 | 4010.7 | 1034 | 1.301 / 2.082 | 0 | 0 / 2 | 1 of 2 | 2.32 | 152 |
| fr24_via200 | D7 | b9817b | 2.4.1 | INELIGIBLE | - | 50 | 3856.2 | 972 | 1.225 / 1.804 | 0 | 0 / 3 | 3 of 3 | 0.0 | 181 |

### E (24 experiment rows; baseline: 142 router vias, 3771.8 mm, 773 segments)

| config | phase | pre-route | jar | verdict | Q | router vias | length mm | segments | detour med / p90 | pairs > 1 mm | raw hard / open | stub closed | autoroute min | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | E4 | 3363d5 | 1.9.0 | MET* | 0.668 | 55 | 3816.7 | 660 | 1.147 / 1.636 | 1 | 0 / 0 | 0 of 0 | 0.0 | 28 |
| planevia20 | E4 | 3363d5 | 1.9.0 | MET* | 0.668 | 55 | 3816.7 | 660 | 1.147 / 1.636 | 1 | 0 / 0 | 0 of 0 | 0.0 | 32 |
| fr19_base | E4 | 3363d5 | 1.9.0 | MET* | 0.668 | 55 | 3816.7 | 660 | 1.147 / 1.636 | 1 | 0 / 0 | 0 of 0 | 0.0 | 32 |
| fr19_base | E4 | 3363d5 | 1.9.0 | MET* | 0.668 | 55 | 3816.7 | 660 | 1.147 / 1.636 | 1 | 0 / 0 | 0 of 0 | 0.0 | 27 |
| pref_hvhv | E4 | 3363d5 | 1.9.0 | MET* | 0.689 | 65 | 3679.0 | 648 | 1.132 / 1.341 | 1 | 0 / 0 | 0 of 0 | 0.0 | 205 |
| pref_vhvh | E4 | 3363d5 | 1.9.0 | MET* | 0.691 | 67 | 3674.2 | 629 | 1.11 / 1.369 | 1 | 0 / 0 | 0 of 0 | 0.0 | 169 |
| ripup200 | E4 | 3363d5 | 1.9.0 | MET* | 0.728 | 72 | 3785.0 | 672 | 1.14 / 1.343 | 1 | 0 / 0 | 0 of 0 | 0.0 | 121 |
| fr19_plain | E4 | 3363d5 | 1.9.0 | MET* | 0.746 | 83 | 3650.0 | 630 | 1.125 / 1.251 | 1 | 0 / 0 | 0 of 0 | 0.0 | 157 |
| fr24_plain | E4 | 3363d5 | 2.4.1 | MET* | 0.904 | 120 | 3720.7 | 719 | 1.18 / 1.403 | 1 | 0 / 0 | 0 of 0 | 0.0 | 92 |
| fr24_base | E4 | 3363d5 | 2.4.1 | MET* | 0.919 | 121 | 3765.2 | 748 | 1.18 / 1.459 | 1 | 0 / 0 | 0 of 0 | 0.0 | 54 |
| fr24_base | E4 | 3363d5 | 2.4.1 | MET* | 0.919 | 121 | 3766.6 | 748 | 1.183 / 1.459 | 1 | 0 / 0 | 0 of 0 | 0.0 | 48 |
| fr19_via200 | E4 | 3363d5 | 1.9.0 | REGRESSION* | 0.634 | 33 | 4372.8 | 658 | 1.216 / 1.88 | 1 | 0 / 0 | 0 of 0 | 1.02 | 240 |
| via200 | E4 | 3363d5 | 1.9.0 | REGRESSION* | 0.635 | 33 | 4376.0 | 659 | 1.216 / 1.88 | 1 | 0 / 0 | 0 of 0 | 1.34 | 289 |
| fr19_via200 | E4 | 3363d5 | 1.9.0 | REGRESSION* | 0.635 | 33 | 4376.0 | 659 | 1.216 / 1.88 | 1 | 0 / 0 | 0 of 0 | 1.26 | 269 |
| via200_ripup200 | E4 | 3363d5 | 1.9.0 | REGRESSION* | 0.666 | 44 | 4123.2 | 708 | 1.267 / 1.889 | 1 | 0 / 0 | 0 of 0 | 0.0 | 110 |
| via100 | E4 | 3363d5 | 1.9.0 | REGRESSION* | 0.667 | 41 | 4208.6 | 726 | 1.206 / 1.669 | 1 | 0 / 0 | 0 of 0 | 0.0 | 196 |
| fr24_fanout | E4 | 3363d5 | 2.4.1 | INELIGIBLE | - | 128 | 3770.7 | 686 | 1.155 / 1.355 | 1 | 0 / 1 | 0 of 1 | 0.0 | 65 |
| fr24_via200 | E4 | 3363d5 | 2.4.1 | INELIGIBLE | - | 78 | 3918.6 | 693 | 1.191 / 1.429 | 1 | 0 / 1 | 0 of 1 | 0.0 | 91 |
| via200_pref_hvhv | E4 | 3363d5 | 1.9.0 | INELIGIBLE | - | 50 | 3912.7 | 727 | 1.279 / 1.785 | 1 | 3 / 1 | 0 of 1 | 1.54 | 103 |
| via400_pref_hvhv | E4 | 3363d5 | 1.9.0 | INELIGIBLE | - | 40 | 4129.2 | 716 | 1.232 / 1.658 | 1 | 0 / 1 | 0 of 1 | 2.55 | 163 |
| via400 | E4 | 3363d5 | 1.9.0 | INELIGIBLE | - | 43 | 4568.4 | 715 | 1.248 / 1.872 | 1 | 7 / 0 | 0 of 0 | 3.1 | 196 |
| ripup400 | E4 | 3363d5 | 1.9.0 | INELIGIBLE | - | 65 | 3853.5 | 730 | 1.167 / 1.435 | 1 | 3 / 2 | 0 of 2 | 4.46 | 277 |
| fr24_fanout | E4 | 3363d5 | 2.4.1 | INELIGIBLE | - | 128 | 3771.1 | 687 | 1.155 / 1.355 | 1 | 0 / 1 | 0 of 1 | 0.0 | 69 |
| fr24_via200 | E4 | 3363d5 | 2.4.1 | INELIGIBLE | - | 78 | 3918.6 | 693 | 1.191 / 1.429 | 1 | 0 / 1 | 0 of 1 | 0.0 | 103 |

### Knob classification (effect = router vias or length moved by at least 5 percent against the base config on at least two boards)

| config | boards | router vias delta | length delta | verdicts | class |
|---|---|---|---|---|---|
| fr19_base | E, E, D, D, A, A, C, B, B, B, B | +0.0%, +0.0%, +0.0%, +0.0%, +0.0%, +9.2%, +0.0%, +0.0%, +0.0%, +0.0%, +0.0% | +0.0%, +0.0%, +0.0%, +0.0%, +0.0%, +1.0%, -0.0%, -0.0%, +0.5%, +0.0%, -0.0% | MET, MET, MET, MET, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | WEAK (one board) |
| fr19_plain | E, D, B, B | +50.9%, +33.3%, +41.5%, +54.7% | -4.4%, -5.3%, +0.1%, +0.0% | MET, MET, REGRESSION, INELIGIBLE | EFFECT |
| fr19_planes | B | +8.2% | -5.4% | INELIGIBLE | HARMFUL |
| fr19_planes_via200 | B | -37.6% | +3.8% | INELIGIBLE | HARMFUL |
| fr19_via200 | E, E, D, D, A, A, C, B, B, B | -40.0%, -40.0%, -18.5%, -18.5%, -28.2%, -21.5%, -8.9%, -20.6%, -40.4%, -18.8% | +14.6%, +14.7%, +7.0%, +7.0%, +8.5%, +9.6%, -5.6%, +8.5%, +4.6%, +8.5% | REGRESSION, REGRESSION, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | HARMFUL |
| fr24_base | E, E, D, D, A, A, C, B, B, B, B | +120.0%, +120.0%, +64.8%, +64.8%, +85.9%, +103.1%, +37.4%, +69.1%, +93.5%, +69.1%, +93.5% | -1.3%, -1.3%, -9.9%, -9.9%, +1.8%, +2.9%, +4.1%, -3.9%, -0.8%, -3.9%, -0.7% | MET, MET, MET, MET, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | EFFECT |
| fr24_fanout | E, E, D, D, A, A, C, B, B, B, B | +132.7%, +132.7%, +70.4%, +70.4%, +157.7%, +181.5%, +36.0%, +102.4%, +102.1%, +101.8%, +102.1% | -1.2%, -1.2%, -9.7%, -9.7%, +1.8%, +2.8%, +5.5%, -2.1%, -3.9%, -2.1%, -3.9% | INELIGIBLE, INELIGIBLE, MET, MET, REGRESSION, REGRESSION, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | EFFECT |
| fr24_plain | E, D, B, B | +118.2%, +53.7%, +92.9%, +72.3% | -2.5%, -6.9%, +0.1%, -0.5% | MET, INELIGIBLE, INELIGIBLE, INELIGIBLE | EFFECT |
| fr24_planes | B | +85.3% | -6.7% | INELIGIBLE | HARMFUL |
| fr24_via200 | E, E, D, D, A, A, C, B, B, B, B | +41.8%, +41.8%, -7.4%, -7.4%, -2.8%, +6.2%, -7.0%, +8.8%, -10.1%, +8.8%, -10.6% | +2.7%, +2.7%, +2.9%, +2.9%, +5.6%, +6.7%, -10.7%, +3.9%, -0.0%, +3.9%, -0.0% | INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | HARMFUL |
| inj24_base | B | +93.5% | -0.7% | INELIGIBLE | HARMFUL |
| inj24_via200 | B | +7.6% | +3.6% | INELIGIBLE | HARMFUL |
| inj_base | B | +0.0% | +0.0% | INELIGIBLE | HARMFUL |
| inj_via200 | B | -18.8% | +8.5% | INELIGIBLE | HARMFUL |
| no_layer_rules | B | -0.6% | +54.9% | INELIGIBLE | HARMFUL |
| planevia20 | E, D, A, A, A, C, B, B | +0.0%, +0.0%, -7.7%, -12.7%, -4.6%, +0.0%, +0.0%, +0.0% | +0.0%, +0.0%, -0.1%, +0.1%, +1.2%, +0.0%, -0.0%, -0.0% | MET, MET, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | EFFECT |
| pref_hvhv | E, D, A, A, A, C, B, B | +18.2%, +14.8%, +63.1%, +49.3%, +63.1%, +10.3%, +13.3%, +23.5% | -3.6%, -5.9%, +3.4%, +2.3%, +3.4%, -0.2%, -0.4%, -0.2% | MET, MET, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | EFFECT |
| pref_vhvh | E, D, A, A, A, C, B | +21.8%, +13.0%, +69.2%, +54.9%, +69.2%, +4.2%, +23.5% | -3.7%, -5.1%, +3.3%, +2.2%, +3.3%, +27.3%, +1.7% | MET, MET, INELIGIBLE, INELIGIBLE, INELIGIBLE, MET, INELIGIBLE | EFFECT |
| ripup200 | E, D, A, A, A, C, B, B | +30.9%, +7.4%, +53.8%, +45.1%, +58.5%, +23.8%, +10.6%, +29.4% | -0.8%, -3.3%, -0.7%, -0.9%, +0.2%, +4.4%, -1.8%, -0.0% | MET, MET, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | EFFECT |
| ripup400 | E, D, A, A, A, C, B, B | +18.2%, +40.7%, +83.1%, +67.6%, +83.1%, +38.8%, +31.9%, +44.1% | +1.0%, -2.7%, +0.4%, -0.6%, +0.4%, +13.9%, -1.5%, +0.4% | INELIGIBLE, MET, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | EFFECT |
| via100 | E, D, A, A, A, C, B | -25.5%, -7.4%, -15.4%, -15.5%, -7.7%, +40.2%, -18.2% | +10.3%, +2.7%, +2.0%, +2.1%, +3.1%, +17.4%, +4.1% | REGRESSION, REGRESSION, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | HARMFUL |
| via200 | E, D, A, A, A, C, B, B | -40.0%, -18.5%, -21.5%, -28.2%, -21.5%, -8.9%, -40.4%, -18.8% | +14.7%, +7.0%, +9.6%, +8.5%, +9.6%, -5.6%, +4.6%, +8.5% | REGRESSION, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | HARMFUL |
| via200_pref_hvhv | E, D, A, A, A, C, B, B | -9.1%, -22.2%, -9.2%, -12.7%, -4.6%, +13.1%, -34.0%, -21.2% | +2.5%, +2.0%, +4.6%, +4.8%, +5.9%, +14.3%, +3.8%, +4.0% | INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | HARMFUL |
| via200_ripup200 | E, D, A, A, A, C, B, B | -20.0%, -1.9%, -16.9%, -23.9%, -16.9%, +1.4%, -31.4%, -10.6% | +8.0%, +5.0%, +7.8%, +6.6%, +7.8%, +2.9%, +6.9%, +8.7% | REGRESSION, REGRESSION, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | HARMFUL |
| via400 | E, D, A, A, A, C, B, B | -21.8%, -22.2%, -36.9%, -38.0%, -32.3%, -22.0%, -39.9%, -35.3% | +19.7%, +13.0%, +8.7%, +7.7%, +8.8%, +0.8%, +10.6%, +12.3% | INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | HARMFUL |
| via400_pref_hvhv | E, D, A, A, A, C, B, B | -27.3%, -42.6%, -24.6%, -28.2%, -21.5%, -19.2%, -48.4%, -32.9% | +8.2%, +8.7%, +7.4%, +7.4%, +8.5%, +6.1%, +8.0%, +7.4% | INELIGIBLE, REGRESSION, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE, INELIGIBLE | HARMFUL |

### Stage 4 gate: Freerouting 2.4.1 against 1.9.0 (fr24_plain against fr19_plain per board, no settings block, on the board's newest pre-route; the finish is the production finish)

| board | 1.9.0 session | 2.4.1 session | 1.9.0 hard / open (raw open) | 2.4.1 hard / open (raw open) | 1.9.0 router vias | 2.4.1 router vias | 1.9.0 Q | 2.4.1 Q | board verdict |
|---|---|---|---|---|---|---|---|---|---|
| A | yes | yes | 0 / 0 (0) | 0 / 2 (3) | 95 | 130 | 0.828 | - | FAIL (completion below 1.9.0) |
| B | yes | yes | 12 / 1 (1) | 0 / 4 (10) | 263 | 328 | - | - | FAIL (completion below 1.9.0) |
| D | yes | yes | 0 / 0 (0) | 0 / 1 (2) | 72 | 83 | 0.887 | - | FAIL (completion below 1.9.0) |
| E | yes | yes | 0 / 0 (0) | 0 / 0 (0) | 83 | 120 | 0.746 | 0.904 | REGRESSED |

Gate verdict: NOT MET, 1.9.0 stays the production jar (4 boards: 3 FAIL, 0 BETTER, 1 REGRESSED; the gate needs 0 FAIL, 0 REGRESSED and BETTER on at least 3).
