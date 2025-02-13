import XCTest
import AsyncTestSwift

final class AsyncTests: XCTestCase {
    var asynchronous: Asynchronous!
    override func setUp() async throws {
        asynchronous = await Asynchronous.getInstance()
    }
    
    func testAsyncMethodCall() async {
        let result = await asynchronous.add(a: 40, b: 2)
        XCTAssertEqual(result, 42)
    }
    
    func testNoParametersNoReturncall() async {
        await asynchronous.noParametersNoReturn()
    }
    
    func testAsyncCallback() async {
        class MulitiplyCallbackImpl : MultiplyCallback {
            func invoke(a: Int32, b: Int32) async -> Int32 {
                return a * b
            }
        }
        let result = await asynchronous.multiplyCallback(callback: MulitiplyCallbackImpl())
        XCTAssertEqual(result, 42)
    }
    
    func testNoParametersNoReturnAsyncCallback() async {
        class NoParametersNoReturnCallbackImpl : NoParametersNoReturnCallback {
            func invoke() async {
                return
            }
        }
        await asynchronous.noParametersNoReturnCallback(callback: NoParametersNoReturnCallbackImpl())
    }
    

}

