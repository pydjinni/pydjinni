/*#
Copyright 2024 jothepro

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
#*/
package {{ package }};

import java.util.concurrent.ForkJoinPool;

import static java.util.concurrent.ForkJoinPool.commonPool;

class NativeRunnable implements Runnable {
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

    private NativeRunnable(long nativeRef) {
        if (nativeRef == 0) throw new RuntimeException("nativeRef is zero");
        this.nativeRef = nativeRef;
        {{ native_cleaner.package }}.{{ native_cleaner.name }}.register(this, new CleanupTask(nativeRef));
    }

    @Override
    public void run() {
        nativeRun(this.nativeRef);
    }

    private native void nativeRun(long _nativeRef);
}

