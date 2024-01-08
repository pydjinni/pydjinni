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
using System.Globalization;
using System.Threading;
using Test.Record.CppCli;
using NUnit.Framework;
using System;

namespace Testing.Unit.Record
{
    [TestFixture]
    public class PrimitiveTypesTest
    {
        PrimitiveTypes record;

        [SetUp]
        [Test]
        public void Init()
        {
            Thread.CurrentThread.CurrentCulture = CultureInfo.CreateSpecificCulture("en-US");
            record = new PrimitiveTypes(true, 8, 16, 32, 64, 32.32f, 64.64, "test string", new DateTime(2023, 7, 1, 12, 8, 29));
        }

        [Test]
        public void TestPrimitiveTypes()
        {
            var returned_record = Helper.GetPrimitiveTypes(record);
            Assert.That(returned_record.BooleanT, Is.EqualTo(true));
            Assert.That(returned_record.ByteT, Is.EqualTo(8));
            Assert.That(returned_record.ShortT, Is.EqualTo(16));
            Assert.That(returned_record.IntT, Is.EqualTo(32));
            Assert.That(returned_record.LongT, Is.EqualTo(64));
            Assert.That(returned_record.FloatT, Is.GreaterThan(32));
            Assert.That(returned_record.FloatT, Is.LessThan(33));
            Assert.That(returned_record.DoubleT, Is.GreaterThan(64));
            Assert.That(returned_record.DoubleT, Is.LessThan(65));
            Assert.That(returned_record.StringT, Is.EqualTo("test string"));
            Assert.That(returned_record.DateT, Is.EqualTo(new DateTime(2023, 7, 1, 12, 8, 29)));
        }

        [Test]
        public void TestToString()
        {
            Assert.That(record.ToString(), Is.EqualTo("Test.Record.CppCli.PrimitiveTypes(BooleanT=True, ByteT=8, ShortT=16, IntT=32, LongT=64, FloatT=32.32, DoubleT=64.64, StringT=test string, DateT=7/1/2023 12:08:29 PM)"));
        }


    }
}
