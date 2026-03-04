# Assignment 2 - Design Patterns Implementation
**Team Number:** [Insert Team Number]  
**Team Members:** [Insert Team Members]  

---

## Relevant Assumptions
1. The codebase is tested primarily through `ScenarioTest` and we assume the validation logic extracted fulfills all existing domain constraints.
2. We assume the code metrics calculated (CK Metrics and Designite Java output) are the standard evaluation formats for lines of code, cohesion, and cyclomatic complexity requested by the prompt.
3. Halstead metrics are not natively provided by the core CK extractor but can theoretically be inferred; however, we rely on the standard Cyclomatic/WMC mapping as the primary complexity measure out of the box.

---

## Part 1: Design Pattern Applications and Reasoning

### 1. Strategy Pattern (Payment Processing)
**Description & Reasoning**: 
The `FlightOrder` class originally contained monolithic methods for different payment types (`processOrderWithCreditCard`, `processOrderWithPayPal`). This violated the Open/Closed Principle because adding a new payment method required modifying the class. We introduced a `PaymentStrategy` interface and implemented `CreditCardStrategy` and `PaypalStrategy`. 
**Benefits & Drawbacks**:
- *Benefits*: Removes tight coupling, adheres to Open/Closed Principle, makes adding new payments trivial.
- *Drawbacks*: Slight increase in the number of classes.

**Class Structure Before & After:**
```plantuml
' Before Applying Strategy Pattern 
class FlightOrder {
  +processOrderWithCreditCard()
  +processOrderWithPayPal()
}

' After Applying Strategy Pattern 
class FlightOrder {
  -paymentStrategy: PaymentStrategy
  +processOrderWithStrategy(strategy: PaymentStrategy)
}
interface PaymentStrategy {
  +pay(amount: double): boolean
}
class CreditCardStrategy implements PaymentStrategy { }
class PaypalStrategy implements PaymentStrategy { }
FlightOrder o-- PaymentStrategy
```

**Code Snippet:**
```java
// FlightOrder.java
public boolean processOrderWithStrategy(PaymentStrategy strategy) {
    if (isClosed()) return true;
    boolean isPaid = strategy.pay(this.getPrice());
    if (isPaid) this.setClosed();
    return isPaid;
}
```

---

### 2. Adapter Pattern (Aircraft Unification)
**Description & Reasoning**: 
The system treated `Helicopter`, `PassengerPlane`, and `PassengerDrone` as distinct, unconnected types without a shared abstraction, forcing `instanceof` checks and reflection (`NoSuchFieldException`) when querying capacities. We created an `Aircraft` interface and corresponding adapters to wrap these existing classes.
**Benefits & Drawbacks**:
- *Benefits*: Eliminates error-prone reflection and `instanceof` checks. The system can now treat all aircraft identically through polymorphic behavior.
- *Drawbacks*: Increased object allocation due to wrapping inside the adapter.

**Class Structure Before & After:**
```plantuml
' Before Applying Adapter Pattern
class ScheduledFlight {
  -passengerPlane: PassengerPlane
  -helicopter: Helicopter
  +getCapacity()
}
class Helicopter { +getPassengerCapacity() }
class PassengerPlane { +getPassengerCapacity() }

' After Applying Adapter Pattern
class ScheduledFlight {
  -aircraft: Aircraft
  +getCapacity()
}
interface Aircraft {
  +getPassengerCapacity()
}
class HelicopterAdapter implements Aircraft { -helicopter: Helicopter }
class PassengerPlaneAdapter implements Aircraft { -plane: PassengerPlane }
ScheduledFlight --> Aircraft
```

**Code Snippet:**
```java
// HelicopterAdapter.java
public class HelicopterAdapter implements Aircraft {
    private final Helicopter helicopter;
    public HelicopterAdapter(Helicopter helicopter) { this.helicopter = helicopter; }
    
    @Override
    public int getPassengerCapacity() { return helicopter.getPassengerCapacity(); }
}
```

---

### 3. Factory Pattern (Aircraft Instantiation)
**Description & Reasoning**: 
Instantiating planes and manually wrapping them in adapters leaked concrete implementation details to the tests and the `Runner` class. We introduced an `AircraftFactory` to encapsulate instantiation.
**Benefits & Drawbacks**:
- *Benefits*: Centralizes object creation logic. Clients only parse strings representing type and model without knowing the concrete class.
- *Drawbacks*: The factory switch statement must be updated when new aircraft models are added.

