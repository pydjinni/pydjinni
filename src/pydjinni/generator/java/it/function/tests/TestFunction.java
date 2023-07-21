import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.*;
import test.function_test.*;
import java.util.*;
import java.time.*;

class TestFunction {

    @Test
    void testNamedFunction() {
        Helper.namedFunction(input -> {
            return input == 42;
        });
    }

    @Test
    void testAnonymousFunction() {
        Helper.anonymousFunction(input -> {
            return input == 42;
        });
    }

    @Test
    void testCppNamedFunction() {
        var function = Helper.cppNamedFunction();
        var result = function.invoke(42);
        assertTrue(result);
    }

    @Test
    void testCppAnonymousFunction() {
        var function = Helper.cppAnonymousFunction();
        var result = function.invoke(42);
        assertTrue(result);
    }

    @Test
    void testCppFunctionThrowingException() {
        var function = Helper.cppFunctionThrowingException();
        Exception exception = assertThrows(RuntimeException.class, () -> function.invoke());
        assertTrue(exception.getMessage().equals("shit hit the fan"));
    }
}
