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
using Test.Enum.CppCli;
using NUnit.Framework;

namespace Testing.Unit.Enum
{
    [TestFixture]
    public class EnumTest
    {
        [Test]
        public void TestEnum()
        {
            var exampleEnum = Helper.GetEnum(ExampleEnum.A);
            Assert.That(exampleEnum, Is.EqualTo(ExampleEnum.A));
        }
    }
}
