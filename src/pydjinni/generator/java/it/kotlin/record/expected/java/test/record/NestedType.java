// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
package test.record;

public final class NestedType {
    final @org.jetbrains.annotations.NotNull int a;
    final java.util.@org.jetbrains.annotations.NotNull ArrayList<java.util.@org.jetbrains.annotations.NotNull ArrayList<@org.jetbrains.annotations.NotNull Integer>> b;
    public NestedType(
        @org.jetbrains.annotations.NotNull int a,
        java.util.@org.jetbrains.annotations.NotNull ArrayList<java.util.@org.jetbrains.annotations.NotNull ArrayList<@org.jetbrains.annotations.NotNull Integer>> b
    ) {
        this.a = a;
        this.b = b;
    }

    public @org.jetbrains.annotations.NotNull int getA() { return a; }
    public java.util.@org.jetbrains.annotations.NotNull ArrayList<java.util.@org.jetbrains.annotations.NotNull ArrayList<@org.jetbrains.annotations.NotNull Integer>> getB() { return b; }
    @Override
    public String toString() {
        return "test.record.NestedType{" +
            "a=" + a +
            ",b=" + b +
        "}";
    }
}
