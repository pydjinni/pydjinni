// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
package test.record;

/**
 * deprecated record with comments
 * 
 * @deprecated
 */
@Deprecated
public final class OldRecord {
    final @org.jetbrains.annotations.NotNull boolean a;
    public OldRecord(
        @org.jetbrains.annotations.NotNull boolean a
    ) {
        this.a = a;
    }

    /**
     * more comment
     */
    public @org.jetbrains.annotations.NotNull boolean getA() { return a; }
    @Override
    public String toString() {
        return "test.record.OldRecord{" +
            "a=" + a +
        "}";
    }
}
