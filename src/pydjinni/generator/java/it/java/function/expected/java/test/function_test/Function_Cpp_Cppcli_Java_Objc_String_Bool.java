// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'function.pydjinni'
package test.function_test;

@FunctionalInterface
public interface Function_Cpp_Cppcli_Java_Objc_String_Bool {
    boolean invoke(String param);
}

final class Function_Cpp_Cppcli_Java_Objc_String_BoolCppProxy implements Function_Cpp_Cppcli_Java_Objc_String_Bool {
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

    private Function_Cpp_Cppcli_Java_Objc_String_BoolCppProxy(long nativeRef)
    {
        if (nativeRef == 0) throw new RuntimeException("nativeRef is zero");
        this.nativeRef = nativeRef;
        test.function_test.pydjinni.NativeCleaner.register(this, new CleanupTask(nativeRef));
    }

    @Override
    public boolean invoke(String param) {
        return nativeInvoke(this.nativeRef, param);
    }
    private native boolean nativeInvoke(long _nativeRef, String param);
}
