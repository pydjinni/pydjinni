import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import test.flags_test.Helper;
import test.flags_test.ExampleFlags;
import java.util.EnumSet;

class TestFlags {
    @Test
    void testFlags() {
        var exampleFlags = Helper.getFlag(EnumSet.of(ExampleFlags.A));
        assertEquals(exampleFlags, EnumSet.of(ExampleFlags.A));
    }

    @Test
    void testAllFlags() {
        var exampleFlags = Helper.getAllFlag(EnumSet.allOf(ExampleFlags.class));
        assertEquals(exampleFlags, EnumSet.allOf(ExampleFlags.class));
    }

    @Test
    void testNoneFlags() {
        var exampleFlags = Helper.getNoneFlag(EnumSet.noneOf(ExampleFlags.class));
        assertEquals(exampleFlags, EnumSet.noneOf(ExampleFlags.class));
    }



}