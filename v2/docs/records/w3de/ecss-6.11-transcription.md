# DRAFT addition to v2/vendor/standards/ecss-q-st-30-11c-rev2-2021-06-23.md (w3de, 27 September 2026)

For the owner of the transcription: the connector clause EQ-16's record cites (`drafts/w3de/EQ16-dock-vin-raw.md`
section 2, `drafts/w3de/dock_contacts.py`), read from the same file the transcription already names (fetched again on
27 September 2026 from the URL in its header; sha256 `10cf7066fad0314918c6a7d38517bbcf7cb00e206480fc10377e9fdb83e7db6e`,
988,694 bytes, identical to the one it records). Append after the fuse section:

---

## 6.11 Connectors, family-group codes 02-01, 02-02, 02-03, 02-07 and 02-09 (printed pages 38 and 39)

> 6.11.2 a. Parameters of connectors from family-group code 02-01, 02-02, 02-03, 02-07 and 02-09 shall be derated as
> per Table 6-10.

**Table 6-10, Derating of parameters for connectors family-group code 02-01, 02-02, 02-03, 02-07 and 02-09**:

| parameter | load ratio or limit |
|---|---|
| Working voltage | 25 % of the connector Dielectric Withstanding test Voltage (at sea level, unconditioned), or 75 % of the connector rated operating (working) voltage (at sea level), whichever is lower |
| Current | **50 %** |
| Maximum operating temperature | **30 C below maximum rated temperature** |

> 6.11.3 a. For power connectors, power and return lines shall be separated by at least one unassigned contact to
> reduce the short-circuit risk.

## What this project may and may not conclude from it (connectors)

**May.** Use Table 6-10 as a SCREEN, as the fuse row is used: a contact carrying under half its maker's rating with its
temperature 30 C under its maker's maximum is inside a criterion a space standard sets. The dock's spring contacts are
PCB connectors (02-03) in the standard's own coding.

**May not, without saying so.** Claim that the standard sets a terrestrial field kit's limit, or that a contact past the
screen is non-compliant with anything. EQ-16's record reports the 813 and the Mill-Max power pins against the screen and
decides on the makers' own figures.
