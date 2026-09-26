#!/usr/bin/env python3
"""ZEROIZE slot map for the ATECC608B-SSHDA-T on board B (U8): build the 128-byte configuration-zone image the
bench experiment Z-EXP-A provisions, and prove from the image itself that it has the properties ZEROIZE needs.

DRAFT for v2/docs/feasibility/ZEROIZE.md (MESHSAT-1357, review of 26 September 2026 section 3). Prototype design,
nothing built, no part provisioned. Run: python3 zer_config.py   (prints the image and exits 0 when every check holds)

Provenance of every number, so that nothing here is a convenient value:
  BASE      CryptoAuthLib v3.8.0 (github.com/MicrochipTech/cryptoauthlib, commit d49c7d578efb09d4a498d5ab86839d4c17812f15),
            test/api_calib/test_calib_config.c:35-44, `test_ecc608_configdata`: the ATECC608 image Microchip's own test
            suite runs against. Every byte this draft does not deliberately change stays at that value, so every
            ATECC608-only byte whose meaning is published only in the NDA data sheet (CountMatch, UseLock,
            VolatileKeyPermission, SecureBoot, KdfIvLoc/Str, ChipOptions) keeps a value a Microchip test exercises.
  LAYOUT    byte offsets: CryptoAuthLib lib/calib/calib_device.h:104-134 (`atecc608_config_t`); SlotConfig bytes 20-51
            and KeyConfig bytes 96-127: ATECC508A Complete Data Sheet DS20005927A Table 2-5, pp. 13-15.
  SLOTCFG   bit meanings: DS20005927A Table 2-6 p. 16-17 (WriteConfig 15-12, WriteKey 11-8, IsSecret 7, EncryptRead 6,
            LimitedUse 5, NoMac 4, ReadKey 3-0; for a private key ReadKey bit 3 = ECDH output to slot N+1, bit 2 = ECDH
            allowed, bit 1 = internal sign, bit 0 = external sign).
  WRITECFG  DS20005927A Tables 2-8 (Write), 2-10 (GenKey), 2-11 (PrivWrite), pp. 18-19: bit 13 set = GenKey may write a
            random key into the slot after the data zone is locked; bit 14 clear = PrivWrite forbidden; code 001x =
            Write never.
  KEYCFG    DS20005927A Table 2-12 pp. 20-21 (Private 0, PubInfo 1, KeyType 4-2 = 100 for P256, Lockable 5, ReqRandom 6,
            ReqAuth 7, AuthKey 11-8, bit 12, X509id 15-14).
  LOCKING   DS20005927A section 2.4.3 and Table 2-15 p. 25: SlotLocked bit 1 and Lockable 0 = writeable but never lockable.
  608 == 508A for these fields: ATECC608B Summary DS40002239A section 3.1 p. 12 ('No configuration bit fields have
            changed' from the ATECC608A) and section 3.2 pp. 12-13 (compatible with the ATECC508A except the listed
            functions, none of which is GenKey, ECDH, SlotConfig or KeyConfig).
"""
import sys

# ---- BASE: CryptoAuthLib v3.8.0 test/api_calib/test_calib_config.c:35-44, verbatim ----------------------------------
BASE = bytes([
    0x01, 0x23, 0x00, 0x00, 0x00, 0x00, 0x60, 0x00, 0x04, 0x05, 0x06, 0x07, 0xEE, 0x01, 0x01, 0x00,
    0xC0, 0x00, 0xA1, 0x00, 0xAF, 0x2F, 0xC4, 0x44, 0x87, 0x20, 0xC4, 0xF4, 0x8F, 0x0F, 0x0F, 0x0F,
    0x9F, 0x8F, 0x83, 0x64, 0xC4, 0x44, 0xC4, 0x64, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
    0x0F, 0x0F, 0x0F, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF,
    0x00, 0x00, 0x00, 0x00, 0xFF, 0x84, 0x03, 0xBC, 0x09, 0x69, 0x76, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x0E, 0x40, 0x00, 0x00, 0x00, 0x00,
    0x33, 0x00, 0x1C, 0x00, 0x13, 0x00, 0x1C, 0x00, 0x3C, 0x00, 0x3A, 0x10, 0x1C, 0x00, 0x33, 0x00,
    0x1C, 0x00, 0x1C, 0x00, 0x38, 0x00, 0x30, 0x00, 0x3C, 0x00, 0x3C, 0x00, 0x32, 0x00, 0x30, 0x00,
])

SLOTCONFIG_AT, KEYCONFIG_AT, SLOTLOCKED_AT = 20, 96, 88     # DS20005927A Table 2-5; calib_device.h:104-134
I2C_ADDRESS_AT = 16                                          # DS20005927A Table 2-5 p. 13: default 0xC0 (7-bit 0x60)

