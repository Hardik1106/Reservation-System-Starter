package flight.reservation.plane;

public class PassengerDroneAdapter implements Aircraft {
    private final PassengerDrone drone;

    public PassengerDroneAdapter(PassengerDrone drone) {
        this.drone = drone;
    }

    @Override
    public String getModel() {
        return "HypaHype";
    }

    @Override
    public int getPassengerCapacity() {
        return 4;
    }

    @Override
    public int getCrewCapacity() {
        return 0;
    }
}
