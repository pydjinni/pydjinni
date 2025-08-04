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

using NUnit.Framework;
using Test.Properties.CppCli;

namespace Testing.Unit.Properties
{
    [TestFixture]
    public class HostPropertyTest
    {
        public class HostPropertiesImpl : HostProperties
        {
            public HostPropertiesImpl()
            {
                ReadwriteProperty = 0;
                ReadonlyProperty = "";
                OptionalProperty = 0;
            }
            override public void ChangeReadonlyProperty()
            {
                ReadonlyProperty = "changed";
            }
        }

        HostProperties hostProperties;
        HostPropertyHelper helper;

        [SetUp]
        public void Init()
        {
            hostProperties = new HostPropertiesImpl();
            helper = HostPropertyHelper.Setup(hostProperties);
        }

        [Test]
        public void TestChangingReadwriteHostProperty()
        {
            hostProperties.ReadwriteProperty = 42;
            var result = helper.ReadwritePropertyData();
            Assert.That(result.ChangeCounter, Is.EqualTo(1));
            Assert.That(result.CallbackValue, Is.EqualTo(42));
            Assert.That(result.ReadValue, Is.EqualTo(42));
        }

        [Test]
        public void TestChangingReadonlyHostProperty()
        {
            hostProperties.ChangeReadonlyProperty();
            var result = helper.ReadonlyPropertyData();
            Assert.That(result.ChangeCounter, Is.EqualTo(1));
            Assert.That(result.CallbackValue, Is.EqualTo("changed"));
            Assert.That(result.ReadValue, Is.EqualTo("changed"));
        }

        [Test]
        public void TestChangingHostPropertyFromHelper()
        {
            long observedValue = 0;
            hostProperties.PropertyChanged += (sender, args) =>
            {
                if (args.PropertyName == "ReadwriteProperty")
                {
                    observedValue = hostProperties.ReadwriteProperty;
                }
            };
            helper.ModifyHostReadwriteProperty();
            var result = helper.ReadwritePropertyData();
            Assert.That(hostProperties.ReadwriteProperty, Is.EqualTo(2));
            Assert.That(observedValue, Is.EqualTo(2));
            Assert.That(result.ChangeCounter, Is.EqualTo(1));
            Assert.That(result.CallbackValue, Is.EqualTo(2));
            Assert.That(result.ReadValue, Is.EqualTo(2));
        }

        [Test]
        public void TestChangingOptionalHostPropertyNonnull()
        {
            hostProperties.OptionalProperty = 42;
            var result = helper.OptionalPropertyData();
            Assert.That(result.ChangeCounter, Is.EqualTo(1));
            Assert.That(result.CallbackValue, Is.EqualTo(42));
            Assert.That(result.ReadValue, Is.EqualTo(42));
        }

        [Test]
        public void TestChangingOptionalHostPropertyNil()
        {
            hostProperties.OptionalProperty = null;
            var result = helper.OptionalPropertyData();
            Assert.That(result.ChangeCounter, Is.EqualTo(1));
            Assert.That(result.CallbackValue, Is.EqualTo(null));
            Assert.That(result.ReadValue, Is.EqualTo(null));
        }
    }
}
