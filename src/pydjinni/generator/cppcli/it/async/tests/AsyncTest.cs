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
using System.Threading.Tasks;
using Test.Async.CppCli;
using NUnit.Framework;
using System;

namespace Testing.Unit.Async
{
    [TestFixture]
    public class AsyncTest
    {
        Asynchronous asynchronous;

        [SetUp]
        public async Task Init()
        {
            asynchronous = await Asynchronous.GetInstance();
        }

        [Test]
        public async Task TestAsyncMethodCall()
        {
            var result = await asynchronous.Add(40, 2);
            Assert.That(result, Is.EqualTo(42));
        }

        [Test]
        public async Task TestAsyncCallback()
        {
            var result = await asynchronous.MultiplyCallback(new MultiplyCallbackImpl());
            Assert.That(result, Is.EqualTo(42));
        }

        class MultiplyCallbackImpl : MultiplyCallback
        {
            public async override Task<int> Invoke(int a, int b)
            {
                await Task.Delay(1);
                return a * b;
            }
        }

        [Test]
        public async Task TestAsyncNoParametersNoReturnCallback()
        {
            var callback = new NoParametersNoReturnCallbackImpl();
            await asynchronous.NoParametersNoReturnCallback(callback);
            Assert.That(callback.CallbackInvoked, Is.True);
        }

        class NoParametersNoReturnCallbackImpl : NoParametersNoReturnCallback
        {
            public bool CallbackInvoked = false;
            public override async Task Invoke()
            {
                await Task.Delay(1);
                CallbackInvoked = true;
            }
        }

        [Test]
        public void TestAsyncThrowingException()
        {
            var exception = Assert.ThrowsAsync<Exception>(async () => await asynchronous.ThrowingException());
            Assert.That(exception.Message, Is.EqualTo("asynchronous runtime error"));
        }

        [Test]
        public void TestAsyncThrowingExceptionCallback()
        {
            var exception = Assert.ThrowsAsync<Exception>(async () => await asynchronous.ThrowingCallback(new ThrowingCallbackImpl()));
            Assert.That(exception.Message, Is.EqualTo("asynchronous runtime error from callback"));
        }

        class ThrowingCallbackImpl : ThrowingCallback
        {
            public bool CallbackInvoked = false;
            public override async Task Invoke()
            {
                await Task.Delay(1);
                CallbackInvoked = true;
                throw new Exception("asynchronous runtime error from callback");
            }
        }
    }
}
