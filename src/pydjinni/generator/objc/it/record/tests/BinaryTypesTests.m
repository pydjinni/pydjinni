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
#import "TSTHelper.h"

@interface BinaryTypesTests : XCTestCase

@property (nonatomic, strong) TSTBinaryTypes * record;

@end

@implementation BinaryTypesTests

- (void)setUp {
    const unsigned char byteArray[] = {0x8F};
    self.record = [TSTBinaryTypes binaryTypesWithBinaryT: [NSData dataWithBytes:byteArray length:sizeof(byteArray)]
                                          binaryOptional: [NSData dataWithBytes:byteArray length:sizeof(byteArray)]];
}

- (void)testBinaryTypes {
    TSTBinaryTypes* returned_record = [TSTHelper getBinaryTypes:self.record];

    XCTAssertEqual(returned_record.binaryT.length, 1);
    XCTAssertEqual(returned_record.binaryOptional.length, 1);
}

@end
