package fr.skyle.pokeludoworld.scripts.gameplay.story

import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.core.PackedStringArray

/**
 * Ce que dit un personnage ou un meuble selon l'avancée de l'histoire.
 *
 * `states` est une liste d'entrées `drapeau > texte`, dans l'ordre de
 * l'histoire. Elle se lit **de bas en haut** : la dernière étape atteinte
 * gagne. Si aucun de ses drapeaux n'est posé, c'est le texte par défaut.
 */
object StoryText {

	/** Le texte en vigueur : celui du dernier état dont le drapeau est posé, sinon [text]. */
	fun current(text: String, states: PackedStringArray): String = reached(states) ?: text

	/** Découpe un texte en boîtes : une barre verticale `|` en sépare deux. */
	fun boxes(raw: String): List<String> = raw.split("|").map { it.trim() }.filter { it.isNotEmpty() }

	private fun reached(states: PackedStringArray): String? {
		for (index in states.size - 1 downTo 0) {
			val entry = states[index]
			val cut = entry.indexOf('>')
			if (cut < 0) {
				Logger.e("Etat sans drapeau (attendu : drapeau > texte) : $entry")
				continue
			}
			val flag = entry.substring(0, cut).trim()
			if (StoryFlags.has(flag)) return entry.substring(cut + 1).trim()
		}
		return null
	}
}
