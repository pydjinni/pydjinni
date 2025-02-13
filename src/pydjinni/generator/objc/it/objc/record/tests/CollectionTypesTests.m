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

@interface CollectionTypesTests : XCTestCase

@property (nonatomic, strong) TSTCollectionTypes * record;

@end

@implementation CollectionTypesTests

- (void)setUp {
    self.record = [TSTCollectionTypes
            collectionTypesWithIntList:@[@0, @1]
                            stringList:@[@"foo", @"bar"]
                                intSet:[NSSet setWithObjects: @0, @1, nil]
                             stringSet:[NSSet setWithObjects: @"foo", @"bar", nil]
                             intIntMap:[NSDictionary dictionaryWithObjects:@[@1]
                                                                    forKeys:@[@0]]
                       stringStringMap:[NSDictionary dictionaryWithObjects:@[@"bar"]
                                                                   forKeys:@[@"foo"]]
    ];
}

- (void)testCollectionTypes {
    TSTCollectionTypes* returned_record = [TSTHelper getCollectionTypes:self.record];

    XCTAssertEqual(returned_record.intList.count, 2);
    XCTAssertEqualObjects([returned_record.intList objectAtIndex:0], @0);
    XCTAssertEqualObjects([returned_record.intList objectAtIndex:1], @1);

    XCTAssertEqual(returned_record.stringList.count, 2);
    XCTAssertEqualObjects([returned_record.stringList objectAtIndex:0], @"foo");
    XCTAssertEqualObjects([returned_record.stringList objectAtIndex:1], @"bar");

    XCTAssertEqual(returned_record.intSet.count, 2);
    XCTAssertTrue([returned_record.intSet containsObject:@0]);
    XCTAssertTrue([returned_record.intSet containsObject:@1]);

    XCTAssertEqual(returned_record.stringSet.count, 2);
    XCTAssertTrue([returned_record.stringSet containsObject:@"foo"]);
    XCTAssertTrue([returned_record.stringSet containsObject:@"bar"]);

    XCTAssertEqual(returned_record.intIntMap.count, 1);
    XCTAssertEqualObjects([returned_record.intIntMap objectForKey:@0], @1);

    XCTAssertEqual(returned_record.stringStringMap.count, 1);
    XCTAssertEqualObjects([returned_record.stringStringMap objectForKey:@"foo"], @"bar");
}

- (void)testDescription {
    XCTAssertEqualObjects([self.record description], @"<TSTCollectionTypes intList:(\n"
                                                     @"    0,\n"
                                                     @"    1\n"
                                                     @") stringList:(\n"
                                                     @"    foo,\n"
                                                     @"    bar\n"
                                                     @") intSet:{(\n"
                                                     @"    0,\n"
                                                     @"    1\n"
                                                     @")} stringSet:{(\n"
                                                     @"    foo,\n"
                                                     @"    bar\n"
                                                     @")} intIntMap:{\n"
                                                     @"    0 = 1;\n"
                                                     @"} stringStringMap:{\n"
                                                     @"    foo = bar;\n"
                                                     @"}>");
}

@end
