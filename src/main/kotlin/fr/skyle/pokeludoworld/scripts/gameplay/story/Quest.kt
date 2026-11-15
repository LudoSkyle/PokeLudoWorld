package fr.skyle.pokeludoworld.scripts.gameplay.story

import fr.skyle.pokeludoworld.scripts.gameplay.items.Inventory
import fr.skyle.pokeludoworld.scripts.ui.N

/**
 * Une quête, vue comme une suite d'étapes : le drapeau de chacune, et ce
 * qu'elle met dans le sac ou en retire.
 *
 * Le jeu lui-même ne passe pas par ici — chaque étape est posée par un
 * dialogue de la carte (voir docs/quests.md). Ceci sert à la mise au point :
 * sauter à une étape sans rejouer ce qui précède, ou tout défaire pour
 * repartir de zéro, depuis l'entrée Debug du menu de pause.
 *
 * [label] est son nom, en français, traduit à l'affichage. [epilogue] liste les
 * drapeaux que la suite de l'histoire pose d'elle-même une fois la quête finie
 * (la fin de la Veillée, quand on quitte l'île) : aucune étape ne les pose,
 * mais repartir de zéro les retire aussi.
 */
class Quest(val id: String, val label: String, private val steps: List<Step>, private val epilogue: List<String> = emptyList()) {

	data class Step(val flag: String, val gives: List<String> = emptyList(), val takes: List<String> = emptyList())

	val isStarted: Boolean
		get() = steps.any { StoryFlags.has(it.flag) } || epilogue.any { StoryFlags.has(it) }

	val isFinished: Boolean
		get() = steps.all { StoryFlags.has(it.flag) }

	/** Franchit la première étape qui ne l'est pas encore. Renvoie false si la quête est finie. */
	fun advance(): Boolean {
		val step = steps.firstOrNull { !StoryFlags.has(it.flag) } ?: return false
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

	/**
	 * Défait les étapes franchies, de la dernière à la première : le drapeau
	 * de chacune est retiré, ce qu'elle avait donné quitte le sac et ce qu'elle
	 * avait pris y revient. Il ne reste rien de la quête. Renvoie false si elle
	 * n'avait pas commencé.
	 *
	 * La carte, elle, ne change qu'à son rechargement : c'est à l'appelant de
	 * le demander (`@reload`), pour que chacun retrouve sa place d'avant.
	 */
	fun reset(): Boolean {
		if (!isStarted) return false
		epilogue.forEach { StoryFlags.unset(it) }
		steps.asReversed().filter { StoryFlags.has(it.flag) }.forEach { step ->
			step.gives.forEach { if (Inventory.has(it)) Inventory.remove(it) }
			step.takes.forEach { if (!Inventory.has(it)) Inventory.add(it) }
			StoryFlags.unset(step.flag)
		}
		return true
	}
}

/** Les quêtes du jeu, dans l'ordre où on les rencontre. Une nouvelle quête s'ajoute ici. */
object Quests {

	val BELL = Quest(
		"bell",
		N("La cloche de la Veillée"),
		listOf(
			Quest.Step("bell_told"),
			Quest.Step("bell_register", gives = listOf("dusty_register")),
			Quest.Step("bell_tarnished", gives = listOf("tarnished_bell")),
			Quest.Step("bell_clean", gives = listOf("clear_bell"), takes = listOf("tarnished_bell")),
			Quest.Step("bell_ribbon", gives = listOf("vigil_ribbon")),
			Quest.Step("bell_hung", takes = listOf("clear_bell")),
		),
		epilogue = listOf("vigil_over"),
	)

	val ALL = listOf(BELL)
}
