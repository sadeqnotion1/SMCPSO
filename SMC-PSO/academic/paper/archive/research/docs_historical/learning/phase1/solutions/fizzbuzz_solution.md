<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/phase1/solutions/fizzbuzz_solution.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# FizzBuzz Solution - Classic Programming Exercise

## Problem Statement

Write a program that prints the numbers from 1 to 100, but:
- For multiples of 3, print "Fizz" instead of the number
- For multiples of 5, print "Buzz" instead of the number
- For multiples of both 3 and 5, print "FizzBuzz"

**Example Output**:
```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
16
...
```

------

## Solution Approach

The key insight is to check divisibility in the correct order:
1. Check if divisible by both 3 AND 5 first (otherwise you'll print Fizz or Buzz instead of FizzBuzz)
2. Then check divisibility by 3
3. Then check divisibility by 5
4. Otherwise, print the number

------

## Step-by-Step Solution

### Version 1: Basic Solution

```python
for i in range(1, 101):
    if i % 15 == 0:  # Divisible by both 3 and 5
        print("FizzBuzz")
    elif i % 3 == 0:  # Divisible by 3
        print("Fizz")
    elif i % 5 == 0:  # Divisible by 5
        print("Buzz")
    else:
        print(i)
```

**Explanation**:
- `i % 15 == 0` checks for multiples of both 3 and 5 (since 3 × 5 = 15)
- Order matters! If we checked `i % 3 == 0` first, we'd print "Fizz" for 15 instead of "FizzBuzz"
- `range(1, 101)` generates numbers 1 through 100 (101 is excluded)

### Version 2: String Building (More Flexible)

```python
for i in range(1, 101):
    output = ""

    if i % 3 == 0:
        output += "Fizz"

    if i % 5 == 0:
        output += "Buzz"

    if output == "":
        output = str(i)

    print(output)
```

**Explanation**:
- Start with empty string
- Add "Fizz" if divisible by 3
- Add "Buzz" if divisible by 5 (this naturally handles multiples of both)
- If string is still empty, use the number itself

**Advantages**:
- Easier to extend (e.g., add "Bazz" for multiples of 7)
- More maintainable for complex rules

### Version 3: Function-Based (Reusable)

```python
def fizzbuzz(n):
    """
    Return FizzBuzz string for number n.

    Args:
        n: Integer to check

    Returns:
        "Fizz", "Buzz", "FizzBuzz", or string representation of n
    """
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return str(n)


def main():
    """Run FizzBuzz for 1 to 100."""
    for i in range(1, 101):
        print(fizzbuzz(i))


if __name__ == "__main__":
    main()
```

**Explanation**:
- Encapsulates logic in a function for reusability
- Easier to test individual numbers
- Follows professional coding standards

------

## Common Mistakes

### Mistake 1: Wrong Order

```python
# WRONG - 15 will print "Fizz" instead of "FizzBuzz"
for i in range(1, 101):
    if i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    elif i % 15 == 0:
        print("FizzBuzz")  # Never reached!
    else:
        print(i)
```

**Why wrong**: `elif` means "else if", so once `i % 3 == 0` is true (which it is for 15), the other conditions aren't checked.

### Mistake 2: Off-by-One Error

```python
# WRONG - only goes to 99
for i in range(1, 100):
    # ...
```

**Why wrong**: `range(1, 100)` generates 1 through 99. Need `range(1, 101)` for 1 through 100.

### Mistake 3: Forgetting String Conversion

```python
# WRONG - can't concatenate int to string
output = ""
if i % 3 == 0:
    output += "Fizz"
if output == "":
    output = i  # Should be str(i)
```

------

## Alternative Approaches

### Approach 1: List Comprehension

```python
def fizzbuzz(n):
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return str(n)

results = [fizzbuzz(i) for i in range(1, 101)]
print("\n".join(results))
```

### Approach 2: Conditional Expression (One-Liner)

```python
for i in range(1, 101):
    print("FizzBuzz" if i % 15 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else i)
```

**Note**: This works but is less readable. Clarity > brevity!

------

## Extension Challenges

### Challenge 1: FizzBuzzBazz

Add another rule: Print "Bazz" for multiples of 7, and combine appropriately (e.g., "FizzBazz" for 21).

**Hint**: Use the string-building approach (Version 2).

<details>
<summary>Click to reveal solution</summary>

```python
for i in range(1, 101):
    output = ""

    if i % 3 == 0:
        output += "Fizz"

    if i % 5 == 0:
        output += "Buzz"

    if i % 7 == 0:
        output += "Bazz"

    if output == "":
        output = str(i)

    print(output)
```

</details>

### Challenge 2: Custom Rules

Write a function that takes a list of (divisor, word) pairs and generates FizzBuzz-style output.

```python
def general_fizzbuzz(n, rules):
    """
    Generalized FizzBuzz.

    Args:
        n: Upper limit
        rules: List of (divisor, word) tuples

    Example:
        general_fizzbuzz(20, [(3, "Fizz"), (5, "Buzz"), (7, "Bazz")])
    """
    # Your implementation here
```

<details>
<summary>Click to reveal solution</summary>

```python
def general_fizzbuzz(n, rules):
    for i in range(1, n + 1):
        output = ""

        for divisor, word in rules:
            if i % divisor == 0:
                output += word

        if output == "":
            output = str(i)

        print(output)


# Test
general_fizzbuzz(20, [(3, "Fizz"), (5, "Buzz"), (7, "Bazz")])
```

</details>

### Challenge 3: Unit Tests

Write pytest tests for your FizzBuzz function.

<details>
<summary>Click to reveal solution</summary>

```python
def fizzbuzz(n):
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return str(n)


def test_fizzbuzz_multiples_of_3():
    assert fizzbuzz(3) == "Fizz"
    assert fizzbuzz(6) == "Fizz"
    assert fizzbuzz(9) == "Fizz"


def test_fizzbuzz_multiples_of_5():
    assert fizzbuzz(5) == "Buzz"
    assert fizzbuzz(10) == "Buzz"
    assert fizzbuzz(20) == "Buzz"


def test_fizzbuzz_multiples_of_both():
    assert fizzbuzz(15) == "FizzBuzz"
    assert fizzbuzz(30) == "FizzBuzz"
    assert fizzbuzz(45) == "FizzBuzz"


def test_fizzbuzz_normal_numbers():
    assert fizzbuzz(1) == "1"
    assert fizzbuzz(2) == "2"
    assert fizzbuzz(4) == "4"
    assert fizzbuzz(7) == "7"
```

Run with: `pytest test_fizzbuzz.py`

</details>

------

## Key Takeaways

1. **Order matters** in if-elif-else chains
2. **Modulo operator** (`%`) is essential for divisibility checks
3. **String building** is more flexible than nested conditions
4. **Functions** make code reusable and testable
5. **Edge cases** matter (e.g., range boundaries)

------

**Difficulty**: Beginner
**Topics**: Control flow, modulo operator, functions
**Estimated Time**: 15-30 minutes