**Class Structure Before & After:**
```plantuml
' Before Applying Factory Pattern
class Client {
  +initOptions()
}
Client --> Helicopter
Client --> PassengerPlane

' After Applying Factory Pattern
class Client { }
class AircraftFactory {
  +createAircraft(type: String, model: String): Aircraft
}
Client --> AircraftFactory
AircraftFactory --> HelicopterAdapter
AircraftFactory --> PassengerPlaneAdapter
```

**Code Snippet:**
```java
// AircraftFactory.java
public static Aircraft createAircraft(String type, String model) {
    switch (type) {
        case "PassengerPlane": return new PassengerPlaneAdapter(new PassengerPlane(model));
        case "Helicopter": return new HelicopterAdapter(new Helicopter(model));
        // ... (Drone handled here too)
    }
}
```

---

### 4. Builder Pattern (FlightOrder Creation)
**Description & Reasoning**: 
`Customer.createOrder` previously constructed a `FlightOrder` and sequentially called setters, leaving the order in an ambiguous, incomplete state during parts of its lifetime. A `FlightOrderBuilder` was introduced to collect parameters and atomically assemble the object.
**Benefits & Drawbacks**:
- *Benefits*: Ensures orders are always instantiated in a fully valid, structurally sound state. Code is highly readable.
- *Drawbacks*: Extra boilerplate code for the builder class itself.

**Class Structure Before & After:**
```plantuml
' Before Applying Builder Pattern
class Customer {
  +createOrder()
}
class FlightOrder { +setCustomer(), +setPrice() ... }
Customer -> FlightOrder : Instantiates directly

' After Applying Builder Pattern
class FlightOrderBuilder {
  +setCustomer()
  +setPrice()
  +build(): FlightOrder
}
Customer -> FlightOrderBuilder : Uses to build
FlightOrderBuilder -> FlightOrder : Assembles
```

**Code Snippet:**
```java
// Customer.createOrder snippet
FlightOrder order = new FlightOrderBuilder()
    .setFlights(flights)
    .setCustomer(this)
    .setPrice(price)
    .setPassengers(passengers)
    .build();
```

---

### 5. Chain of Responsibility Pattern (Order Validation)
**Description & Reasoning**: 
Validating an order required hardcoded sequences of validation (`!FlightOrder.getNoFlyList().contains(...)` and capacity checks) tightly coupled inside `Customer`. We decoupled this into an `OrderValidator` chain (`CustomerNoFlyListValidator`, etc.).
**Benefits & Drawbacks**:
- *Benefits*: Adding or reordering validation rules is simple and respects the Open/Closed Principle.
- *Drawbacks*: If the chain is exceptionally long or improperly linked, debugging validation failures can be harder.

**Class Structure Before & After:**
```plantuml
' Before Applying Chain of Responsibility
class Customer {
  +isOrderValid(order) ' Hardcoded validations here
}

' After Applying Chain of Responsibility
abstract class OrderValidator {
  +setNext(validator): OrderValidator
  +isValid(...): boolean
}
class CustomerNoFlyListValidator extends OrderValidator { }
class CapacityValidator extends OrderValidator { }
Customer --> OrderValidator
```

**Code Snippet:**
```java
// Setting up the validation chain
OrderValidator validator = new CustomerNoFlyListValidator();
validator.setNext(new PassengerNoFlyListValidator())
         .setNext(new CapacityValidator());

if (!validator.isValid(this, passengerNames, flights)) {
    throw new IllegalStateException("Order is not valid");
}
```

---

### 6. Observer Pattern (Schedule Updates)
**Description & Reasoning**: 
When flights were added or removed from the `Schedule`, there was no extensible event-driven way to alert other parts of the application. The `Schedule` was refactored into an Observable subject, notifying registered `Observer` interfaces.
**Benefits & Drawbacks**:
- *Benefits*: Promotes a reactive, decoupled architecture. Listeners (e.g., UI or external systems) can subscribe to flight schedule changes.
- *Drawbacks*: Observers might cause memory leaks if not explicitly deregistered.

**Class Structure Before & After:**
```plantuml
' Before Applying Observer Pattern
class Schedule {
  +scheduleFlight()
  +removeFlight()
}

' After Applying Observer Pattern
class Schedule {
  -observers: List<Observer>
  +addObserver(o: Observer)
  +notifyObservers()
}
interface Observer {
  +update(flight: ScheduledFlight, action: String)
}
Schedule --> Observer
```

