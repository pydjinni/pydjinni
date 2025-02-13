import XCTest
import FlagsTestSwift

final class FlagsTests: XCTestCase {
    func testFlags() {
        XCTAssertEqual(Helper.getFlag(exampleFlag: ExampleFlags.A), ExampleFlags.A)
    }
    
    func testAllFlags() {
        XCTAssertEqual(Helper.getAllFlag(exampleFlag: ExampleFlags.all), ExampleFlags.all)
    }
    
    func testNoneFlags() {
        XCTAssertEqual(Helper.getNoneFlag(exampleFlag: []), [])
    }
}
