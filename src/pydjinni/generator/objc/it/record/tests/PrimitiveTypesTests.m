// Copyright 2023 jothepro
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
#import "Helper.h"

@interface PrimitiveTypesTests : XCTestCase

@property (nonatomic, strong) PrimitiveTypes * record;

@end

@implementation PrimitiveTypesTests

- (void)setUp {
    self.record = [PrimitiveTypes primitiveTypesWithBooleanT:YES
                                                       byteT:8
                                                      shortT:16
                                                        intT:32
                                                       longT:64
                                                      floatT:32.32f
                                                     doubleT:64.64
                                                     stringT:@"test string"
                                                       dateT:[NSDate dateWithTimeIntervalSince1970:1688213309]];
}

- (void)testPrimitiveTypes {
    PrimitiveTypes* returned_record = [Helper getPrimitiveTypes:self.record];

    XCTAssertEqual(returned_record.booleanT, YES);
    XCTAssertEqual(returned_record.byteT, 8);
    XCTAssertEqual(returned_record.shortT, 16);
    XCTAssertEqual(returned_record.intT, 32);
    XCTAssertEqual(returned_record.longT, 64);
    XCTAssertGreaterThan(returned_record.floatT, 32);
    XCTAssertLessThan(returned_record.floatT, 33);
    XCTAssertGreaterThan(returned_record.doubleT, 64);
    XCTAssertLessThan(returned_record.doubleT, 65);
    XCTAssertEqualObjects(returned_record.stringT, @"test string");
    XCTAssertEqualObjects(returned_record.dateT, [NSDate dateWithTimeIntervalSince1970:1688213309]);
}

- (void)testPrimitiveTypesEqual {
    PrimitiveTypes* returned_record = [Helper getPrimitiveTypes:self.record];
    XCTAssertEqualObjects(returned_record, self.record);
}

- (void)testDescription {
    XCTAssertEqualObjects([self.record description], @"<PrimitiveTypes booleanT:YES byteT:8 shortT:16 intT:32 longT:64 floatT:32.32 doubleT:64.64 stringT:test string dateT:2023-07-01 12:08:29 +0000>");
}

@end
