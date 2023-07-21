#import <XCTest/XCTest.h>
#import "Helper.h"

@interface BaseRecordTests : XCTestCase
@end

@implementation BaseRecordTests

- (void)testCppBaseRecord {
    BaseRecord* record = [Helper getCppBaseRecord];

    XCTAssertEqual(record.value, 42);
}

@end
