#import <XCTest/XCTest.h>
#import "Helper.h"
#import "Foo.h"

@interface RecordTests : XCTestCase
@end

@implementation RecordTests

- (void)testGetRecord {
    Foo* foo = [Foo fooWithBar:42];
    Foo* foo_result = [Helper getFoo:foo];
    XCTAssertEqual(foo_result.bar, 42, @"Returned Record does not match input");
}

- (void)testConstValue {
    XCTAssertEqual(FooBaz, 5, @"Unexpected constant value");
}

- (void)testDescription {
    Foo* foo = [Foo fooWithBar:42];
    XCTAssertEqualObjects([foo description], @"<Foo bar:42>", @"unexpected object description");
}

@end
