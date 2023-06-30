#import <XCTest/XCTest.h>
#import "Helper.h"

@interface CollectionTypesTests : XCTestCase

@property (nonatomic, strong) CollectionTypes * record;

@end

@implementation CollectionTypesTests

- (void)setUp {
    self.record = [CollectionTypes
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
    CollectionTypes* returned_record = [Helper getCollectionTypes:self.record];

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
    XCTAssertEqualObjects([self.record description], @"<CollectionTypes intList:(\n"
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
