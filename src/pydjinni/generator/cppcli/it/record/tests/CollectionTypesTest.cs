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
    public class CollectionTypesTest
    {

        CollectionTypes record;

        [SetUp]
        public void Init()
        {
            record = new CollectionTypes(
                new List<int>() {0, 1},
                new List<string>() {"foo", "bar"},
                new HashSet<int>() {0, 1},
                new HashSet<string>() {"foo", "bar"},
                new Dictionary<int, int>() {{0, 1}},
                new Dictionary<string, string>() {{"foo", "bar"}}
            );
        }

        [Test]
        public void TestCollectionTypes()
        {
            var returnedRecord = Helper.GetCollectionTypes(record);
            Assert.That(returnedRecord.IntList.Count, Is.EqualTo(2));
            Assert.That(returnedRecord.IntList[0], Is.EqualTo(0));
            Assert.That(returnedRecord.IntList[1], Is.EqualTo(1));

            Assert.That(returnedRecord.StringList.Count, Is.EqualTo(2));
            Assert.That(returnedRecord.StringList[0], Is.EqualTo("foo"));
            Assert.That(returnedRecord.StringList[1], Is.EqualTo("bar"));

            Assert.That(returnedRecord.IntSet.Count, Is.EqualTo(2));
            Assert.That(returnedRecord.IntSet.Contains(0));
            Assert.That(returnedRecord.IntSet.Contains(1));

            Assert.That(returnedRecord.StringSet.Count, Is.EqualTo(2));
            Assert.That(returnedRecord.StringSet.Contains("foo"));
            Assert.That(returnedRecord.StringSet.Contains("bar"));

            Assert.That(returnedRecord.IntIntMap.Count, Is.EqualTo(1));
            Assert.That(returnedRecord.IntIntMap[0], Is.EqualTo(1));

            Assert.That(returnedRecord.StringStringMap.Count, Is.EqualTo(1));
            Assert.That(returnedRecord.StringStringMap["foo"], Is.EqualTo("bar"));
        }

        [Test]
        public void TestToString()
        {
            Assert.That(record.ToString(), Is.EqualTo("Test.Record.CppCli.CollectionTypes(IntList=System.Collections.Generic.List`1[System.Int32], StringList=System.Collections.Generic.List`1[System.String], IntSet=System.Collections.Generic.HashSet`1[System.Int32], StringSet=System.Collections.Generic.HashSet`1[System.String], IntIntMap=System.Collections.Generic.Dictionary`2[System.Int32,System.Int32], StringStringMap=System.Collections.Generic.Dictionary`2[System.String,System.String])"));
        }
    }
}
