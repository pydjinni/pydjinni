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

using System.Collections.Generic;
using Test.Properties.CppCli;
using NUnit.Framework;
using System;
using System.IO;

namespace Testing.Unit.Properties
{
    [TestFixture]
    public class PropertyTest
    {
        CppProperties properties;

        [SetUp]
        public void Init()
        {
            properties = CppProperties.GetInstance();
        }

        [Test]
        public void TestPropertySetter()
        {
            properties.ReadwriteProperty = 42;
            Assert.That(properties.ReadwriteProperty, Is.EqualTo(42));
        }

        [Test]
        public void testNotifyPropertyChanged()
        {
            long notifiedNewValue = 0;
            properties.PropertyChanged += (sender, args) =>
            {
                if (args.PropertyName == "ReadwriteProperty")
                {
                    notifiedNewValue = properties.ReadwriteProperty;
                }

            };
            properties.ReadwriteProperty = 42;
            Assert.That(notifiedNewValue, Is.EqualTo(42));
        }

        [Test]
        public void TestReadonlyPropertyChangedThroughSideEffect()
        {
            string notifiedNewValue = "uncalled";
            properties.PropertyChanged += (sender, args) =>
            {
                if (args.PropertyName == "ReadonlyProperty")
                {
                    notifiedNewValue = properties.ReadonlyProperty;
                }
            };
            properties.ChangeReadonlyProperty();
            Assert.That(properties.ReadonlyProperty, Is.EqualTo("changed"));
            Assert.That(notifiedNewValue, Is.EqualTo("changed"));
        }

        [Test]
        public void TestOptionalPropertyNonnullValue()
        {
            long? notifiedNewValue = 0;
            properties.PropertyChanged += (sender, args) =>
            {
                if (args.PropertyName == "OptionalProperty")
                {
                    notifiedNewValue = properties.OptionalProperty;
                }
            };
            properties.OptionalProperty = 42;
            Assert.That(properties.OptionalProperty, Is.EqualTo(42));
            Assert.That(notifiedNewValue, Is.EqualTo(42));
        }

        [Test]
        public void TestOptionalPropertyNullValue()
        {
            long? notifiedNewValue = 0;
            properties.PropertyChanged += (sender, args) =>
            {
                if (args.PropertyName == "OptionalProperty")
                {
                    notifiedNewValue = properties.OptionalProperty;
                }
            };
            properties.OptionalProperty = null;
            Assert.That(properties.OptionalProperty, Is.EqualTo(null));
            Assert.That(notifiedNewValue, Is.EqualTo(null));
        }
    }
}
