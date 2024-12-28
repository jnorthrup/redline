# Block Edit Demo

This demonstrates a workflow for making targeted edits to source files.

#bash api 
   scan <filepat> \"<regex>\"" | tee -a output.log
   edit <input_file> \"<text>\" <start> <end>" | tee -a output.log
   verify <file_a> <file_b> <start> <end>" | tee -a output.log
   read <file> <gcat_switches> <start> <end>" | tee -a output.log
   -A equivalent to -vET" | tee -a output.log
   -b number nonempty output lines, overrides -n" | tee -a output.log
   -e equivalent to -vE" | tee -a output.log
   -E display $ at end of each line" | tee -a output.log
   -n number all output lines" | tee -a output.log
   -s suppress repeated empty output lines" | tee -a output.log
   -t equivalent to -vT" | tee -a output.log
   -T display TAB characters as ^I" | tee -a output.log
   -v use ^ and M- notation, except for LFD and TAB" | tee -a output.log
   
## Initial State (block-before.c)
```c
#include <stdio.h>

int main() {
    return 0;
}
```

## Search Operation
Search for pattern '\s?int\s+' shows grep -nC2E  functionality:
```c
1-#include <stdio.h>
2-
3:int main() {
4-    return 0;
5-}
```

## Edit Operation
Add printf statement between main() opening brace and return:

edit block-before.c '    printf("Hello, World!\n");'   3 4
 

## Final State
```c
#include <stdio.h>

int main() {
    printf("Hello, World!\n");
    return 0;
}
```

verify 
 
