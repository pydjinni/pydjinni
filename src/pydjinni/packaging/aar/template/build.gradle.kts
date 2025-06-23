plugins {
    id("com.android.library") version "8.10.1"
    id("maven-publish")
    id("org.jetbrains.kotlin.android") version "2.1.21"
}

android {
    namespace = "{{ config.aar.publish.group_id }}.{{ config.aar.publish.artifact_id }}"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
    }
    packaging {
        jniLibs.keepDebugSymbols.add("**/*.so")
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
    publishing {
        singleVariant("release") {
            withJavadocJar()
            withSourcesJar()
        }
    }
}
afterEvaluate {
    publishing {
        publications {
            create<MavenPublication>("release") {
                groupId = "{{ config.aar.publish.group_id }}"
                artifactId = "{{ config.aar.publish.artifact_id }}"
                version = "{{ config.version }}"
                from(components["release"])
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
}


