import XCTest
import InterfaceTestSwift

class InterfaceTestsSwiftTests: XCTestCase {
    var calculator = Calculator.getInstance()
    
    func testCalculator() {
        let result = calculator.add(a: 40, b: 2)
        XCTAssertEqual(result, 42)
    }
    
    func testPlatformImplementation() {
        class PlatformImplementation : PlatformInterface {
            func getValue() -> Int8 {
                return 5
            }
        }
        let result = calculator.getPlatformValue(platform: PlatformImplementation())
        XCTAssertEqual(result, 5)
    }
    
    func testMethodNoParametersNoReturn() {
        calculator.noParametersNoReturn()
    }
    
    func testMethodThrowingException() {
        XCTAssertThrowsError(try calculator.throwingException()) { error in
            XCTAssertEqual(error.localizedDescription, "shit hit the fan")
        }
    }
    
    func testNoParametersNoReturnCallback() {
        class NoParametersNoReturnCallbackImpl : NoParametersNoReturnCallback {
            var invoked = false
            func invoke() {
                invoked = true
            }
        }
        let callback = NoParametersNoReturnCallbackImpl()
        calculator.noParametersNoReturnCallback(callback: callback)
        XCTAssertTrue(callback.invoked)
    }
}
