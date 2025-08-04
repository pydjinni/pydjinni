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

#import <XCTest/XCTest.h>
#import "TSTCppProperties.h"

static void *TestPropertyKVOContext = &TestPropertyKVOContext;

@interface PropertiesTests : XCTestCase

@property (nonatomic, strong) TSTCppProperties * properties;
@property (nonatomic, strong) NSNumber* changedReadwriteProperty;
@property (nonatomic, strong) NSString* changedReadonlyProperty;
@property (nonatomic, strong) NSNumber* changedOptionalProperty;

@end

@implementation PropertiesTests

- (void)setUp {
    self.properties = [TSTCppProperties getInstance];
    self.changedReadwriteProperty = nil;
    self.changedReadonlyProperty = nil;
    self.changedOptionalProperty = nil;
}

- (void)testPropertySetter {
    self.properties.readwriteProperty = 42;    
    XCTAssertEqual(self.properties.readwriteProperty, 42);
}

- (void)testPropertyKVO {
    [self.properties addObserver:self
                      forKeyPath:@"readwriteProperty"
                         options:(NSKeyValueObservingOptionNew)
                         context:TestPropertyKVOContext];
    self.properties.readwriteProperty = 42;
    XCTAssertEqualObjects(self.changedReadwriteProperty, @42);
}

- (void)testReadonlyPropertyChangedThroughSideEffect {
    [self.properties addObserver:self
                      forKeyPath:@"readonlyProperty"
                         options:(NSKeyValueObservingOptionNew)
                         context:TestPropertyKVOContext];
    [self.properties changeReadonlyProperty];
    XCTAssertEqualObjects(self.properties.readonlyProperty, @"changed");
    XCTAssertEqualObjects(self.changedReadonlyProperty, @"changed");
}

- (void)testOptionalPropertyNonnullValue {
    [self.properties addObserver:self
                      forKeyPath:@"optionalProperty"
                         options:(NSKeyValueObservingOptionNew)
                         context:TestPropertyKVOContext];
    self.properties.optionalProperty = @42;
    XCTAssertEqualObjects(self.properties.optionalProperty, @42);
    XCTAssertEqualObjects(self.changedOptionalProperty, @42);
}

- (void)testOptionalPropertyNullValue {
    [self.properties addObserver:self
                      forKeyPath:@"optionalProperty"
                         options:(NSKeyValueObservingOptionNew)
                         context:TestPropertyKVOContext];
    self.properties.optionalProperty = nil;
    XCTAssertNil(self.properties.optionalProperty);
    XCTAssertEqualObjects(self.changedOptionalProperty, [NSNull null]);
}

- (void)observeValueForKeyPath:(NSString *)keyPath
                      ofObject:(id)object
                        change:(NSDictionary *)change
                       context:(void *)context {
    if (context == TestPropertyKVOContext) {
        if ([keyPath isEqualToString:@"readwriteProperty"]) {
            self.changedReadwriteProperty = change[NSKeyValueChangeNewKey];
        } else if ([keyPath isEqualToString:@"readonlyProperty"]) {
            self.changedReadonlyProperty = change[NSKeyValueChangeNewKey];
        } else if ([keyPath isEqualToString:@"optionalProperty"]) {
            self.changedOptionalProperty = change[NSKeyValueChangeNewKey];
        }
    }
}

@end
