// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
package test.record;

public final class PrimitiveTypes {
    final boolean booleanT;
    final byte byteT;
    final short shortT;
    final int intT;
    final long longT;
    final float floatT;
    final double doubleT;
    final String stringT;
    final java.time.Instant dateT;
    public PrimitiveTypes(
        boolean booleanT,
        byte byteT,
        short shortT,
        int intT,
        long longT,
        float floatT,
        double doubleT,
        String stringT,
        java.time.Instant dateT
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

    public boolean getBooleanT() { return booleanT; }
    public byte getByteT() { return byteT; }
    public short getShortT() { return shortT; }
    public int getIntT() { return intT; }
    public long getLongT() { return longT; }
    public float getFloatT() { return floatT; }
    public double getDoubleT() { return doubleT; }
    public String getStringT() { return stringT; }
    public java.time.Instant getDateT() { return dateT; }

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
