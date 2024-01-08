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
using Test.Flags.CppCli;
using NUnit.Framework;

namespace Testing.Unit.Flags
{
    [TestFixture]
    public class FlagsTest
    {
        [Test]
        public void TestFlags()
        {
            var exampleFlags = Helper.GetFlag(ExampleFlags.A);
            Assert.That(exampleFlags, Is.EqualTo(ExampleFlags.A));
        }

        [Test]
        public void TestAllFlags()
        {
            var exampleFlags = Helper.GetAllFlag(ExampleFlags.All);
            Assert.That(exampleFlags, Is.EqualTo(ExampleFlags.All));
        }

        [Test]
        public void TestNoneFlags()
        {
            var exampleFlags = Helper.GetNoneFlag(ExampleFlags.None);
            Assert.That(exampleFlags, Is.EqualTo(ExampleFlags.None));
        }
    }
}
