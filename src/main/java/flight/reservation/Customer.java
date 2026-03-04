package flight.reservation;

import flight.reservation.flight.ScheduledFlight;
import flight.reservation.order.FlightOrder;
import flight.reservation.order.Order;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class Customer {

    private String email;
    private String name;
    private List<Order> orders;

    public Customer(String name, String email) {
        this.name = name;
        this.email = email;
        this.orders = new ArrayList<>();
    }

    public FlightOrder createOrder(List<String> passengerNames, List<ScheduledFlight> flights, double price) {
        flight.reservation.order.OrderValidator validator = new flight.reservation.order.CustomerNoFlyListValidator();
        validator.setNext(new flight.reservation.order.PassengerNoFlyListValidator())
                .setNext(new flight.reservation.order.CapacityValidator());

        if (!validator.isValid(this, passengerNames, flights)) {
            throw new IllegalStateException("Order is not valid");
        }
        List<Passenger> passengers = passengerNames
                .stream()
                .map(Passenger::new)
                .collect(Collectors.toList());

        FlightOrder order = new flight.reservation.order.FlightOrderBuilder()
                .setFlights(flights)
                .setCustomer(this)
                .setPrice(price)
                .setPassengers(passengers)
                .build();

        order.getScheduledFlights().forEach(scheduledFlight -> scheduledFlight.addPassengers(passengers));
        orders.add(order);
        return order;
    }

    // Removed isOrderValid as it's replaced by OrderValidator chain

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<Order> getOrders() {
        return orders;
    }

    public void setOrders(List<Order> orders) {
        this.orders = orders;
    }

}
