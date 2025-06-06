// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
package test.record;

public final class PrimitiveTypes {
    final @org.jetbrains.annotations.NotNull boolean booleanT;
    final @org.jetbrains.annotations.NotNull byte byteT;
    final @org.jetbrains.annotations.NotNull short shortT;
    final @org.jetbrains.annotations.NotNull int intT;
    final @org.jetbrains.annotations.NotNull long longT;
    final @org.jetbrains.annotations.NotNull float floatT;
    final @org.jetbrains.annotations.NotNull double doubleT;
    final @org.jetbrains.annotations.NotNull String stringT;
    final java.time.@org.jetbrains.annotations.NotNull Instant dateT;
    public PrimitiveTypes(
        @org.jetbrains.annotations.NotNull boolean booleanT,
        @org.jetbrains.annotations.NotNull byte byteT,
        @org.jetbrains.annotations.NotNull short shortT,
        @org.jetbrains.annotations.NotNull int intT,
        @org.jetbrains.annotations.NotNull long longT,
        @org.jetbrains.annotations.NotNull float floatT,
        @org.jetbrains.annotations.NotNull double doubleT,
        @org.jetbrains.annotations.NotNull String stringT,
        java.time.@org.jetbrains.annotations.NotNull Instant dateT
    ) {
        this.booleanT = booleanT;
        this.byteT = byteT;
        this.shortT = shortT;
        this.intT = intT;
        this.longT = longT;
        this.floatT = floatT;
        this.doubleT = doubleT;
        this.stringT = stringT;
        this.dateT = dateT;
    }

    public @org.jetbrains.annotations.NotNull boolean getBooleanT() { return booleanT; }
    public @org.jetbrains.annotations.NotNull byte getByteT() { return byteT; }
    public @org.jetbrains.annotations.NotNull short getShortT() { return shortT; }
    public @org.jetbrains.annotations.NotNull int getIntT() { return intT; }
    public @org.jetbrains.annotations.NotNull long getLongT() { return longT; }
    public @org.jetbrains.annotations.NotNull float getFloatT() { return floatT; }
    public @org.jetbrains.annotations.NotNull double getDoubleT() { return doubleT; }
    public @org.jetbrains.annotations.NotNull String getStringT() { return stringT; }
    public java.time.@org.jetbrains.annotations.NotNull Instant getDateT() { return dateT; }
    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof PrimitiveTypes)) {
            return false;
        }
        PrimitiveTypes other = (PrimitiveTypes) obj;
        return this.booleanT == other.booleanT &&
               this.byteT == other.byteT &&
               this.shortT == other.shortT &&
               this.intT == other.intT &&
               this.longT == other.longT &&
               this.floatT == other.floatT &&
               this.doubleT == other.doubleT &&
               stringT.equals(other.stringT) &&
               dateT.equals(other.dateT);
    }

    @Override
    public int hashCode() {
        // Pick an arbitrary non-zero starting value
        int hashCode = 17;
        hashCode = hashCode * 31 + (booleanT ? 1 : 0);
        hashCode = hashCode * 31 + byteT;
        hashCode = hashCode * 31 + shortT;
        hashCode = hashCode * 31 + intT;
        hashCode = hashCode * 31 + ((int) (longT ^ (longT >>> 32)));
        hashCode = hashCode * 31 + Float.floatToIntBits(floatT);
        hashCode = hashCode * 31 + ((int) (Double.doubleToLongBits(doubleT) ^ (Double.doubleToLongBits(doubleT) >>> 32)));
        hashCode = hashCode * 31 + stringT.hashCode();
        hashCode = hashCode * 31 + dateT.hashCode();
        return hashCode;
    }
    @Override
    public String toString() {
        return "test.record.PrimitiveTypes{" +
            "booleanT=" + booleanT +
            ",byteT=" + byteT +
            ",shortT=" + shortT +
            ",intT=" + intT +
            ",longT=" + longT +
            ",floatT=" + floatT +
            ",doubleT=" + doubleT +
            ",stringT=" + stringT +
            ",dateT=" + dateT +
        "}";
    }
}
