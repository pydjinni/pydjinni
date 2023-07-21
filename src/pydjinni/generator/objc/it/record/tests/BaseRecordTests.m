#import <XCTest/XCTest.h>
#import "Helper.h"
#import "BaseRecord.h"

@interface BaseRecordTests : XCTestCase
@end

@implementation BaseRecordTests

- (void)testCppBaseRecord {
    BaseRecord* record = [Helper getCppBaseRecord];

    XCTAssertEqual(record.value, 42);
}

- (void)testObjcBaseRecord {
    BaseRecord* record = [BaseRecord baseRecord];
    BaseRecord* returned_record = [Helper getHostBaseRecord:record];
    XCTAssertEqual(returned_record.value, 42);
}

@end
