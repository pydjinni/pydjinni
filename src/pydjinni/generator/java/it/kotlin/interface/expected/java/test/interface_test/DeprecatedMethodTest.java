// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'interface.pydjinni'
package test.interface_test;

public abstract class DeprecatedMethodTest {
    /**
     * @deprecated this method is deprecated but the type is not
     */
    @Deprecated
    public abstract @org.jetbrains.annotations.NotNull boolean deprecatedTestMethod();
    private static final class CppProxy extends DeprecatedMethodTest {
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

        @Override
        public @org.jetbrains.annotations.NotNull boolean deprecatedTestMethod() {
            return native_deprecatedTestMethod(this.nativeRef );
        }
        private native @org.jetbrains.annotations.NotNull boolean native_deprecatedTestMethod(long _nativeRef);
    }
}
