// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
package test.record;

public final class NestedType {
    final int a;
    final java.util.ArrayList<java.util.ArrayList<Integer>> b;
    public NestedType(
        @org.jetbrains.annotations.NotNull
        int a,
        @org.jetbrains.annotations.NotNull
        java.util.ArrayList<java.util.ArrayList<Integer>> b
    ) {
        this.a = a;
        this.b = b;
    }

    @org.jetbrains.annotations.NotNull
    public int getA() { return a; }
    @org.jetbrains.annotations.NotNull
    public java.util.ArrayList<java.util.ArrayList<Integer>> getB() { return b; }
    @Override
    public String toString() {
        return "test.record.NestedType{" +
            "a=" + a +
            ",b=" + b +
        "}";
    }
}
