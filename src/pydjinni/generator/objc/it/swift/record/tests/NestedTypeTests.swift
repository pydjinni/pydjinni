import XCTest
import RecordTestSwift

final class NestedTypeTests: XCTestCase {
    let record = ParentType(nested: NestedType(a: 42, b: [[1, 2], [3, 4]]))
    
    func testNestedType() {
        let returnedRecord = Helper.getNestedType(parent: record)
        XCTAssertEqual(returnedRecord.nested.a, 42)
    }

    func testDescription() {
        XCTAssertEqual(
            record.description,
            """
            <TSTParentType nested:<TSTNestedType a:42 b:(
                    (
                    1,
                    2
                ),
                    (
                    3,
                    4
                )
            )>>
            """
        )
    }
}
