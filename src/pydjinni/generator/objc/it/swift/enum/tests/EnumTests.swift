import XCTest
import EnumTestSwift

final class EnumTests: XCTestCase {
    func testEnum() {
        let result = Helper.getEnum(exampleEnum: ExampleEnum.A)
        XCTAssertEqual(result, ExampleEnum.A)
    }
}