# ---- the two key-encryption keys (KEK_A, KEK_B) -----------------------------------------------------------------------
# One P-256 private key per slot, created inside the device by GenKey, usable only for ECDH with the output in the
# clear, never readable, never written by Write or PrivWrite, re-creatable by GenKey after the data zone is locked,
# and never lockable. This is CryptoAuthLib's test slot 2 (SlotConfig 0x2087, KeyConfig 0x0013), the slot its ECDH
# test regenerates with GenKey on a data-locked device (test/api_atcab/atca_tests_ecdh.c:62 and :87-119), with the
# two signing permissions removed (ReadKey 0111 -> 0100), which only narrows what the key can do.
KEK_SLOTS = (0, 1)
KEK_SLOTCONFIG = (0b0010 << 12) | (0 << 8) | (1 << 7) | (0 << 6) | (0 << 5) | (0 << 4) | 0b0100    # = 0x2084
KEK_KEYCONFIG = (0 << 14) | (0 << 12) | (0 << 8) | (0 << 7) | (0 << 6) | (0 << 5) | (0b100 << 2) | (1 << 1) | 1  # = 0x0013


def u16(img, at):
    return img[at] | (img[at + 1] << 8)


def put16(img, at, v):
    img[at] = v & 0xFF
    img[at + 1] = (v >> 8) & 0xFF


def build():
    img = bytearray(BASE)
    for s in KEK_SLOTS:
        put16(img, SLOTCONFIG_AT + 2 * s, KEK_SLOTCONFIG)
        put16(img, KEYCONFIG_AT + 2 * s, KEK_KEYCONFIG)
    return bytes(img)


def decode_slot(img, s):
    sc, kc = u16(img, SLOTCONFIG_AT + 2 * s), u16(img, KEYCONFIG_AT + 2 * s)
    return dict(sc=sc, kc=kc, write_config=sc >> 12, write_key=(sc >> 8) & 0xF, is_secret=(sc >> 7) & 1,
                encrypt_read=(sc >> 6) & 1, limited_use=(sc >> 5) & 1, no_mac=(sc >> 4) & 1, read_key=sc & 0xF,
                private=kc & 1, pub_info=(kc >> 1) & 1, key_type=(kc >> 2) & 7, lockable=(kc >> 5) & 1,
                req_random=(kc >> 6) & 1, req_auth=(kc >> 7) & 1, auth_key=(kc >> 8) & 0xF, bit12=(kc >> 12) & 1,
                x509=(kc >> 14) & 3, slot_locked_bit=(u16(img, SLOTLOCKED_AT) >> s) & 1)


def check(img):
    """Every property ZEROIZE relies on, read back from the image with the data sheet's own bit tables.
    Returns a list of failures (empty = all hold)."""
    bad = []
    def need(cond, what):
        if not cond:
            bad.append(what)
    need(len(img) == 128, "the configuration zone is 128 bytes (DS20005927A section 2.2)")
    need(img[I2C_ADDRESS_AT] == 0xC0, "I2C_Address stays 0xC0, 7-bit 0x60, the address PANEL.md section 7 reserves")
    for s in KEK_SLOTS:
        d = decode_slot(img, s)
        tag = "slot %d" % s
        need(d["private"] == 1 and d["key_type"] == 0b100, tag + ": holds a P256 private key (Table 2-12)")
        need(d["is_secret"] == 1, tag + ": IsSecret set, required for GenKey (p. 70) and for secrecy (Table 2-7)")
        need(d["encrypt_read"] == 0, tag + ": EncryptRead clear (private keys are never readable, p. 29)")
        need((d["write_config"] >> 1) & 1 == 1, tag + ": SlotConfig bit 13 set, GenKey may replace the key after "
             "the data zone is locked (Table 2-10 p. 19; GenKey restrictions p. 70)")
        need((d["write_config"] >> 2) & 1 == 0, tag + ": SlotConfig bit 14 clear, PrivWrite forbidden (Table 2-11)")
        need(d["write_config"] & 0b1110 == 0b0010, tag + ": WriteConfig 001x, Write never (Table 2-8)")
        need(d["lockable"] == 0, tag + ": Lockable clear, so no Lock(slot) can make the key permanent (Table 2-15)")
        need(d["slot_locked_bit"] == 1, tag + ": SlotLocked bit 1 at configuration lock (a 0 would forbid GenKey, p. 70)")
        need(d["req_auth"] == 0 and d["auth_key"] == 0, tag + ": ReqAuth clear, destruction needs no secret "
             "(GenKey after lock needs AuthKey authorisation when ReqAuth is set, p. 70)")
        need(d["limited_use"] == 0, tag + ": LimitedUse clear, no counter can exhaust the key's use (section 3.2.5)")
        need(d["pub_info"] == 1, tag + ": PubInfo set, the public key can always be recomputed, which is how a "
             "destruction is verified (Table 2-12; GenKey public mode p. 71)")
        need(d["read_key"] & 0b0100 != 0, tag + ": ReadKey bit 2 set, ECDH allowed (Table 2-6)")
        need(d["read_key"] & 0b1000 == 0, tag + ": ReadKey bit 3 clear, ECDH output returned, never copied to slot N+1")
        need(d["read_key"] & 0b0011 == 0, tag + ": ReadKey bits 1-0 clear, the key signs nothing")
        need(d["bit12"] == 0, tag + ": KeyConfig bit 12 clear, the key does not depend on a volatile latch")
    # No other slot may name a KEK slot as the key that encrypts its writes, reads, derivations or authorisations.
    for s in range(16):
        if s in KEK_SLOTS:
            continue
        d = decode_slot(img, s)
        tag = "slot %d" % s
        uses_write_key = (d["write_config"] >> 2) & 1 or ((d["write_config"] >> 1) & 1 and not d["private"])
        if uses_write_key:
            need(d["write_key"] not in KEK_SLOTS, tag + ": its WriteKey is not a KEK slot")
        if d["encrypt_read"] and not d["private"]:
            need(d["read_key"] not in KEK_SLOTS, tag + ": its ReadKey is not a KEK slot")
        if d["req_auth"]:
            need(d["auth_key"] not in KEK_SLOTS, tag + ": its AuthKey is not a KEK slot")
    # Everything outside the two KEK slots' SlotConfig and KeyConfig words is Microchip's tested image, byte for byte.
    changed = {i for i in range(128) if img[i] != BASE[i]}
    allowed = set()
    for s in KEK_SLOTS:
        allowed |= {SLOTCONFIG_AT + 2 * s, SLOTCONFIG_AT + 2 * s + 1, KEYCONFIG_AT + 2 * s, KEYCONFIG_AT + 2 * s + 1}
    need(changed <= allowed, "only the KEK slots' SlotConfig and KeyConfig words differ from the base image "
         "(differences at %s)" % sorted(changed - allowed))
    return bad


