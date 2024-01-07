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
using Test.Record.CppCli;
using NUnit.Framework;
using System;

namespace Testing.Unit.Record
{
    [TestFixture]
    public class OptionalTypesTest
    {

        OptionalTypes record;

        [SetUp]
        public void Init()
        {
            record = new OptionalTypes(42, "optional");
        }

        [Test]
        public void TestCsBaseRecord()
        {
            var returnedRecord = Helper.GetOptionalTypes(record);
            Assert.That(returnedRecord.IntOptional, Is.EqualTo(42));
            Assert.That(
                returnedRecord.GetType().GetProperty("IntOptional").PropertyType.GetGenericTypeDefinition(),
                Is.EqualTo(typeof(Nullable<>))
            );
            Assert.That(returnedRecord.StringOptional, Is.EqualTo("optional"));
        }

        [Test]
        public void TestToString()
        {
            Assert.That(record.ToString(), Is.EqualTo("Test.Record.CppCli.OptionalTypes(IntOptional=42, StringOptional=optional)"));
        }


    }
}
