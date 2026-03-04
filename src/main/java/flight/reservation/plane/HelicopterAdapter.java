package flight.reservation.plane;

public class HelicopterAdapter implements Aircraft {
    private final Helicopter helicopter;

    public HelicopterAdapter(Helicopter helicopter) {
        this.helicopter = helicopter;
    }

    @Override
    public String getModel() {
        return helicopter.getModel();
    }

    @Override
    public int getPassengerCapacity() {
        return helicopter.getPassengerCapacity();
    }

    @Override
    public int getCrewCapacity() {
        return 2;
    }
}
