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
using Test.Function.CppCli;
using NUnit.Framework;
using System;

namespace Testing.Unit.Function
{
    [TestFixture]
    public class FunctionTest
    {

        [Test]
        public void TestNamedFunction()
        {
            Helper.NamedFunction(input => input == 42);
        }

        [Test]
        public void TestAnonymousFunction()
        {
            Helper.AnonymousFunction(input => input == 42);
        }

        [Test]
        public void TestCppNamedFunction()
        {
            var function = Helper.CppNamedFunction();
            var result = function(42);
            Assert.That(result);
        }

        [Test]
        public void TestCppAnonymousFunction()
        {
            var function = Helper.CppAnonymousFunction();
            var result = function(42);
            Assert.That(result);
        }

        [Test]
        public void TestFunctionThrowingException()
        {
            var function = Helper.CppFunctionThrowingException();
            var exception = Assert.Throws<Exception>(() => function());
            Assert.That(exception.Message, Is.EqualTo("shit hit the fan"));
        }

    }
}
