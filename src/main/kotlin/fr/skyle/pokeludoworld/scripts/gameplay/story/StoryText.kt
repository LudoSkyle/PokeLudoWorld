package fr.skyle.pokeludoworld.scripts.gameplay.story

import fr.skyle.pokeludoworld.scripts.log.Logger
import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import godot.core.PackedStringArray

/**
 * Ce que dit un personnage ou un meuble selon l'avancée de l'histoire.
 *
 * `states` est une liste d'entrées `drapeau > texte`, dans l'ordre de
 * l'histoire. Elle se lit **de bas en haut** : la dernière étape atteinte
 * gagne. Si aucun de ses drapeaux n'est posé, c'est le texte par défaut.
 *
 * `ask` est une question Oui / Non posée avant ce texte : `Question ?` devant
 * le texte par défaut, `drapeau > Question ?` devant celui de cet état-là.
 */
object StoryText {

	/** Le texte en vigueur : celui du dernier état dont le drapeau est posé, sinon [text]. */
	fun current(text: String, states: PackedStringArray): String = reached(states)?.second ?: text

	/**
	 * Dit le texte en vigueur dans la boîte de dialogue. Si [ask] porte sur
	 * lui, la question est posée d'abord et le texte ne vient qu'après un Oui.
	 * [speaker] est le nom de celui qui parle, s'il en a un, et [gender] son genre.
	 */
	fun say(text: String, states: PackedStringArray, ask: String, speaker: String = "", gender: String = "") {
		val lines = boxes(current(text, states))
		val question = question(ask, states)
		if (question == null) {
			MessageBox.instance?.play(lines, speaker, gender)
		} else {
			MessageBox.instance?.ask(question, lines, speaker, gender)
		}
	}

	/** La question à poser avant le texte en vigueur, s'il y en a une. */
	private fun question(ask: String, states: PackedStringArray): String? {
		if (ask.isBlank()) return null
		val cut = ask.indexOf('>')
		val flag = if (cut < 0) "" else ask.substring(0, cut).trim()
		val stage = reached(states)?.first ?: ""
		return if (flag == stage) ask.substring(cut + 1).trim() else null
	}

	/** Découpe un texte en boîtes : une barre verticale `|` en sépare deux. */
	fun boxes(raw: String): List<String> = raw.split("|").map { it.trim() }.filter { it.isNotEmpty() }

	/** L'état en vigueur : son drapeau et son texte. Null si c'est le texte par défaut. */
	private fun reached(states: PackedStringArray): Pair<String, String>? {
		for (index in states.size - 1 downTo 0) {
			val entry = states[index]
			val cut = entry.indexOf('>')
			if (cut < 0) {
				Logger.e("Etat sans drapeau (attendu : drapeau > texte) : $entry")
				continue
			}
			val flag = entry.substring(0, cut).trim()
			if (StoryFlags.has(flag)) return flag to entry.substring(cut + 1).trim()
		}
		return null
	}
}
