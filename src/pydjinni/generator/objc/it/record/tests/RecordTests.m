#import <XCTest/XCTest.h>
#import "Helper.h"
#import "Foo.h"

@interface RecordTests : XCTestCase
@end

@implementation RecordTests

- (void)testGetRecord {
    Foo* foo = [Foo fooWithBooleanT:YES byteT: 8 shortT: 16 intT: 32 longT: 64 floatT: 32.32f doubleT: 64.64 stringT: @"test string"];
    Foo* foo_result = [Helper getFoo:foo];
    XCTAssertEqual(foo_result.booleanT, YES);
    XCTAssertEqual(foo_result.byteT, 8);
    XCTAssertEqual(foo_result.shortT, 16);
    XCTAssertEqual(foo_result.intT, 32);
    XCTAssertEqual(foo_result.longT, 64);
    XCTAssertGreaterThan(foo_result.floatT, 32);
    XCTAssertLessThan(foo_result.floatT, 33);
    XCTAssertGreaterThan(foo_result.doubleT, 64);
    XCTAssertLessThan(foo_result.doubleT, 65);
    XCTAssertEqualObjects(foo_result.stringT, @"test string");
}

- (void)testConstValue {
    XCTAssertEqual(FooBooleanc, YES);
    XCTAssertEqual(FooBytec, 8);
    XCTAssertEqual(FooShortc, 16);
    XCTAssertEqual(FooIntc, 32);
    XCTAssertEqual(FooLongc, 64);
    XCTAssertGreaterThan(FooFloatc, 32);
    XCTAssertLessThan(FooFloatc, 33);
    XCTAssertGreaterThan(FooDoublec, 64);
    XCTAssertLessThan(FooDoublec, 65);
}

- (void)testDescription {
    Foo* foo = [Foo fooWithBooleanT:YES byteT: 8 shortT: 16 intT: 32 longT: 64 floatT: 32.32f doubleT: 64.64 stringT: @"test string"];
    XCTAssertEqualObjects([foo description], @"<Foo booleanT:YES byteT:8 shortT:16 intT:32 longT:64 floatT:32.32 doubleT:64.64 stringT:test string>", @"unexpected object description");
}

@end
