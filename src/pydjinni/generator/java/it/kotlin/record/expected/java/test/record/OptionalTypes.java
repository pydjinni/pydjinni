// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
package test.record;

public final class OptionalTypes {
    final @org.jetbrains.annotations.Nullable Integer intOptional;
    final @org.jetbrains.annotations.Nullable String stringOptional;
    public OptionalTypes(
        @org.jetbrains.annotations.Nullable Integer intOptional,
        @org.jetbrains.annotations.Nullable String stringOptional
    ) {
        this.intOptional = intOptional;
        this.stringOptional = stringOptional;
    }

    public @org.jetbrains.annotations.Nullable Integer getIntOptional() { return intOptional; }
    public @org.jetbrains.annotations.Nullable String getStringOptional() { return stringOptional; }
    @Override
    public String toString() {
        return "test.record.OptionalTypes{" +
            "intOptional=" + intOptional +
            ",stringOptional=" + stringOptional +
        "}";
    }
}
