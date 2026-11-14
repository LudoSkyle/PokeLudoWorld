package fr.skyle.pokeludoworld.scripts.gameplay.items

import fr.skyle.pokeludoworld.scripts.log.Logger

/**
 * Le contenu du sac : combien on a de chaque objet, dans l'ordre où on les a
 * reçus. Il fait partie de la sauvegarde (voir SaveGame).
 */
object Inventory {

	private val counts = LinkedHashMap<String, Int>()

	fun count(id: String): Int = counts[id] ?: 0

	fun has(id: String): Boolean = count(id) > 0

	fun add(id: String, amount: Int = 1) {
		if (Items.get(id) == null) {
			Logger.e("Objet inconnu : $id")
			return
		}
		if (amount > 0) counts[id] = count(id) + amount
	}

	/** Retire [amount] exemplaires. Renvoie false, sans rien retirer, s'il n'y en a pas assez. */
	fun remove(id: String, amount: Int = 1): Boolean {
		val left = count(id) - amount
		if (amount <= 0 || left < 0) return false
		if (left == 0) counts.remove(id) else counts[id] = left
		return true
	}

	/** Les objets d'une poche, avec leur quantité. */
	fun contents(pocket: Pocket): List<Pair<Item, Int>> =
		counts.mapNotNull { (id, amount) -> Items.get(id)?.takeIf { it.pocket == pocket }?.let { it to amount } }

	fun snapshot(): Map<String, Int> = LinkedHashMap(counts)

	fun restore(saved: Map<String, Int>) {
		counts.clear()
		saved.forEach { (id, amount) -> add(id, amount) }
	}

	fun clear() {
		counts.clear()
	}
}
