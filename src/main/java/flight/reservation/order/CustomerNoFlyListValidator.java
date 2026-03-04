package flight.reservation.order;

import flight.reservation.Customer;
import flight.reservation.flight.ScheduledFlight;

import java.util.List;

public class CustomerNoFlyListValidator extends OrderValidator {
    @Override
    protected boolean check(Customer customer, List<String> passengerNames, List<ScheduledFlight> flights) {
        return !FlightOrder.getNoFlyList().contains(customer.getName());
    }
}
