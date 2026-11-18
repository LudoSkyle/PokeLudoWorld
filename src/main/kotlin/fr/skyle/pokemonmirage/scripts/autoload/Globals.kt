package fr.skyle.pokemonmirage.scripts.autoload

import fr.skyle.pokemonmirage.scripts.core.DayNight
import fr.skyle.pokemonmirage.scripts.core.Weather
import fr.skyle.pokemonmirage.scripts.gameplay.items.ItemIcons
import fr.skyle.pokemonmirage.scripts.gameplay.items.Items
import fr.skyle.pokemonmirage.scripts.gameplay.story.StoryFlags
import fr.skyle.pokemonmirage.scripts.gameplay.wild.WildEncounters
import fr.skyle.pokemonmirage.scripts.gameplay.wild.WildTable
import fr.skyle.pokemonmirage.scripts.log.Logger
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Node
import kotlin.random.Random

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

	/**
	 * Les drapeaux d'histoire, vus de Godot : `Globals.has_flag("bell_told")`.
	 * Le code Kotlin s'adresse directement à [StoryFlags] ; ces deux fonctions
	 * servent aux scripts qui n'y ont pas accès, les tests en premier.
	 */
	@Register
	fun hasFlag(flag: String): Boolean = StoryFlags.has(flag)

	@Register
	fun setFlag(flag: String) {
		StoryFlags.set(flag)
	}

	/**
	 * L'heure du jeu, vue de Godot. `set_hour(23.0)` impose une heure, de 0 à
	 * 24 ; une valeur négative rend la main à l'horloge réelle.
	 */
	@Register
	fun hour(): Double = DayNight.hour()

	@Register
	fun setHour(hour: Double) {
		DayNight.forcedHour = hour.takeIf { it >= 0.0 }
	}

	/**
	 * Les objets du catalogue sans icône utilisable sous `assets/items/icons/` —
	 * le fichier manque, ou ne fait pas 32 × 32 —, séparés par des virgules ; vide si
	 * chacun a la sienne.
	 */
	@Register
	fun itemsWithoutIcon(): String = Items.ALL.filter {
		val icon = if (ItemIcons.has(it.icon)) ItemIcons.of(it.icon) else null
		icon == null || icon.getWidth() != 32 || icon.getHeight() != 32
	}.joinToString(",") { it.id }

	/**
	 * Le temps qu'il fait, vu de Godot : son rang dans [Weather.Sky] — 0 normal,
	 * 1 pluie, 2 averse, 3 neige, 4 blizzard, 5 tempête de sable, 6 zénith,
	 * 7 brouillard. `set_weather(2)` fait tomber l'averse.
	 */
	@Register
	fun weather(): Int = Weather.sky.ordinal

	@Register
	fun setWeather(sky: Int) {
		val all = Weather.Sky.entries
		Weather.sky = all[((sky % all.size) + all.size) % all.size]
	}

	/** Le nom du temps qu'il fait, tel que l'outil de mise au point l'affiche. */
	@Register
	fun weatherLabel(): String = Weather.label()

	/**
	 * Les rencontres sauvages, vues de Godot. [forceEncounters] impose le sort :
	 * 1, chaque pas dans l'herbe donne une rencontre ; 0, aucun ; négatif, le
	 * hasard reprend la main.
	 */
	@Register
	fun encounters(): Int = WildEncounters.count

	@Register
	fun forceEncounters(mode: Int) {
		WildEncounters.forced = if (mode < 0) null else mode > 0
	}

	/** Le dernier Pokémon sauvage rencontré, écrit `espèce:niveau` ; vide s'il n'y en a pas eu. */
	@Register
	fun lastEncounter(): String = WildEncounters.last?.let { "${it.species.id}:${it.level}" } ?: ""

	/** Donne une graine au hasard des rencontres : les mêmes tirages à chaque fois. */
	@Register
	fun seedEncounters(seed: Int) {
		WildEncounters.random = Random(seed)
	}

	/**
	 * Tire [count] Pokémon dans la table [table], écrite comme sur une carte,
	 * avec la graine [seed]. Renvoie les tirages `espèce:niveau` séparés par
	 * des virgules : de quoi vérifier une table sans marcher dans l'herbe.
	 */
	@Register
	fun wildDraws(table: String, count: Int, seed: Int): String {
		val parsed = WildTable.parse(table)
		val random = Random(seed)
		return (0 until count).mapNotNull { parsed.pick(random) }.joinToString(",") { "${it.species.id}:${it.level}" }
	}

	/** Les entrées mal écrites de la table [table], une par ligne ; vide si tout est bon. */
	@Register
	fun wildErrors(table: String): String = WildTable.parse(table).errors.joinToString("\n")
}
