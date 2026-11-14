package fr.skyle.pokeludoworld.scripts.gameplay.story

/**
 * Les drapeaux d'histoire : ce que le joueur a déjà fait. Un drapeau est un
 * nom (`bell_told`) ; il est posé ou il ne l'est pas, et une fois posé il le
 * reste. Les textes et la présence des personnages en dépendent.
 *
 * Ils font partie de la sauvegarde (voir SaveGame), comme le sac.
 */
object StoryFlags {

	private val raised = LinkedHashSet<String>()

	fun has(flag: String): Boolean = flag in raised

	fun set(flag: String) {
		if (flag.isNotBlank()) raised.add(flag.trim())
	}

	/**
	 * La condition de présence d'un nœud de carte : [required] doit être posé
	 * et [forbidden] ne pas l'être. Un nom vide ne demande rien.
	 */
	fun allows(required: String, forbidden: String): Boolean =
		(required.isBlank() || has(required.trim())) && (forbidden.isBlank() || !has(forbidden.trim()))

	fun snapshot(): Set<String> = LinkedHashSet(raised)

	fun restore(saved: Set<String>) {
		raised.clear()
		saved.forEach { set(it) }
	}

	fun clear() {
		raised.clear()
	}
}