def self_test():
    """The checker must fail on the defects it exists to catch (a planted defect per property)."""
    good = build()
    assert check(good) == [], check(good)
    plants = {
        "Lockable set": lambda im: put16(im, KEYCONFIG_AT, u16(im, KEYCONFIG_AT) | (1 << 5)),
        "GenKey bit 13 clear": lambda im: put16(im, SLOTCONFIG_AT, u16(im, SLOTCONFIG_AT) & ~(1 << 13)),
        "PrivWrite allowed": lambda im: put16(im, SLOTCONFIG_AT, u16(im, SLOTCONFIG_AT) | (1 << 14)),
        "ECDH to slot N+1": lambda im: put16(im, SLOTCONFIG_AT, u16(im, SLOTCONFIG_AT) | (1 << 3)),
        "slot 0 locked": lambda im: put16(im, SLOTLOCKED_AT, u16(im, SLOTLOCKED_AT) & ~1),
        "ReqAuth set": lambda im: put16(im, KEYCONFIG_AT + 2, u16(im, KEYCONFIG_AT + 2) | (1 << 7)),
        "IsSecret clear": lambda im: put16(im, SLOTCONFIG_AT + 2, u16(im, SLOTCONFIG_AT + 2) & ~(1 << 7)),
        "slot 9 encrypts writes with KEK_A": lambda im: put16(im, SLOTCONFIG_AT + 18, (u16(im, SLOTCONFIG_AT + 18) & ~0x0F00) | 0x4000),
        "I2C address moved": lambda im: im.__setitem__(I2C_ADDRESS_AT, 0xC2),
    }
    for name, plant in plants.items():
        im = bytearray(good)
        plant(im)
        assert check(bytes(im)), "planted defect not caught: " + name
    return len(plants)


def main():
    n = self_test()
    img = build()
    for s in KEK_SLOTS:
        d = decode_slot(img, s)
        print("slot %d  SlotConfig 0x%04X  KeyConfig 0x%04X  SlotLocked bit %d" % (s, d["sc"], d["kc"], d["slot_locked_bit"]))
    print("bytes 16..127 for atcab_write_config_zone before the configuration lock (CryptoAuthLib calib_write.c:351-392 "
          "writes 16..127 and sets 84/85 through UpdateExtra; bytes 0..15 are factory, 86/87 change only by Lock):")
    for row in range(16, 128, 16):
        print("  %3d: %s" % (row, " ".join("%02X" % b for b in img[row:row + 16])))
    fails = check(img)
    for f in fails:
        print("FAIL", f)
    print("%s: %d planted defects caught, %d checks failed" % ("PASS" if not fails else "FAIL", n, len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
