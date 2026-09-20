import godot.annotation.processor.classgraph.AnnotationProcessingMode
import godot.gradle.GodotLanguage

plugins {
    id("com.utopia-rise.godot-jvm") version "1.0.0-rc1"
}

repositories {
    mavenCentral()
    google()
}

godot {
    // --------- Setup ---------
    languages.set(setOf(GodotLanguage.KOTLIN, GodotLanguage.JAVA, GodotLanguage.SCALA))

    registration.annotationProcessingMode.set(AnnotationProcessingMode.Inferred)

    // Only change this if the Gradle project is not the Godot project root containing project.godot.
    //godotProjectDirectory.set(file("."))

    // Keep the default short registered class names instead of using fully qualified names.
    //registration.nameMode.set(RegisteredNameMode.SIMPLE_NAME)

    // Enable coroutines integration with Godot signal/lifecycle callbacks.
    //isGodotCoroutinesEnabled.set(true)

    // --------- Toolchain ---------
    //toolchain.javaVersion.set(17)
    //toolchain.kotlinVersion.set("2.3.20")
    //toolchain.scalaVersion.set("3.6.3")

    // --------- Android ---------
    //android.d8ToolPath.set("${System.getenv("ANDROID_SDK_ROOT")}/build-tools/36.0.0/d8")
    //android.compileSdkDirectory.set("${System.getenv("ANDROID_SDK_ROOT")}/platforms/android-36")
    //android.minApiLevel.set(21)

    // --------- Graal / iOS ---------
    //graal.homeDirectory.set(System.getenv("GRAALVM_HOME"))

    // --------- Library Authors ---------
    // Set this to true when this Gradle project is a reusable Godot-JVM library instead of a runnable game project.
    //isLibrary.set(true)
}
