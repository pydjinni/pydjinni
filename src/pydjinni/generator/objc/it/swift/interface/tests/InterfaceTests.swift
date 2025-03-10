// Copyright 2025 jothepro
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import XCTest
import InterfaceTestSwift

class InterfaceTestsSwiftTests: XCTestCase {
    let calculator = Calculator.getInstance()
    
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
