# Refactoring Report

This report outlines the refactoring performed on the Reservation System to improve its maintainability, extensibility, and code quality. We applied six key design patterns to resolve specific flaws and code smells.

## 1. Strategy Pattern (Payment Processing)
**Flaw**: The `FlightOrder` class originally had separate, monolithic methods for different payment types (`processOrderWithCreditCard`, `processOrderWithPayPal`), violating the Open/Closed Principle. Adding a new payment method would require modifying the `FlightOrder` class.

**Refactoring**: We introduced a `PaymentStrategy` interface and implemented `CreditCardStrategy` and `PaypalStrategy`.
**How it helped**: The order class now delegates payment to the strategy, removing tight coupling and making it trivial to add new payment methods. 

*Code Snippet*:
```java
// FlightOrder.java
public boolean processOrderWithStrategy(PaymentStrategy strategy) {
    if (isClosed()) {
        return true;
    }
    boolean isPaid = strategy.pay(this.getPrice());
    if (isPaid) {
        this.setClosed();
    }
    return isPaid;
}
```

## 2. Adapter Pattern (Aircraft Unification)
**Flaw**: The system handled `Helicopter`, `PassengerPlane`, and `PassengerDrone` as entirely disparate objects since they did not share a common abstraction. This resulted in `instanceof` checks and reflection (`NoSuchFieldException`) when checking capacity, which is brittle and error-prone.

**Refactoring**: Created an `Aircraft` interface and corresponding adapters (`PassengerPlaneAdapter`, `HelicopterAdapter`, `PassengerDroneAdapter`) that wrap the existing classes.
**How it helped**: The `Flight` and `ScheduledFlight` classes can now interact seamlessly with any aircraft type via a unified `Aircraft` interface, completely eliminating reflection and `instanceof` checks.

*Code Snippet*:
```java
// HelicopterAdapter.java
public class HelicopterAdapter implements Aircraft {
    private final Helicopter helicopter;
    
    public HelicopterAdapter(Helicopter helicopter) {
        this.helicopter = helicopter;
    }

    @Override
    public int getPassengerCapacity() {
        return helicopter.getPassengerCapacity();
    }
    // ...
}
```

## 3. Factory Pattern (Aircraft Instantiation)
**Flaw**: Instantiating planes and wrapping them in adapters manually across tests and the `Runner` class led to heavy, repetitive code that leaked concrete implementation details to the client.

**Refactoring**: Created an `AircraftFactory` responsible for parsing the requested type and model and returning the correctly adapted `Aircraft`.
**How it helped**: Centralized the creation logic. Clients only need to provide the type and model strings.

*Code Snippet*:
```java
// AircraftFactory.java
public static Aircraft createAircraft(String type, String model) {
    switch (type) {
        case "PassengerPlane":
            return new PassengerPlaneAdapter(new PassengerPlane(model));
        case "Helicopter":
            return new HelicopterAdapter(new Helicopter(model));
        // ...
    }
}
```

## 4. Builder Pattern (FlightOrder Creation)
**Flaw**: `Customer.createOrder` was manually instantiating `FlightOrder` and sequentially calling setters (`setCustomer`, `setPrice`, `setPassengers`), which left the order in an incomplete state during instantiation.

**Refactoring**: Introduced a `FlightOrderBuilder` to handle the construction of the order.
**How it helped**: Centralized validation upon building and ensured that orders are created atomically in a valid state.

*Code Snippet*:
```java
FlightOrder order = new FlightOrderBuilder()
    .setFlights(flights)
    .setCustomer(this)
    .setPrice(price)
    .setPassengers(passengers)
    .build();
```

## 5. Chain of Responsibility Pattern (Order Validation)
**Flaw**: Validating an order required a large grouping of boolean checks (`!FlightOrder.getNoFlyList().contains(...)`, capacity checks) hardcoded inside the `Customer` class. 

**Refactoring**: Extracted these checks into an `OrderValidator` chain (`CustomerNoFlyListValidator`, `PassengerNoFlyListValidator`, `CapacityValidator`).
**How it helped**: Adding or removing new validation rules is now simply a matter of adding or detaching a link in the chain, preventing the `Customer` class from mutating when validation rules change.

*Code Snippet*:
```java
OrderValidator validator = new CustomerNoFlyListValidator();
validator.setNext(new PassengerNoFlyListValidator())
         .setNext(new CapacityValidator());

if (!validator.isValid(this, passengerNames, flights)) {
    throw new IllegalStateException("Order is not valid");
}
```

## 6. Observer Pattern (Schedule Updates)
**Flaw**: When flights were added or removed from the `Schedule`, there was no extensible way for other parts of the application to react to these events.

**Refactoring**: Turned `Schedule` into an observable subject that notifies registered `Observer`s when a flight is scheduled or removed.
**How it helped**: The system is now reactive. UI elements, logging mechanisms, or external systems can implement `Observer` and register themselves with the schedule.

*Code Snippet*:
```java
// Schedule.java
public void scheduleFlight(Flight flight, Date date) {
    ScheduledFlight scheduledFlight = new ScheduledFlight(...);
    scheduledFlights.add(scheduledFlight);
    notifyObservers(scheduledFlight, "SCHEDULED");
}
```
