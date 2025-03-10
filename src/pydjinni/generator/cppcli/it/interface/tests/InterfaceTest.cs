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

using Test.Interface.CppCli;
using NUnit.Framework;
using System;

namespace Testing.Unit.Interface
{
    [TestFixture]
    public class InterfaceTest
    {

        Calculator calculator;

        [SetUp]
        public void Init()
        {
            calculator = Calculator.GetInstance();
        }

        [Test]
        public void TestCalculator()
        {
            var result = calculator.Add(40, 2);
            Assert.That(result, Is.EqualTo(42));
        }

        [Test]
        public void TestPlatformImplementation()
        {
            var result = calculator.GetPlatformValue(new CsPlatformInterface());
            Assert.That(result, Is.EqualTo(5));
        }

        class CsPlatformInterface : PlatformInterface
        {
            public override sbyte GetValue() { return 5; }
        }

        [Test]
        public void TestMethodNoParametersNoReturn()
        {
            calculator.NoParametersNoReturn();
        }

        [Test]
        public void TestMethodThrowingException()
        {
            var exception = Assert.Throws<Exception>(() => calculator.ThrowingException());
            Assert.That(exception.Message, Is.EqualTo("shit hit the fan"));
        }

        [Test]
        public void TestNoParametersNoReturnCallback()
        {
            var callback = new NoParametersNoReturnCallbackImpl();
            calculator.NoParametersNoReturnCallback(callback);
            Assert.That(callback.callbackInvoked, Is.True);
        }

        class NoParametersNoReturnCallbackImpl : NoParametersNoReturnCallback
        {
            public bool callbackInvoked = false;
            public override void Invoke()
            {
                callbackInvoked = true;
            }
        }

        [Test]
        public void TestThrowingExceptionCallback()
        {
            var exception = Assert.Throws<Exception>(() => calculator.ThrowingCallback(new ThrowingCallbackImpl()));
            Assert.That(exception.Message, Is.EqualTo("exception from callback"));
        }

        class ThrowingCallbackImpl : ThrowingCallback
        {
            public override void Invoke()
            {
                throw new Exception("exception from callback");
            }
        }
    }
}
