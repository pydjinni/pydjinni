// swift-tools-version:5.3
import PackageDescription

let package = Package(
    name: "{{ config.target }}",
    products: [
        // Products define the executables and libraries a package produces, and make them visible to other packages.
        .library(
                name: "{{ config.target }}",
                targets: ["{{ config.target }}"])
    ],
    targets: [
        .binaryTarget(
            name: "{{ config.target }}",
            path: "bin/{{ config.target }}.xcframework"
        )
    ]
)
