import XCTest
import RecordTestSwift

class BinaryTypesTests: XCTestCase {

    var record: BinaryTypes!

    override func setUp() {
        super.setUp()
        let byteArray: [UInt8] = [0x8F]
        let data = Data(byteArray)
        record = BinaryTypes(binaryT: data, binaryOptional: data)
    }

    func testBinaryTypes() {
        let returnedRecord = Helper.getBinaryTypes(recordType: record)

        XCTAssertEqual(returnedRecord.binaryT.count, 1)
        XCTAssertEqual(returnedRecord.binaryOptional?.count, 1)
    }
}
