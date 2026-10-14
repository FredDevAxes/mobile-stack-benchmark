plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}
android {
    namespace = "dev.devaxes.catalogue"
    compileSdk = 36
    defaultConfig {
        applicationId = "dev.devaxes.catalogue"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "0.1"
        ndk { abiFilters += "arm64-v8a" }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true }
    flavorDimensions += "navigation"
    productFlavors {
        create("instant") { dimension = "navigation" }
        create("animated") { dimension = "navigation" }
    }
    buildTypes {
        getByName("release") {
            isMinifyEnabled = true
            isShrinkResources = true
            signingConfig = signingConfigs.getByName("debug")
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
    lint {
        lintConfig = file("../lint.xml")
        abortOnError = true
        warningsAsErrors = true
        disable += "GradleDependency"
    }
}
dependencies {
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.compose.ui:ui:1.9.0")
    implementation("androidx.compose.foundation:foundation:1.9.0")
    implementation("androidx.compose.animation:animation:1.9.0")
    testImplementation("junit:junit:4.13.2")
}
dependencyLocking { lockAllConfigurations() }
