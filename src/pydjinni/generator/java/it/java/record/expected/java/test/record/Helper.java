// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
package test.record;

public abstract class Helper {
    static {
        test.record.pydjinni.NativeRecordTestJniLoader.loadLibrary();
    }
    public static test.record.PrimitiveTypes getPrimitiveTypes(test.record.PrimitiveTypes recordType) {
        return CppProxy.getPrimitiveTypes(recordType);
    };
    public static test.record.CollectionTypes getCollectionTypes(test.record.CollectionTypes recordType) {
        return CppProxy.getCollectionTypes(recordType);
    };
    public static test.record.OptionalTypes getOptionalTypes(test.record.OptionalTypes recordType) {
        return CppProxy.getOptionalTypes(recordType);
    };
    public static test.record.BinaryTypes getBinaryTypes(test.record.BinaryTypes recordType) {
        return CppProxy.getBinaryTypes(recordType);
    };
    public static test.record.BaseRecord getCppBaseRecord() {
        return CppProxy.getCppBaseRecord();
    };
    public static test.record.BaseRecord getHostBaseRecord(test.record.BaseRecord recordType) {
        return CppProxy.getHostBaseRecord(recordType);
    };
    public static test.record.ParentType getNestedType(test.record.ParentType parent) {
        return CppProxy.getNestedType(parent);
    };
    private static final class CppProxy extends Helper {
        private final long nativeRef;

        static class CleanupTask implements Runnable {
            private final long nativeRef;
            CleanupTask(long nativeRef) {
                this.nativeRef = nativeRef;
            }

            @Override
            public void run() {
                nativeDestroy(this.nativeRef);
            }

            private native void nativeDestroy(long nativeRef);
        }

        private CppProxy(long nativeRef) {
            if (nativeRef == 0) throw new RuntimeException("nativeRef is zero");
            this.nativeRef = nativeRef;
            test.record.pydjinni.NativeCleaner.register(this, new CleanupTask(nativeRef));
        }

        public static native test.record.PrimitiveTypes getPrimitiveTypes(test.record.PrimitiveTypes recordType);
        public static native test.record.CollectionTypes getCollectionTypes(test.record.CollectionTypes recordType);
        public static native test.record.OptionalTypes getOptionalTypes(test.record.OptionalTypes recordType);
        public static native test.record.BinaryTypes getBinaryTypes(test.record.BinaryTypes recordType);
        public static native test.record.BaseRecord getCppBaseRecord();
        public static native test.record.BaseRecord getHostBaseRecord(test.record.BaseRecord recordType);
        public static native test.record.ParentType getNestedType(test.record.ParentType parent);
    }
}
