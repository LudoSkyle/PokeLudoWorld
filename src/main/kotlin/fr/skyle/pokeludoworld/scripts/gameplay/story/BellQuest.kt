package fr.skyle.pokeludoworld.scripts.gameplay.story

import fr.skyle.pokeludoworld.scripts.gameplay.items.Inventory

/**
 * Les étapes de la quête de la cloche, dans l'ordre : le drapeau de chacune,
 * et ce qu'elle met dans le sac ou en retire.
 *
 * Le jeu lui-même ne passe pas par ici — chaque étape est posée par un
 * dialogue de la carte (voir docs/quests.md). Ceci sert à la mise au point :
 * sauter à une étape sans rejouer ce qui précède, depuis l'entrée Debug du
 * menu de pause.
 */
object BellQuest {

	private data class Step(val flag: String, val gives: List<String> = emptyList(), val takes: List<String> = emptyList())

	private val STEPS = listOf(
		Step("bell_told"),
		Step("bell_register", gives = listOf("dusty_register")),
		Step("bell_tarnished", gives = listOf("tarnished_bell")),
		Step("bell_clean", gives = listOf("clear_bell"), takes = listOf("tarnished_bell")),
		Step("bell_ribbon", gives = listOf("vigil_ribbon")),
		Step("bell_hung", takes = listOf("clear_bell")),
	)

	val isFinished: Boolean
		get() = STEPS.all { StoryFlags.has(it.flag) }

	/** Franchit la première étape qui ne l'est pas encore. Renvoie false si la quête est finie. */
	fun advance(): Boolean {
		val step = STEPS.firstOrNull { !StoryFlags.has(it.flag) } ?: return false
		step.takes.forEach { if (Inventory.has(it)) Inventory.remove(it) }
		step.gives.forEach { if (!Inventory.has(it)) Inventory.add(it) }
		StoryFlags.set(step.flag)
		return true
	}

	/** Franchit toutes les étapes restantes. Renvoie false s'il n'en restait aucune. */
	fun finish(): Boolean {
		if (isFinished) return false
		while (advance()) Unit
		return true
	}
}
