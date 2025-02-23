import XCTest
import NamespaceTestSwift

final class NamespaceTests: XCTestCase {
    func testGlobalInterface() {
        let result = GlobalInterface.getNamespacedRecord()
        XCTAssertEqual(result, SomethingNamespaced.NamespacedRecord(a: GlobalRecord(a: SomethingNamespaced.OtherNamespacedRecord(a: 5))))
    }
    
    func testNamespacedInterface() {
        let result = SomethingNamespaced.NamespacedInterface.getGlobalRecord()
        XCTAssertEqual(result, GlobalRecord(a: SomethingNamespaced.OtherNamespacedRecord(a: 5)))
    }
}
