package flight.reservation.order;

import flight.reservation.Customer;
import flight.reservation.flight.ScheduledFlight;

import java.util.List;

public class PassengerNoFlyListValidator extends OrderValidator {
    @Override
    protected boolean check(Customer customer, List<String> passengerNames, List<ScheduledFlight> flights) {
        return passengerNames.stream().noneMatch(passenger -> FlightOrder.getNoFlyList().contains(passenger));
    }
}
