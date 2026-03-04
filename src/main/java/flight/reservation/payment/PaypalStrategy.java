package flight.reservation.payment;

public class PaypalStrategy implements PaymentStrategy {
    private String email;
    private String password;

    public PaypalStrategy(String email, String password) {
        this.email = email;
        this.password = password;
    }

    @Override
    public boolean pay(double amount) throws IllegalStateException {
        if (email != null && password != null && email.equals(Paypal.DATA_BASE.get(password))) {
            System.out.println("Paying " + amount + " using PayPal.");
            return true;
        } else {
            throw new IllegalStateException("Payment information is not set or not valid.");
        }
    }
}
