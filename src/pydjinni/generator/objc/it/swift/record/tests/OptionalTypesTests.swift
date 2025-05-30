import XCTest
import RecordTestSwift

final class OptionalTypesTests: XCTestCase {
    let record = OptionalTypes(intOptional: 42, stringOptional: "optional")
    
    func testOptionalTypes() {
        let returnedRecord = Helper.getOptionalTypes(recordType: record)

        XCTAssertEqual(returnedRecord.intOptional, 42)
        XCTAssertEqual(returnedRecord.stringOptional, "optional")
    }

    func testDescription() {
        XCTAssertEqual(
            record.description,
            "<SFTOptionalTypes intOptional:42 stringOptional:optional>"
        )
    }
}
