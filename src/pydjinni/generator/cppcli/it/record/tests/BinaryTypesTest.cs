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
    public class BinaryTypesTest
    {

        BinaryTypes record;
        Byte[] binaryData = new Byte[] { 0x8F };

        [SetUp]
        public void Init()
        {
            record = new BinaryTypes(binaryData, binaryData);
        }

        [Test]
        public void TestBinaryTypes()
        {
            var returnedRecord = Helper.GetBinaryTypes(record);

            Assert.That(returnedRecord.BinaryT, Is.EqualTo(binaryData).AsCollection);
            Assert.That(returnedRecord.BinaryOptional, Is.EqualTo(binaryData).AsCollection);
        }
    }
}
