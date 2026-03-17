# Refactoring Lesson: Project Euler Problem 8
### From Iteration Collapse to Architectural Thinking

---

## The Problem

> Find the thirteen adjacent digits in the 1000-digit number that have the greatest product. What is the value of this product?

This is a straightforward problem on the surface. But the way you solve it reveals a lot about how deeply you understand your tools, your language, and your algorithms.

---

## The Naive Approach

The obvious solution uses nested loops: an outer loop sliding a window through the 1000 digits, an inner loop multiplying 13 digits together for each window position. In pseudocode:

```
for each starting position (0 to 987):
    product = 1
    for each of 13 digits starting at that position:
        product = product * digit
    if product > best:
        best = product
```

This is correct. In Python, Go, or most compiled/interpreted languages, it runs fast enough that you'll never notice. The total iteration count is roughly 988 × 13 = **12,844 iterations**. That's nothing.

### Why This Fails in Steps

Steps is a teaching interpreter built in Python. It has a deliberate iteration ceiling to prevent runaway programs from hanging the classroom environment. When a naive implementation uses poorly structured nested loops — especially with incorrect loop logic that compounds iterations — that ceiling becomes a wall.

The original Steps code hit the **10,000,000 iteration limit** without producing an answer.

This is not a flaw in Steps. It is the lesson.

---

## What Went Wrong: Diagnosing the Problem

The original code had three nested loops: one to convert characters, one sliding the window, and one multiplying digits. The logic connecting them was broken in two ways:

**Problem 1: Loop structure multiplied iterations instead of sequencing them.**
Nested loops that should have been sequential were stacked, causing the iteration count to multiply rather than add.

**Problem 2: The index variable `j` was never updated inside the inner loop.**
This meant the same digit was being multiplied 13 times rather than walking forward through 13 consecutive digits. The algorithm was computing the wrong thing at enormous cost.

The fix to the index logic alone would have reduced iterations dramatically. But the deeper lesson here is: *before you optimize speed, make sure the algorithm is correct.*

---

## Refactoring Step 1: Fix the Structure

Once the loop logic is corrected, the core algorithm becomes a single outer loop with one inner loop:

```
set cnt to 0
repeat while cnt is less than 988
    set tmp to 1
    set i to 0
    repeat while i is less than 13
        set j to cnt + i
        set tmp to tmp * data_list[j]
        set i to i + 1
    if tmp is greater than tot
        set tot to tmp
    set cnt to cnt + 1
```

This is correct and runs in approximately 12,844 Steps iterations. Better — but we can do much more.

---

## Refactoring Step 2: Exploit the Zero

Here is a key observation about this specific problem: **any window containing a zero has a product of zero, and zero can never be the maximum product.**

This means:
- We never need to compute the product of any window that contains a zero.
- More importantly, if a zero is at position 7 within a window, then *every window that includes that position* is also poisoned. We can skip all of them at once by jumping our window start to the position *after* the zero.

This transforms the algorithm from "check every window" to "skip entire regions of the number." In a 1000-digit string with zeros scattered through it, this eliminates a large fraction of the work.

---

## Refactoring Step 3: Push Work to the Runtime

The zero-check insight raises a question: how do we find the zero in a window? We could write a Steps loop to scan 13 digits. But that just adds another nested loop — exactly what we are trying to eliminate.

A better approach is to ask: *does our language or runtime already have a built-in that does this?*

Steps has `index_of` for text, and `slice` for extracting substrings. Both are implemented in the Python runtime, not in the Steps interpreter. They run at Python speed, not Steps interpreter speed.

This insight drives the final architecture:

1. Keep the number as **text** for as long as possible.
2. Use `slice` (Python-speed) to extract each 13-character window.
3. Use `index_of` (Python-speed) to check for the character `"0"`.
4. Only if no zero is found: convert to numbers and compute the product (Steps loop).
5. If a zero is found: jump the window index past it (no Steps loop at all).

---

## The Final Algorithm

```
set cnt to 0

repeat while cnt is less than 988
    call slice with data_text, cnt, cnt+13 storing result in window
    call index_of with window, "0" storing result in zero_pos

    if zero_pos is equal to -1
        set tmp to 1
        set i to 0
        call characters with window storing result in digit_list
        repeat while i is less than 13
            set tmp to tmp * digit_list[i] as number
            set i to i + 1
        if tmp is greater than tot
            set tot to tmp
        set cnt to cnt + 1
    else
        set cnt to cnt + zero_pos + 1
```

---

## What Changed and Why It Matters

| | Naive (broken) | Naive (fixed) | Optimized |
|---|---|---|---|
| Outer loop iterations | Millions+ | ~988 | ~988 (with large skips) |
| Inner loop iterations | Millions+ | ~12,844 | Small fraction of 12,844 |
| Zero check | None | None | Python-speed via `index_of` |
| Result | Hits iteration limit | Correct, slow | Correct, fast |
| Time | Did not complete | Acceptable | **0.123 seconds** |

The outer loop count does not change much — it still slides from 0 to 987. What changes is how often the inner loop runs. Most windows either contain a zero (skipped entirely) or are jumped over because a previous zero made them redundant. The multiplication loop runs only on clean, zero-free windows.

