/* test_main.c: runs every test of test_list.h and prints one line per test with its citation. Host only. */
#include <stdio.h>

#include "fixture.h"
#include "test_list.h"

#define DECL(fn, cite) void fn(void);
TEST_LIST(DECL)
#undef DECL

typedef struct { void (*fn)(void); const char *name, *cite; } test_t;
#define ROW(fn, cite) { fn, #fn, cite },
static const test_t TESTS[] = { TEST_LIST(ROW) };
#undef ROW

int main(void)
{
    unsigned n = sizeof TESTS / sizeof TESTS[0], failed = 0;
    for (unsigned i = 0; i < n; i++) {
        test_failed = 0;
        TESTS[i].fn();
        printf("%s %s  [%s]\n", test_failed ? "FAIL" : "ok  ", TESTS[i].name, TESTS[i].cite);
        failed += (unsigned)test_failed;
    }
    printf("%u tests, %u passed, %u failed\n", n, n - failed, failed);
    return failed ? 1 : 0;
}
