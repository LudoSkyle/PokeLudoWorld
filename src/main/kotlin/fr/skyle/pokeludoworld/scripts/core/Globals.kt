package fr.skyle.pokeludoworld.scripts.core

import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Node

@Script
class Globals : Node() {

	companion object {
		lateinit var instance: Globals
			private set
	}

	@Category("Gameplay")
	@Export
	var gridSize: Int = 16

	@Register
	override fun _ready() {
		instance = this

		Logger.i("Loading Globals ...")
	}
}
