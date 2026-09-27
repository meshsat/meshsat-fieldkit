"""r8int5: append stream w3de's transcription of ECSS-Q-ST-30-11C Rev.2 clause 6.11 (Table 6-10) to the standards
transcription, as its draft asks ('Append after the fuse section'), from its '---' line on. Run from the root."""
import os
K = os.path.dirname(os.path.abspath(__file__))
P = 'v2/vendor/standards/ecss-q-st-30-11c-rev2-2021-06-23.md'
d = open(os.path.join(K, 'ecss-6.11-transcription.md')).read()
add = d[d.index('\n---\n') + 1:]
t = open(P).read()
if '## 6.11 Connectors, family-group codes' not in t:
    t = t.rstrip('\n') + '\n\n' + add.replace('---\n', '---\n\nAdded 27 September 2026 by board D and E stream w3de (integrated in `fnd/r8int5`) from the same PDF, fetched again from the URL in this file\'s header (sha256 `10cf7066fad0314918c6a7d38517bbcf7cb00e206480fc10377e9fdb83e7db6e`, 988,694 bytes, identical to the one recorded here); the record that cites it is `v2/docs/records/w3de/EQ16-dock-vin-raw.md`.\n', 1)
    open(P, 'w').write(t.rstrip('\n') + '\n')
print('ecss_append_r8int5: done')
