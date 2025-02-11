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
#import "TSTGlobalInterface.h"
#import "TSTSomethingNamespacedNamespacedInterface.h"

@interface InterfaceTests : XCTestCase
@end

@implementation InterfaceTests

- (void)testGlobalInterface {
    TSTSomethingNamespacedNamespacedRecord* result = [TSTGlobalInterface getNamespacedRecord];
    XCTAssertEqualObjects(result,
       [TSTSomethingNamespacedNamespacedRecord namespacedRecordWithA:
            [TSTGlobalRecord globalRecordWithA:
                    [TSTSomethingNamespacedOtherNamespacedRecord otherNamespacedRecordWithA:5]
            ]
        ]
    );
}

- (void)testNamespacedInterface {
    TSTGlobalRecord* result = [TSTSomethingNamespacedNamespacedInterface getGlobalRecord];
    XCTAssertEqualObjects(result,
       [TSTGlobalRecord globalRecordWithA:
               [TSTSomethingNamespacedOtherNamespacedRecord otherNamespacedRecordWithA:5]
       ]
    );
}

@end
