package flight.reservation.order;

import flight.reservation.Customer;
import flight.reservation.flight.ScheduledFlight;

import java.util.List;

public class CapacityValidator extends OrderValidator {
    @Override
    protected boolean check(Customer customer, List<String> passengerNames, List<ScheduledFlight> flights) {
        return flights.stream()
                .allMatch(scheduledFlight -> scheduledFlight.getAvailableCapacity() >= passengerNames.size());
    }
}
