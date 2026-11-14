plugins {
 id("com.android.application")
 id("org.jetbrains.kotlin.android")
 id("org.jetbrains.kotlin.plugin.compose")
}
android {
 namespace = "com.example.pixelfitfixtures"
 compileSdk = 35
 defaultConfig { applicationId = "com.example.pixelfitfixtures"; minSdk = 23; targetSdk = 28 }
 buildFeatures { compose = true }
}
dependencies {
 implementation(platform("androidx.compose:compose-bom:2024.12.01"))
 implementation("androidx.compose.material3:material3")
 implementation("androidx.activity:activity-compose:1.9.3")
}
kotlin { jvmToolchain(21) }
android { compileOptions { sourceCompatibility = JavaVersion.VERSION_21; targetCompatibility = JavaVersion.VERSION_21 } }
