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
#import "TSTOptionalInterface.h"

@interface OptionalInterfaceTests : XCTestCase

@property (nonatomic, strong) TSTOptionalInterface * instance;

@end

@implementation OptionalInterfaceTests

- (void)setUp {
    self.instance = [TSTOptionalInterface getInstance];
}

- (void)testNullInterface {
    TSTOptionalInterface* nilInstance = [TSTOptionalInterface getNullInstance];
    XCTAssertNil(nilInstance);
}

- (void)testOptionalParameters {
    NSString* result = [self.instance optionalParameter:@"some optional string"];
    XCTAssertNotNil(result);
    XCTAssertEqualObjects(result, @"some optional string");
}

- (void)testOptionalNullParameter {
    NSString* result = [self.instance optionalNullParameter:nil];
    XCTAssertNil(result);
}

@end
