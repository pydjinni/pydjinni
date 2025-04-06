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

using Test.ExportedTypes.CppCli;
using Test.ExternalTypes.CppCli;
using NUnit.Framework;

namespace Testing.Unit.ExternalTypes
{
    [TestFixture]
    public class ExternalTypesTest
    {
        [Test]
        public void TestFlags()
        {
            var result = MainInterface.UseExternalTypes(
                Test.ExportedTypes.CppCli.Foo.EnumType.A,
                FlagsType.A,
                new RecordType(4, 2, "foo"),
                () => true
            );
            Assert.That(result, Is.True);
        }

        [Test]
        public void TestExternalInterface()
        {
            var result = InterfaceType.SomeMethod();
            Assert.That(result, Is.True);
        }
    }
}
