# Block Edit Demo with Python Function Swap

This demonstrates using `blockedit.sh` to swap a function in a Python module.

## Initial State (large_module.py)

```python
"""A large Python module with multiple functions."""

def func1():
    """This is func1."""
    print("func1 called")

def func2(a, b):
    """This is func2."""
    return a + b

def target_function(x):
    """This is the target function to be replaced."""
    print(f"Target function called with {x}")

def func4():
    """This is func4."""
    print("func4 called")

def func5(y):
    """This is func5."""
    return y * 2
```

## New Function Implementation

```python
def target_function(x):
    """This is the new implementation of the target function."""
    print(f"New target function called with {x}, returning its square")
    return x * x
```

## Block Edit Steps

1. **Scan:** Identify the lines of the `target_function` using `scan`:

   ```bash
   source src/blockedit.sh
   scan large_module.py "def target_function\(x\):"
   ```

2. **Edit:** Replace the old `target_function` with the new implementation using `edit`:

   ```bash
   # Assuming target_function starts at line 9 and ends at line 11 (inclusive)
   edit large_module.py "def target_function(x):\n    \"\"\"This is the new implementation of the target function.\"\"\"\n    print(f\"New target function called with {x}, returning its square\")\n    return x * x" 9 12
   ```

3. **Verify:** Confirm the changes using `verify`:

   ```bash
   verify large_module.py large_module.py.bak 9 12
   ```

## Final State (large_module.py)

```python
"""A large Python module with multiple functions."""

def func1():
    """This is func1."""
    print("func1 called")

def func2(a, b):
    """This is func2."""
    return a + b

def target_function(x):
    """This is the new implementation of the target function."""
    print(f"New target function called with {x}, returning its square")
    return x * x

def func4():
    """This is func4."""
    print("func4 called")

def func5(y):
    """This is func5."""
    return y * 2
