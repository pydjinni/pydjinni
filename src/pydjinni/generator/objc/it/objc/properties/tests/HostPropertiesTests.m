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
#import "TSTHostProperties.h"
#import "TSTHostPropertyHelper.h"
#import "TSTReadwritePropertyData.h"
#import "TSTReadonlyPropertyData.h"
#import "TSTOptionalPropertyData.h"

static void *HostTestPropertyKVOContext = &HostTestPropertyKVOContext;

@interface HostPropertiesImpl : NSObject <TSTHostProperties>
@property (readwrite) int64_t readwriteProperty;
@property (nonnull) NSString* readonlyProperty;
@property (readwrite, nullable) NSNumber* optionalProperty;
@end

@implementation HostPropertiesImpl

- (instancetype)init {
    if (self = [super init]) {
        _readwriteProperty = 0;
        _readonlyProperty = @"initial";
        _optionalProperty = @0;
    }
    return self;
}

- (void)changeReadonlyProperty {
    self.readonlyProperty = @"changed";
}

@end

@interface HostPropertiesTests : XCTestCase

@property (nonatomic, strong) NSObject <TSTHostProperties>* hostProperties;
@property (nonatomic, strong) TSTHostPropertyHelper* helper;
@property (nonatomic, strong) NSNumber* observedValue;

@end

@implementation HostPropertiesTests

- (void)setUp {
    [super setUp];
    self.hostProperties = [[HostPropertiesImpl alloc] init];
    self.helper = [TSTHostPropertyHelper setup:self.hostProperties];
    self.observedValue = 0;
}

- (void)testChangingReadwriteHostProperty {
    self.hostProperties.readwriteProperty = 42;
    TSTReadwritePropertyData* result = [self.helper readwritePropertyData];
    XCTAssertEqual(result.changeCounter, 1);
    XCTAssertEqual(result.callbackValue, 42);
    XCTAssertEqual(result.readValue, 42);
}

- (void)testChangingReadonlyHostProperty {
    [self.hostProperties changeReadonlyProperty];
    TSTReadonlyPropertyData* result = [self.helper readonlyPropertyData];
    XCTAssertEqual(result.changeCounter, 1);
    XCTAssertEqualObjects(result.callbackValue, @"changed");
    XCTAssertEqualObjects(result.readValue, @"changed");
}

- (void)testChangingHostPropertyFromHelper {
    [self.hostProperties addObserver:self
                          forKeyPath:@"readwriteProperty"
                             options:(NSKeyValueObservingOptionNew)
                             context:HostTestPropertyKVOContext];
    [self.helper modifyHostReadwriteProperty];
    TSTReadwritePropertyData* result = [self.helper readwritePropertyData];
    XCTAssertEqual(self.hostProperties.readwriteProperty, 2);
    XCTAssertEqualObjects(self.observedValue, @2);
    XCTAssertEqual(result.changeCounter, 1);
    XCTAssertEqual(result.callbackValue, 2);
    XCTAssertEqual(result.readValue, 2);
    [self.hostProperties removeObserver:self forKeyPath:@"readwriteProperty"];
}

- (void)testChangingOptionalHostPropertyNonnull {
    self.hostProperties.optionalProperty = @42;
    TSTOptionalPropertyData* result = [self.helper optionalPropertyData];
    XCTAssertEqual(result.changeCounter, 1);
    XCTAssertEqualObjects(result.callbackValue, @42);
    XCTAssertEqualObjects(result.readValue, @42);
}

- (void)testChangingOptionalHostPropertyNil {
    self.hostProperties.optionalProperty = nil;
    TSTOptionalPropertyData* result = [self.helper optionalPropertyData];
    XCTAssertEqual(result.changeCounter, 1);
    XCTAssertNil(result.callbackValue);
    XCTAssertNil(result.readValue);
}

- (void)observeValueForKeyPath:(NSString *)keyPath
                      ofObject:(id)object
                        change:(NSDictionary *)change
                       context:(void *)context {
    if (context == HostTestPropertyKVOContext) {
        if ([keyPath isEqualToString:@"readwriteProperty"]) {
            self.observedValue = change[NSKeyValueChangeNewKey];
        }
    }
}

@end
