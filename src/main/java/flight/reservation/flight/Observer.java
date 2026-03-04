package flight.reservation.flight;

public interface Observer {
    void update(ScheduledFlight flight, String action);
}
