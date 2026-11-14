package fr.skyle.pokeludoworld.scripts.gameplay.levels

import fr.skyle.pokeludoworld.scripts.gameplay.story.StoryFlags
import fr.skyle.pokeludoworld.scripts.gameplay.story.StoryText
import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.MultilineText
import godot.annotation.Register
import godot.annotation.Script
import godot.api.StaticBody2D

/**
 * Panneau lisible. Le joueur l'atteint par la requête physique devant lui,
 * donc un panneau est un corps solide comme un autre : il bloque aussi.
 */
@Script
class Sign : StaticBody2D() {

	/**
	 * Texte affiché. Une barre verticale `|` sépare deux boîtes successives,
	 * ce qui évite d'exporter un tableau pour si peu.
	 */
	@Category("Contenu")
	@MultilineText
	@Export
	var text: String = ""

	/** Drapeau sans lequel le panneau n'est pas sur la carte. */
	@Category("Histoire")
	@Export
	var requiredFlag: String = ""

	/** Drapeau avec lequel le panneau n'est plus sur la carte. */
	@Category("Histoire")
	@Export
	var forbiddenFlag: String = ""

	@Register
	override fun _ready() {
		// Absent de cette étape de l'histoire : il quitte la carte avant d'y avoir servi.
		if (!StoryFlags.allows(requiredFlag, forbiddenFlag)) queueFree()
	}

	fun read() {
		MessageBox.instance?.play(StoryText.boxes(text))
	}
}
