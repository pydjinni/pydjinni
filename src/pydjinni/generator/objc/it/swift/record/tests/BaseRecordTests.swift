import XCTest
import RecordTestSwift

class BaseRecordTests: XCTestCase {

    func testCppBaseRecord() {
        let record = Helper.getCppBaseRecord()
        XCTAssertEqual(record.value, 42)
    }

    func testObjcBaseRecord() {
        let record = BaseRecord()
        let returnedRecord = Helper.getHostBaseRecord(recordType: record)
        XCTAssertEqual(returnedRecord.value, 42)
    }
}
