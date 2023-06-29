import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import test.interface_test.Calculator;
import test.interface_test.PlatformInterface;

class TestInterface {
    @Test
    void testCalculator() {
        var calculator = Calculator.getInstance();
        var result = calculator.add((byte)40, (byte)2);
        assertEquals(result, 42);
    }

    @Test
    void testConstant() {
        var constant = Calculator.A;
        assertEquals(constant, 5);
    }

    @Test
    void testPlatformImplementation() {
        var calculator = Calculator.getInstance();
        var result = calculator.getPlatformValue(new PlatformInterface() {
            public byte getValue() {
                return 5;
            }
        });
    }

    @Test
    void testMethodNoParametersNoReturn() {
        var calculator = Calculator.getInstance();
        calculator.noParametersNoReturn();
    }

}