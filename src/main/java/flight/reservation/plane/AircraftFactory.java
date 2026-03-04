package flight.reservation.plane;

public class AircraftFactory {
    public static Aircraft createAircraft(String type, String model) {
        switch (type) {
            case "PassengerPlane":
                return new PassengerPlaneAdapter(new PassengerPlane(model));
            case "Helicopter":
                return new HelicopterAdapter(new Helicopter(model));
            case "PassengerDrone":
                return new PassengerDroneAdapter(new PassengerDrone(model));
            default:
                throw new IllegalArgumentException(String.format("Aircraft type '%s' is not recognized", type));
        }
    }
}
