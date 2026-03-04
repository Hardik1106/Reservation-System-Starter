package flight.reservation.order;

import flight.reservation.Customer;
import flight.reservation.flight.ScheduledFlight;

import java.util.List;

public abstract class OrderValidator {
    private OrderValidator next;

    public OrderValidator setNext(OrderValidator next) {
        this.next = next;
        return next;
    }

    public boolean isValid(Customer customer, List<String> passengerNames, List<ScheduledFlight> flights) {
        if (check(customer, passengerNames, flights)) {
            if (next != null) {
                return next.isValid(customer, passengerNames, flights);
            }
            return true;
        }
        return false;
    }

    protected abstract boolean check(Customer customer, List<String> passengerNames, List<ScheduledFlight> flights);
}
