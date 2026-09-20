package fr.skyle.pokeludoworld.scripts.core

import godot.global.GD
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

object Logger {

	private fun log(level: LogLevel, vararg message: Any?) {
		// Log info
		val dateTime = LocalDateTime.now()
		val timeStamp = "[${dateTime.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))}]"

		// Stacktrace info
		val callingMethod = Thread.currentThread().stackTrace[3]
		val className = callingMethod.className.substringAfterLast('.')
		val methodName = callingMethod.methodName
		val lineNumber = callingMethod.lineNumber

		val logMessage = "$timeStamp [$level] [$className] [$methodName:$lineNumber] "

		// Log color
		val color = when (level) {
			LogLevel.DEBUG ->
				LogColor.GRAY

			LogLevel.INFO ->
				LogColor.CYAN

			LogLevel.WARNING ->
				LogColor.ORANGE

			LogLevel.ERROR ->
				LogColor.RED
		}

		// Print using small subset of BBCode
		GD.printRich("[color=$color][b]$logMessage[/b][/color]", *message)
	}

	fun d(message: String) {
		log(level = LogLevel.DEBUG, message)
	}

	fun i(message: String) {
		log(level = LogLevel.INFO, message)
	}

	fun w(message: String) {
		log(level = LogLevel.WARNING, message)
	}

	fun e(message: String) {
		log(level = LogLevel.ERROR, message)
	}

	/** Colors defined in [GD.printRich] method */
	private enum class LogColor {
		BLACK,
		RED,
		GREEN,
		YELLOW,
		BLUE,
		MAGENTA,
		PINK,
		PURPLE,
		CYAN,
		WHITE,
		ORANGE,
		GRAY
	}
}
