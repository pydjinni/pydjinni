// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'interface.pydjinni'
package test.interface_test;

public abstract class Calculator {
    static {
        test.interface_test.pydjinni.NativeInterfaceTestKotlinJniLoader.loadLibrary();
    }
    public static test.interface_test.@org.jetbrains.annotations.NotNull Calculator getInstance() {
        return CppProxy.getInstance();
    };
    /**
     * adds up two values
     * 
     * @param a the first value
     * @param b the second value
     * @return the sum of both values
     */
    public abstract @org.jetbrains.annotations.NotNull byte add(@org.jetbrains.annotations.NotNull byte a, @org.jetbrains.annotations.NotNull byte b);
    public abstract @org.jetbrains.annotations.NotNull byte getPlatformValue(test.interface_test.@org.jetbrains.annotations.NotNull PlatformInterface platform);
    public abstract void noParametersNoReturn();
    public abstract void throwingException();
    public abstract void noParametersNoReturnCallback(test.interface_test.@org.jetbrains.annotations.NotNull NoParametersNoReturnCallback callback);
    public abstract void throwingCallback(test.interface_test.@org.jetbrains.annotations.NotNull ThrowingCallback callback);
    private static final class CppProxy extends Calculator {
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
            test.interface_test.pydjinni.NativeCleaner.register(this, new CleanupTask(nativeRef));
        }

        public static native test.interface_test.@org.jetbrains.annotations.NotNull Calculator getInstance();
        @Override
        public @org.jetbrains.annotations.NotNull byte add(@org.jetbrains.annotations.NotNull byte a, @org.jetbrains.annotations.NotNull byte b) {
            return native_add(this.nativeRef , a, b);
        }
        private native @org.jetbrains.annotations.NotNull byte native_add(long _nativeRef, @org.jetbrains.annotations.NotNull byte a, @org.jetbrains.annotations.NotNull byte b);
        @Override
        public @org.jetbrains.annotations.NotNull byte getPlatformValue(test.interface_test.@org.jetbrains.annotations.NotNull PlatformInterface platform) {
            return native_getPlatformValue(this.nativeRef , platform);
        }
        private native @org.jetbrains.annotations.NotNull byte native_getPlatformValue(long _nativeRef, test.interface_test.@org.jetbrains.annotations.NotNull PlatformInterface platform);
        @Override
        public void noParametersNoReturn() {
            native_noParametersNoReturn(this.nativeRef );
        }
        private native void native_noParametersNoReturn(long _nativeRef);
        @Override
        public void throwingException() {
            native_throwingException(this.nativeRef );
        }
        private native void native_throwingException(long _nativeRef);
        @Override
        public void noParametersNoReturnCallback(test.interface_test.@org.jetbrains.annotations.NotNull NoParametersNoReturnCallback callback) {
            native_noParametersNoReturnCallback(this.nativeRef , callback);
        }
        private native void native_noParametersNoReturnCallback(long _nativeRef, test.interface_test.@org.jetbrains.annotations.NotNull NoParametersNoReturnCallback callback);
        @Override
        public void throwingCallback(test.interface_test.@org.jetbrains.annotations.NotNull ThrowingCallback callback) {
            native_throwingCallback(this.nativeRef , callback);
        }
        private native void native_throwingCallback(long _nativeRef, test.interface_test.@org.jetbrains.annotations.NotNull ThrowingCallback callback);
    }
}