---

## The Deeper Lesson

This problem illustrates three levels of optimization that every programmer should internalize:

**Level 1 — Correctness first.**
A fast algorithm that computes the wrong answer is worthless. Before asking "how do I make this faster," ask "is this actually doing what I think it is?"

**Level 2 — Algorithm before language.**
The naive algorithm in a "fast" language will often beat a bad algorithm in any language. The choice of algorithm matters more than the choice of language for most problems.

**Level 3 — Know your runtime.**
Every language sits on top of a runtime with its own built-in capabilities. Understanding which operations are handled natively — and pushing work to that layer whenever possible — is what separates competent programmers from expert ones. In this case, `slice` and `index_of` are the bridge between the Steps interpreter and Python's native speed.

---

## The Constraint as Teacher

Steps has an iteration limit. In most languages, a broken algorithm just runs slowly. In Steps, it fails visibly and forces a conversation.

That is not a limitation. That is the design.

When a student's program hits the ceiling, the question becomes: *why does this need so many iterations?* That question leads directly to algorithm analysis, to thinking about zeros as poison values, to understanding what the runtime can do for you. The constraint makes the thinking visible.

A student who has wrestled with Steps and won understands something about computation that a student who brute-forced it in Python may never have had reason to think about.

---

---

## Taking It Further: From Solution to Reusable Helper

The fully optimized solution above is excellent for Problem 8. But a hallmark of mature programming thinking is asking: *could this be useful again?*

Problem 8 gives us a fixed 1000-digit number and a fixed window size of 13. Those are constants baked into our solution. But the algorithm itself — slide a window through a digit string, skip zeros, find the maximum product — is completely general. It works for any digit string of any length and any window size.

### A Tempting Optimization That Isn't One

Before moving to generalization, there is a refactoring instinct worth examining — and worth examining critically.

Looking at the outer loop, a programmer might ask: *could we reduce iterations further by replacing the `cnt < 988` condition with a flag variable that we trip when we want to stop?* Like this:

```
set searching to true
repeat while searching equals true
    ...
    if cnt is greater than 987
        set searching to false
```

This feels like an optimization. It looks more flexible. But pause and think about what the machine actually does: it checks a condition at the top of every loop cycle either way. Whether that condition is `cnt < 988` or `searching is true`, it is still one check per iteration. The loop body executes exactly the same number of times. Nothing has been saved.

This is an important lesson in itself: **not every structural change is an algorithmic change.** A refactoring that changes how termination is *expressed* without changing how many times work is *performed* is cosmetic. It may improve readability or flexibility, but it should not be confused with a performance improvement.

The instinct to ask the question was right. The discipline is in being honest about the answer.

### Why Generalization Changes Everything

Here is where the flag approach earns its place. When the function accepts an arbitrary digit string and an arbitrary window size, you can no longer hardcode `988`. The termination condition must be computed from the inputs:

```
set limit to (length of data_text - window_size)
```

This value is different every time the function is called. Now the flag is doing real work — it carries a dynamically computed boundary rather than a constant. And the zero-skip optimization becomes even more valuable, because with an arbitrary input you have no prior knowledge of where the zeros fall. Every call is a new distribution of zeros and the algorithm adapts automatically.

### The Generic Helper

```
step: max_adjacent_product

    belongs to: helpers
    expects: digit_string as text, window_size as number
    returns: best as number
    
    declare:
        cnt as number
        limit as number
        best as number
        tmp as number
        window as text
        zero_pos as number
        digit_list as list
        i as number
        searching as boolean
    
    do:
        set best to 0
        set cnt to 0
        set limit to (length of digit_string - window_size)
        set searching to true
    
        repeat while searching
            call slice with digit_string, cnt, cnt + window_size storing result in window
            call index_of with window, "0" storing result in zero_pos
    
            if zero_pos is equal to -1
                set tmp to 1
                set i to 0
                call characters with window storing result in digit_list
                repeat while i is less than window_size
                    set tmp to tmp * digit_list[i] as number
                    set i to i + 1
                if tmp is greater than best
                    set best to tmp
                set cnt to cnt + 1
            else
                set cnt to cnt + zero_pos + 1
    
            if cnt is greater than limit
                set searching to false
    
        return best
```

Problem 8 now becomes a single call:

```
call max_adjacent_product with data_text, 13 storing result in answer
```

### What Reusability Taught Us

Notice that thinking about reusability completed the flag argument in a way pure optimization didn't. The flag loop wasn't meaningfully better for the specific solution — but it's the *right* structure for the general one. Designing for reuse led us to the cleaner, more correct expression of the algorithm.

This is a pattern worth internalizing: **specific solutions optimize for the known case; reusable helpers must be correct for all cases.** The discipline of writing helpers forces you to stop hardcoding assumptions and start reasoning about the algorithm itself. Often, as here, the general solution turns out to be just as fast as the specific one — and infinitely more useful.

A student who writes `max_adjacent_product` as a helper has not just solved Problem 8. They have built a tool.

---

*Part of the Steps Refactoring Curriculum — Fragillidae Software Educational Tools*
