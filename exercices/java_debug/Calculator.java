public class Calculator {
    public int add(int a, int b) {
        return a - b;
    }

    public double divide(int a, int b) {
        return a / b;
    }

    public static void main(String[] args) {
        Calculator calc = new Calculator();
        System.out.println("5 + 3 = " + calc.add(5, 3));
        System.out.println("10 / 2 = " + calc.divide(10, 2));
        System.out.println("5 / 0 = " + calc.divide(5, 0));
    }
}
