plugins {
    id("com.android.library") version "8.1.1"
    id("maven-publish")
}

android {
    namespace = "{{ config.aar.publish.group_id }}.{{ config.aar.publish.artifact_id }}"
    compileSdk = 33

    defaultConfig {
        minSdk = 24
    }
    packaging {
        jniLibs.keepDebugSymbols.add("**/*.so")
    }
}
dependencies {
    api(files("libs/{{ config.target }}.jar"))
}
publishing {
    publications {
        create<MavenPublication>("release") {
            groupId = "{{ config.aar.publish.group_id }}"
            artifactId = "{{ config.aar.publish.artifact_id }}"
            version = "{{ config.version }}"
            artifact("$buildDir/outputs/aar/{{ config.target }}-release.aar")
        }
        repositories {
            maven {
                name = "remote"
                url = uri("{{ config.aar.publish.maven_registry }}")
                credentials(PasswordCredentials::class)
            }
        }
    }
}

