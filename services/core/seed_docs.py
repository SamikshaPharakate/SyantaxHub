"""
Official Documentation Dataset for Java, React, JavaScript, and Python
Ready for Chunking and ChromaDB Vector Storage in SyntaxHub
"""

OFFICIAL_DOCS = [
    {
        "title": "React 19 Official Documentation & Upgrade Guide",
        "technology": "React",
        "version": "19",
        "content": """
# React 19 Upgrade Guide & Best Practices

## Server Components and Actions
In React 19, Server Components are enabled by default in supporting frameworks. Data fetching should be performed directly on the server or using Server Components instead of `useEffect` client-side hooks to eliminate waterfalls and race conditions.

```jsx
// Recommended React 19 Server Component
export async function UserProfile({ userId }) {
  const user = await fetchUser(userId);
  return <ProfileCard user={user} />;
}
```

## Anti-Pattern: useEffect Data Fetching
Fetching data in `useEffect` is an outdated pattern in React 19:
```jsx
// OUTDATED PATTERN in React 19
useEffect(() => {
  fetchUser(userId).then(setUser);
}, [userId]);
```
*Why this matters*: Data fetching in `useEffect` creates network waterfalls, client-side flicker, and unhandled race conditions.

## The `use` Hook for Async Resources
React 19 introduces the `use()` API to read resources like Promises or Context in render.
```jsx
import { use } from 'react';

function Comments({ commentsPromise }) {
  const comments = use(commentsPromise);
  return comments.map(c => <p key={c.id}>{c.text}</p>);
}
```

## Ref as a Prop
In React 19, `forwardRef` is deprecated. You can now pass `ref` directly as a regular prop to functional components.
"""
    },
    {
        "title": "Java 21 Modern Features & Best Practices",
        "technology": "Java",
        "version": "21",
        "content": """
# Java 21 LTS Official Documentation

## Virtual Threads (Project Loom - JEP 444)
Java 21 introduces Virtual Threads as a lightweight implementation of threads managed by the JDK rather than OS native threads. They dramatically reduce the cost of high-throughput concurrent applications.

```java
// Creating virtual threads in Java 21
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> {
        executor.submit(() => {
            Thread.sleep(Duration.ofSeconds(1));
            return i;
        });
    });
} // Auto-closes and waits for all tasks to complete
```

## Record Patterns (JEP 440)
Record patterns allow destructuring record components directly in `instanceof` checks and `switch` statements.

```java
record Point(int x, int y) {}

// Deconstructing record pattern in Java 21
if (obj instanceof Point(int x, int y)) {
    System.out.println("X=" + x + ", Y=" + y);
}
```

## Pattern Matching for switch (JEP 441)
Enhance `switch` statements with pattern matching, null checks, and guard expressions.
```java
static String formatter(Object obj) {
    return switch (obj) {
        case Integer i -> String.format("int %d", i);
        case Long l    -> String.format("long %d", l);
        case Double d  -> String.format("double %f", d);
        case String s  -> String.format("String %s", s);
        case null      -> "null value";
        default        -> obj.toString();
    };
}
```
"""
    },
    {
        "title": "Modern JavaScript ES2024 & Async Patterns",
        "technology": "JavaScript",
        "version": "ES2024",
        "content": """
# Modern JavaScript ES2024 Guide

## Object.groupBy & Map.groupBy
Group array items dynamically using criterion functions:
```javascript
const inventory = [
  { name: "asparagus", type: "vegetable", quantity: 5 },
  { name: "bananas", type: "fruit", quantity: 0 },
  { name: "goat", type: "meat", quantity: 23 },
];

const result = Object.groupBy(inventory, ({ type }) => type);
/*
{
  vegetable: [{ name: "asparagus", ... }],
  fruit: [{ name: "bananas", ... }],
  meat: [{ name: "goat", ... }]
}
*/
```

## Promise.withResolvers()
Utility method to extract promise capabilities (`promise`, `resolve`, `reject`) in one call:
```javascript
const { promise, resolve, reject } = Promise.withResolvers();
```

## Array.prototype.toSorted / toSpliced / toReversed
Immutable array methods that return a new array copy without mutating the original array:
```javascript
const numbers = [3, 1, 4, 1, 5];
const sorted = numbers.toSorted(); // Original `numbers` remains untouched
```
"""
    },
    {
        "title": "Python 3.13 Performance & Structural Typing Guide",
        "technology": "Python",
        "version": "3.13",
        "content": """
# Python 3.13 Official Documentation

## Experimental Free-Threaded CPython (GIL Removal)
Python 3.13 introduces experimental support for running CPython without the Global Interpreter Lock (GIL), enabling true parallel multithreading on multi-core CPU architectures.

## Type Parameter Syntax (PEP 695)
Generic classes and functions now use intuitive bracket notation:
```python
# Python 3.13 generic function syntax
def max_element[T: Comparable](items: list[T]) -> T:
    return max(items)

# Generic type aliases
type Point[T] = tuple[T, T]
```

## Dataclasses & Immutability
Use frozen dataclasses for immutable data transfer objects:
```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class UserDTO:
    id: str
    username: str
    email: str
```
"""
    }
]
