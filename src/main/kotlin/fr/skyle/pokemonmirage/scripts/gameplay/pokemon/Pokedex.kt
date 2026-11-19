package fr.skyle.pokemonmirage.scripts.gameplay.pokemon

/**
 * Ce que le joueur a inscrit au Pokédex : les espèces qu'il a **vues**, et
 * celles qu'il a **prises**. Une espèce prise est vue. Il fait partie de la
 * sauvegarde (voir SaveGame).
 *
 * Il ne sait rien de la région : il retient des identifiants d'espèces. C'est
 * l'écran qui ne montre et ne compte que celles du [RegionalDex].
 */
object Pokedex {

	private val seen = LinkedHashSet<String>()
	private val caught = LinkedHashSet<String>()

	/** L'espèce [id] vient d'être rencontrée. Renvoie true si c'est la première fois. */
	fun see(id: String): Boolean = id.isNotBlank() && seen.add(id)

	/** L'espèce [id] vient d'être prise : elle est vue du même coup. Renvoie true si c'est la première fois. */
	fun catch(id: String): Boolean {
		if (id.isBlank()) return false
		seen.add(id)
		return caught.add(id)
	}

	fun isSeen(id: String): Boolean = id in seen

	fun isCaught(id: String): Boolean = id in caught

	/** Combien d'espèces de [among] sont vues. */
	fun seenCount(among: Collection<String>): Int = among.count { it in seen }

	/** Combien d'espèces de [among] sont prises. */
	fun caughtCount(among: Collection<String>): Int = among.count { it in caught }

	fun seenSnapshot(): List<String> = seen.toList()

	fun caughtSnapshot(): List<String> = caught.toList()

	fun restore(savedSeen: Collection<String>, savedCaught: Collection<String>) {
		clear()
		savedSeen.forEach { see(it) }
		savedCaught.forEach { catch(it) }
	}

	fun clear() {
		seen.clear()
		caught.clear()
	}
}
