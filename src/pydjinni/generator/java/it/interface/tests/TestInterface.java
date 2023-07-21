import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.*;
import test.interface_test.Calculator;
import test.interface_test.PlatformInterface;

class TestInterface {
    Calculator calculator;

    @BeforeEach
    void setup() {
        calculator = Calculator.getInstance();
    }

    @Test
    void testCalculator() {
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
        var result = calculator.getPlatformValue(new PlatformInterface() {
            public byte getValue() {
                return 5;
            }
        });
    }

    @Test
    void testMethodNoParametersNoReturn() {
        calculator.noParametersNoReturn();
    }

    @Test
    void testMethodThrowingException() {
        Exception exception = assertThrows(RuntimeException.class, () -> calculator.throwingException());
        assertTrue(exception.getMessage().equals("shit hit the fan"));
    }

}
