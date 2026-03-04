package flight.reservation.payment;

public class CreditCardStrategy implements PaymentStrategy {
    private CreditCard creditCard;

    public CreditCardStrategy(CreditCard creditCard) {
        this.creditCard = creditCard;
    }

    @Override
    public boolean pay(double amount) throws IllegalStateException {
        if (creditCard != null && creditCard.isValid()) {
            System.out.println("Paying " + amount + " using Credit Card.");
            double remainingAmount = creditCard.getAmount() - amount;
            if (remainingAmount < 0) {
                System.out.printf("Card limit reached - Balance: %f%n", remainingAmount);
                throw new IllegalStateException("Card limit reached");
            }
            creditCard.setAmount(remainingAmount);
            return true;
        } else {
            throw new IllegalStateException("Payment information is not set or not valid.");
        }
    }
}
