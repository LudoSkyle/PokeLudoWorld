package fr.skyle.pokeludoworld.scripts.gameplay.levels

import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.MultilineText
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

	fun read() {
		val messages = text.split("|").map { it.trim() }.filter { it.isNotEmpty() }
		MessageBox.instance?.play(messages)
	}
}
