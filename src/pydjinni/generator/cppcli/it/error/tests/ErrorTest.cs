// Copyright 2024 jothepro
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

using System.Collections.Generic;
using Test.Error.CppCli;
using NUnit.Framework;
using System;
using System.Threading.Tasks;

namespace Testing.Unit.Error
{
    [TestFixture]
    public class ErrorTest
    {
        [Test]
        public void TestThrowing()
        {
            var exception = Assert.Throws<FooError.SomethingWrong>(() => Helper.ThrowingError());
            Assert.That(exception.Message, Is.EqualTo("some error"));
        }

        [Test]
        public void TestThrowingWithParameter()
        {
            var exception = Assert.Throws<FooError.SomethingWithParameters>(() => Helper.ThrowingWithParameters());
            Assert.That(exception.Message, Is.EqualTo("some error message"));
            Assert.That(exception.Parameter, Is.EqualTo(42));
            
        }

        [Test]
        public void TestThrowingAsync()
        {
            var exception = Assert.ThrowsAsync<FooError.SomethingWrong>(async () => await Helper.ThrowingAsync());
            Assert.That(exception.Message, Is.EqualTo("something wrong in coroutine"));
        }

        class ThrowingCallbackImpl : ThrowingCallback
        {
            public bool callbackInvoked = false;
                
            public override void ThrowingError()
            {
                callbackInvoked = true;
                throw new FooError.SomethingWrong("some callback error");
            }
        }

        [Test]
        public void TestThrowingCallback()
        {
            var callback = new ThrowingCallbackImpl();
            var exception = Assert.Throws<FooError.SomethingWrong>(() => Helper.ThrowingCallbackError(callback));
            Assert.That(callback.callbackInvoked, Is.True);
            Assert.That(exception.Message, Is.EqualTo("some callback error"));
        }

        class AsyncThrowingCallbackImpl : AsyncThrowingCallback
        {
            public bool callbackInvoked = false;

            public override async Task ThrowingError()
            {
                await Task.Delay(1);
                callbackInvoked = true;
                throw new FooError.SomethingWrong("some async callback error");
            }
        }

        [Test]
        public void TestThrowingAsyncCallback()
        {
            var callback = new AsyncThrowingCallbackImpl();
            var exception = Assert.ThrowsAsync<FooError.SomethingWrong>(async () => await Helper.ThrowingAsyncCallbackError(callback));
            Assert.That(callback.callbackInvoked, Is.True);
            Assert.That(exception.Message, Is.EqualTo("some async callback error"));
        }
    }
}
