import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import test.record.Foo;
import test.record.Helper;
import test.record.RecordTest;

class TestRecord {
    static {
        new RecordTest();
    }


    @Test
    void foo() {
        var foo = new Foo((byte)5);
        var new_foo = Helper.getFoo(foo);

    }

}