**Code Snippet:**
```java
// Schedule.java
public void scheduleFlight(Flight flight, Date date) {
    ScheduledFlight scheduledFlight = new ScheduledFlight(...);
    scheduledFlights.add(scheduledFlight);
    notifyObservers(scheduledFlight, "SCHEDULED");
}
```

---

## Part 2: Code Quality Metrics Analysis

Static analysis was performed using **CK Metrics** and **Designite Java** to extract object-oriented and complexity metrics across the entire project before and after refactoring. The results, side-by-side, are tabulated below.

### 2.1 Overall Codebase Averages

| Metric | Pre-Refactor Average | Post-Refactor Average | Change |
|---|---|---|---|
| **WMC** (Weighted Methods / Cyclomatic) | 8.57 | 5.14 | ⬇️ Improved |
| **DIT** (Depth of Inheritance Tree) | 1.14 | 1.18 | ⬆️ Increased |
| **NOC** (Number of Children) | 0.14 | 0.18 | ⬆️ Increased |
| **CBO** (Coupling Between Objects) | 2.43 | 2.50 | ➡️ Unchanged |
| **RFC** (Response for a Class) | 6.36 | 3.43 | ⬇️ Improved |
| **LCOM** (Lack of Cohesion in Methods) | 7.64 | 2.79 | ⬇️ Improved |
| **LOC** (Lines of Code) | 33.71 | 19.61 | ⬇️ Improved |

### 2.2 Key Targeted Class Metrics

| Class | Metric | Pre-Refactor | Post-Refactor |
|---|---|---|---|
| `Customer` | WMC | 12 | 9 |
| `Customer` | LCOM | 12.0 | 4.0 |
| `Customer` | LOC | 57 | 40 |
| `FlightOrder` | WMC | 24 | 6 |
| `FlightOrder` | LCOM | 37.0 | 4.0 |
| `FlightOrder` | LOC | 86 | 23 |
| `ScheduledFlight` | WMC | 17 | 11 |
| `ScheduledFlight` | CBO | 7 | 5 |
| `ScheduledFlight` | LOC | 61 | 43 |
| `Schedule` | WMC | 13 | 19 |
| `Schedule` | LCOM | 0.0 | 0.0 |
| `Schedule` | LOC | 31 | 50 |

---

## Part 3: Metrics Analysis & Reasoning

Based on the tables above, here is the analysis detailing how the design patterns concretely shaped software quality outside of just logical structure:

### Did the metric improve, worsen, or remain unchanged?
- **Improved**: Complexity (WMC), Cohesion (LCOM), File Size (LOC), and External Method Invocation (RFC) all improved massively across the board. The average Cyclomatic Complexity dropped from roughly 8.57 to 5.14. 
- **Worsened/Increased**: DIT (Depth of Inheritance Tree) and NOC (Number of Children) slightly increased. `Schedule` specifically saw an increase in WMC and LOC.
- **Unchanged**: Coupling Between Objects (CBO) remained largely similar on a macro scale.

### Why did this change occur?
- The large improvements in **WMC, LCOM, and LOC** were driven heavily by removing God-Class behaviors. For example, `FlightOrder` shed 60+ lines of code and massive cyclomatic complexity by removing hardcoded PayPal and CreditCard if-else logic and deferring to the Strategy Pattern. This highly cohesive refactor drove LCOM down from 37.0 to 4.0.
- `ScheduledFlight` and `Customer` gained similar cohesion wins using Adapters and Chain of Responsibility, respectfully.
- The increases in **DIT and NOC** occurred strictly because of newly introduced abstraction hierarchies (e.g. `PaymentStrategy` interface, `OrderValidator` abstract class). 
- `Schedule` saw its complexity (**WMC**) and **LOC** slightly increase because it gained new Subject responsibilities from the Observer Pattern, giving it a list operation overhead.

### Were any metrics negatively impacted?
The introduction of `AircraftFactory`, `PaymentStrategy`, and `OrderValidator` intrinsically led to the proliferation of smaller classes, inherently driving up **Depth of Inheritance**. While technically an increase in metric "cost," it is a direct layout of standard OOP abstraction. Coupling (CBO) remained static because, while we decoupled things tightly, the new classes heavily compositionally reference each other (e.g., validators linking to validators). 

### What do the results tell you about the overall code quality?
The refactored classes now securely conform to the Single Responsibility Principle and the Open/Closed Principle. Monolithic control-flow branches (High WMC) have been dissolved into polymorphic dispatch paths, ensuring a significantly higher level of robustness and maintainability.
