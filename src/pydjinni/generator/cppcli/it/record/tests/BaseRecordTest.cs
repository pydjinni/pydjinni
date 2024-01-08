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
    public class BaseRecordTest
    {

        [Test]
        public void TestCppBaseRecord()
        {
            var record = Helper.GetCppBaseRecord();
            Assert.That(record.Value, Is.EqualTo(42));
        }

        [Test]
        public void TestCsBaseRecord()
        {
            var record = new BaseRecord();
            var returned_record = Helper.GetHostBaseRecord(record);
            Assert.That(returned_record.Value, Is.EqualTo(42));
        }


    }
}
