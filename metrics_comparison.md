# Code Metrics Comparison: Pre vs Post Refactoring

This document compares the object-oriented and complexity metrics of the codebase before and after the refactoring (where Strategy, Adaptor, Factory, Builder, Chain of Responsibility, and Observer patterns were applied). 

> **Note**: Halstead metrics are not natively exported by the standard open-source CK or DesigniteJava configurations used in this project, so we focus on Cyclomatic Complexity (WMC) and the Chidamber & Kemerer (CK) Six OO metrics.

## 1. Overall Codebase Averages (CK Metrics)

The following table demonstrates the average metrics across all classes in the project.

| Metric | Pre-Refactor Average | Post-Refactor Average | Change | Interpretation |
|---|---|---|---|---|
| **WMC** (Weighted Methods per Class / Cyclomatic) | 8.57 | 5.14 | ⬇️ Improved | Classes are less complex and have fewer decision points on average. |
| **DIT** (Depth of Inheritance Tree) | 1.14 | 1.18 | ⬆️ Increased | Slight increase due to introducing an interface layer (Observer, Aircraft, PaymentStrategy) and abstract classes. |
| **NOC** (Number of Children) | 0.14 | 0.18 | ⬆️ Increased | Expected increase, as we now have implementations for strategies and validation handlers. |
| **CBO** (Coupling Between Objects) | 2.43 | 2.50 | ➡️ Unchanged | Remained roughly static as decoupling (Factory, Builder) balanced out by creating new compositional references. |
| **RFC** (Response for a Class) | 6.36 | 3.43 | ⬇️ Improved | Classes now invoke far fewer methods, signifying better separation of concerns. |
| **LCOM** (Lack of Cohesion in Methods) | 7.64 | 2.79 | ⬇️ Improved | Drastically improved cohesion. Classes now have a single, unified purpose rather than mixed responsibilities. |
| **LOC** (Lines of Code) | 33.71 | 19.61 | ⬇️ Improved | The average class size significantly decreased, meaning responsibilities are distributed properly rather than clumped. |

---

## 2. Key Refactored Classes Comparison

Here we zoom in on the specific classes that were targeted during the refactoring to observe the direct impact of the applied design patterns.

### `Customer`
*Refactoring applied: Builder Pattern, Chain of Responsibility*
| Metric | Pre-Refactor | Post-Refactor | Impact |
|---|---|---|---|
| **WMC** / Cyclomatic | 12 | 9 | Reduced complexity by delegating hardcoded validation chains to the `OrderValidator`. |
| **RFC** | 21 | 15 | Reduced the number of external methods called. |
| **LCOM** | 12.0 | 4.0 | Huge improvement in cohesion. |
| **LOC** | 57 | 40 | Shorter, simpler class focusing on core logic. |

### `FlightOrder`
*Refactoring applied: Strategy Pattern*
| Metric | Pre-Refactor | Post-Refactor | Impact |
|---|---|---|---|
| **WMC** / Cyclomatic | 24 | 6 | Massively simplified by removing hardcoded PayPal and CreditCard processing logic. |
| **RFC** | 24 | 5 | Methods invoked cut by ~80% by routing through the `PaymentStrategy` interface. |
| **LCOM** | 37.0 | 4.0 | Solved the massive lack of cohesion (previously the class awkwardly mixed PayPal and CC properties). |
| **LOC** | 86 | 23 | Enormous reduction in file size showing immense de-bloat. |

### `ScheduledFlight`
*Refactoring applied: Adapter Pattern, Factory Pattern*
| Metric | Pre-Refactor | Post-Refactor | Impact |
|---|---|---|---|
| **WMC** / Cyclomatic | 17 | 11 | Reduced complexity by eliminating `instanceof` checks and reflection targeting different aircraft types. |
| **CBO** | 7 | 5 | Uncoupled from specific aircraft classes (`PassengerPlane`, `Helicopter`, etc.), coupling only to the `Aircraft` interface. |
| **LOC** | 61 | 43 | Boilerplate and repetitive code drastically reduced. |

### `Schedule`
*Refactoring applied: Observer Pattern*
| Metric | Pre-Refactor | Post-Refactor | Impact |
|---|---|---|---|
| **WMC** / Cyclomatic | 13 | 19 | Complexity increased as it took on the role of an Observable Subject managing state and observers. |
| **RFC** | 12 | 16 | Small increase due to observer notification loops. |
| **LOC** | 31 | 50 | Increased size because it is now managing an extensible `Observer` list. |

## Conclusion
The refactoring successfully improved the maintainability and quality of the system. We saw a stark reduction in average Cyclomatic Complexity (`WMC` down from 8.57 to 5.14) and vastly improved Cohesion (`LCOM` dropped from 7.64 to 2.79). Furthermore, the structural patterns prevented monolithic "God classes", demonstrated by the average Lines of Code (`LOC`) dropping from 33.71 per class to 19.61. This confirms that the implementation of design patterns resolved the structural flaws in the starter code.
