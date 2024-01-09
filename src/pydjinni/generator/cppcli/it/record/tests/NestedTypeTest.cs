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
    public class NestedTypeTest
    {
        ParentType record;

        [SetUp]
        public void Init()
        {
            record = new ParentType(new NestedType(42, new List<List<int>>() {new List<int>() {1, 2}, new List<int>() {3, 4}}));
        }

        [Test]
        public void TestNestedType()
        {
            var returned_record = Helper.GetNestedType(record);
            Assert.That(returned_record.Nested.A, Is.EqualTo(42));
        }

        [Test]
        public void TestToString()
        {
            Assert.That(record.ToString(), Is.EqualTo("Test.Record.CppCli.ParentType(Nested=Test.Record.CppCli.NestedType(A=42, B=System.Collections.Generic.List`1[System.Collections.Generic.List`1[System.Int32]]))"));
        }


    }
}
