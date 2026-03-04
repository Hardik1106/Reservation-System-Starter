package flight.reservation.order;

import flight.reservation.Customer;
import flight.reservation.Passenger;
import flight.reservation.flight.ScheduledFlight;

import java.util.List;

public class FlightOrderBuilder {
    private List<ScheduledFlight> flights;
    private Customer customer;
    private double price;
    private List<Passenger> passengers;

    public FlightOrderBuilder setFlights(List<ScheduledFlight> flights) {
        this.flights = flights;
        return this;
    }

    public FlightOrderBuilder setCustomer(Customer customer) {
        this.customer = customer;
        return this;
    }

    public FlightOrderBuilder setPrice(double price) {
        this.price = price;
        return this;
    }

    public FlightOrderBuilder setPassengers(List<Passenger> passengers) {
        this.passengers = passengers;
        return this;
    }

    public FlightOrder build() {
        if (flights == null || customer == null || passengers == null) {
            throw new IllegalStateException("Flights, Customer, and Passengers must be set to build a FlightOrder");
        }
        FlightOrder order = new FlightOrder(flights);
        order.setCustomer(customer);
        order.setPrice(price);
        order.setPassengers(passengers);
        return order;
    }
}
