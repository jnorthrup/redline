#include <stdio.h>
#include <stdlib.h>
#include "../blockedit.c"

// Test function to verify blockedit functionality
void test_blockedit() {
    // Example test case
    char *input = "Hello, World!";
    char *output = blockedit(input);
    printf("Input: %s\n", input);
    printf("Output: %s\n", output);
    free(output);
}

int main() {
    test_blockedit();
    return 0;
}
