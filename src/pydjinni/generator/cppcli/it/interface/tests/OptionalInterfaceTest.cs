// Copyright 2025 jothepro
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

namespace Testing.Unit.Interface
{
    [TestFixture]
    public class OptionalInterfaceTest
    {
        OptionalInterface instance;

        [SetUp]
        public void Init()
        {
            instance = OptionalInterface.GetInstance();
        }

        [Test]
        public void TestNullInterface()
        {
            var result = OptionalInterface.GetNullInstance();
            Assert.That(result, Is.Null);
        }

        [Test]
        public void TestOptionalParameter()
        {
            var result = instance.OptionalParameter("some optional string");
            Assert.That(result, Is.Not.Null);
            Assert.That(result, Is.EqualTo("some optional string"));
        }

        [Test]
        public void TestOptionalNullParameter()
        {
            var result = instance.OptionalNullParameter(null);
            Assert.That(result, Is.Null);
        }
    }
}
