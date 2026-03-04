package flight.reservation.plane;

public class PassengerPlaneAdapter implements Aircraft {
    private final PassengerPlane plane;

    public PassengerPlaneAdapter(PassengerPlane plane) {
        this.plane = plane;
    }

    @Override
    public String getModel() {
        return plane.model;
    }

    @Override
    public int getPassengerCapacity() {
        return plane.passengerCapacity;
    }

    @Override
    public int getCrewCapacity() {
        return plane.crewCapacity;
    }
}
