// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
package test.record;

public final class OptionalTypes {
    final Integer intOptional;
    final String stringOptional;
    public OptionalTypes(
        @org.jetbrains.annotations.Nullable
        Integer intOptional,
        @org.jetbrains.annotations.Nullable
        String stringOptional
    ) {
        this.intOptional = intOptional;
        this.stringOptional = stringOptional;
    }

    @org.jetbrains.annotations.Nullable
    public Integer getIntOptional() { return intOptional; }
    @org.jetbrains.annotations.Nullable
    public String getStringOptional() { return stringOptional; }
    @Override
    public String toString() {
        return "test.record.OptionalTypes{" +
            "intOptional=" + intOptional +
            ",stringOptional=" + stringOptional +
        "}";
    }
}
