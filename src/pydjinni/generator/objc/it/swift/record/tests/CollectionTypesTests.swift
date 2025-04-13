import XCTest
import RecordTestSwift

final class CollectionTypesTests: XCTestCase {
    var record = CollectionTypes(
        intList: [0, 1],
        stringList: ["foo", "bar"],
        intSet: Set([0, 1]),
        stringSet: Set(["foo", "bar"]),
        intIntMap: [0: 1],
        stringStringMap: ["foo": "bar"]
    )

    func testCollectionTypes() {
        let returnedRecord = Helper.getCollectionTypes(recordType: record)

        XCTAssertEqual(returnedRecord.intList.count, 2)
        XCTAssertEqual(returnedRecord.intList[0], 0)
        XCTAssertEqual(returnedRecord.intList[1], 1)

        XCTAssertEqual(returnedRecord.stringList.count, 2)
        XCTAssertEqual(returnedRecord.stringList[0], "foo")
        XCTAssertEqual(returnedRecord.stringList[1], "bar")

        XCTAssertEqual(returnedRecord.intSet.count, 2)
        XCTAssertTrue(returnedRecord.intSet.contains(0))
        XCTAssertTrue(returnedRecord.intSet.contains(1))

        XCTAssertEqual(returnedRecord.stringSet.count, 2)
        XCTAssertTrue(returnedRecord.stringSet.contains("foo"))
        XCTAssertTrue(returnedRecord.stringSet.contains("bar"))

        XCTAssertEqual(returnedRecord.intIntMap.count, 1)
        XCTAssertEqual(returnedRecord.intIntMap[0], 1)

        XCTAssertEqual(returnedRecord.stringStringMap.count, 1)
        XCTAssertEqual(returnedRecord.stringStringMap["foo"], "bar")
    }

    func testDescription() {
        XCTAssertNotNil(
            record.description.range(of:
                """
                <SFTCollectionTypes intList:(
                    0,
                    1
                ) stringList:(
                    foo,
                    bar
                ) intSet:{(
                """
            )
        )
        XCTAssertNotNil(
            record.description.range(of:
                """
                )} intIntMap:{
                    0 = 1;
                } stringStringMap:{
                    foo = bar;
                }>
                """
            )
        )
    }
}
