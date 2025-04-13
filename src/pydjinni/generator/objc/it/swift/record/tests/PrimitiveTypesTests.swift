import XCTest
import RecordTestSwift

final class PrimitiveTypesTests: XCTestCase {
    var record: PrimitiveTypes = PrimitiveTypes(booleanT: true, byteT: 8, shortT: 16, intT: 32, longT: 64, floatT: 32.32, doubleT: 64.64, stringT: "test string", dateT: Date(timeIntervalSince1970: 1688213309))

    func testPrimitiveTypes() {
        let returnedRecord = Helper.getPrimitiveTypes(recordType: record)

        XCTAssertEqual(returnedRecord.booleanT, true)
        XCTAssertEqual(returnedRecord.byteT, 8)
        XCTAssertEqual(returnedRecord.shortT, 16)
        XCTAssertEqual(returnedRecord.intT, 32)
        XCTAssertEqual(returnedRecord.longT, 64)
        XCTAssertGreaterThan(returnedRecord.floatT, 32)
        XCTAssertLessThan(returnedRecord.floatT, 33)
        XCTAssertGreaterThan(returnedRecord.doubleT, 64)
        XCTAssertLessThan(returnedRecord.doubleT, 65)
        XCTAssertEqual(returnedRecord.stringT, "test string")
        XCTAssertEqual(returnedRecord.dateT, Date(timeIntervalSince1970: 1688213309))
    }
    
    func testPrimitiveTypesEqual() {
        let returnedRecord = Helper.getPrimitiveTypes(recordType: record)
        XCTAssertEqual(returnedRecord, record)
    }

    func testDescription() {
        XCTAssertEqual(
            record.description,
            "<SFTPrimitiveTypes booleanT:YES byteT:8 shortT:16 intT:32 longT:64 floatT:32.32 doubleT:64.64 stringT:test string dateT:2023-07-01 12:08:29 +0000>"
        )
    }
}
