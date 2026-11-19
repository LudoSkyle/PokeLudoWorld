package fr.skyle.pokemonmirage.scripts.ui

import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.DexEntry
import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.NationalDex
import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.Pokedex
import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.RegionalDex
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasLayer
import godot.api.Control
import godot.api.Input
import godot.api.Label
import godot.api.ResourceLoader
import godot.api.Texture2D
import godot.api.TextureRect
import godot.api.TranslationServer
import godot.core.Vector2

/**
 * Le Pokédex régional, celui qu'on ouvre en jeu depuis le menu de pause.
 *
 * Deux vues sur le même écran. **La liste** : les espèces de la région dans
 * leur ordre, douze à la fois, avec à gauche le portrait et la carte de celle
 * que montre le curseur. **La fiche**, qu'on ouvre en validant une espèce
 * déjà vue : sa taille, son poids et sa description à la place de la liste.
 *
 * Ce qu'on sait d'une espèce dépend de ce qu'on en a fait ([Pokedex]) :
 * jamais vue, elle n'a que son numéro ; **vue**, son nom et son portrait ;
 * **prise**, sa catégorie, sa taille, son poids et sa description.
 *
 * L'écran fait 320 × 240 pixels de jeu, tout l'écran en 4:3. Son habillage est
 * provisoire : des cadres du jeu sur un fond uni, en attendant son dessin.
 */
@Script
class PokedexMenu : CanvasLayer() {

	companion object {
		var instance: PokedexMenu? = null
			private set

		/** Lignes visibles de la liste. */
		const val ROWS = 12
	}

	private var screen: Control? = null
	private var counts: Label? = null
	private var portrait: TextureRect? = null
	private var unknown: Label? = null
	private var number: Label? = null
	private var nameLabel: Label? = null
	private var genus: Label? = null
	private var status: Label? = null
	private var list: Control? = null
	private var cursor: Control? = null
	private var numbers: List<Label> = emptyList()
	private var names: List<Label> = emptyList()
	private var marks: List<Label> = emptyList()
	private var scrollUp: Control? = null
	private var scrollDown: Control? = null
	private var sheet: Control? = null
	private var height: Label? = null
	private var weight: Label? = null
	private var text: Label? = null

	private var selected = 0
	private var top = 0

	val isOpen: Boolean
		get() = screen?.visible == true

	/** Vrai quand la fiche d'une espèce est ouverte, à la place de la liste. */
	val isReading: Boolean
		get() = sheet?.visible == true

	/** Le numéro régional de l'espèce sous le curseur : pour les tests. */
	@Register
	fun shownNumber(): Int = selected + 1

	/** Inscrit l'espèce [id] comme vue, puis comme prise si [caught] : pour les tests, qui n'ont pas de combat. */
	@Register
	fun register(id: String, caught: Boolean) {
		if (caught) Pokedex.catch(id) else Pokedex.see(id)
		if (isOpen) refresh()
	}

	@Register
	override fun _ready() {
		instance = this
		screen = getNode("Control/Screen") as? Control
		counts = getNode("Control/Screen/Counts") as? Label
		portrait = getNode("Control/Screen/Portrait") as? TextureRect
		unknown = getNode("Control/Screen/Unknown") as? Label
		number = getNode("Control/Screen/Number") as? Label
		nameLabel = getNode("Control/Screen/Name") as? Label
		genus = getNode("Control/Screen/Genus") as? Label
		status = getNode("Control/Screen/Status") as? Label
		list = getNode("Control/Screen/List") as? Control
		cursor = getNode("Control/Screen/List/Cursor") as? Control
		numbers = rows("Control/Screen/List/Numbers")
		names = rows("Control/Screen/List/Names")
		marks = rows("Control/Screen/List/Marks")
		scrollUp = getNode("Control/Screen/List/ScrollUp") as? Control
		scrollDown = getNode("Control/Screen/List/ScrollDown") as? Control
		sheet = getNode("Control/Screen/Sheet") as? Control
		height = getNode("Control/Screen/Sheet/Height") as? Label
		weight = getNode("Control/Screen/Sheet/Weight") as? Label
		text = getNode("Control/Screen/Sheet/Text") as? Label
		PixelShadow.attachAll(screen)
		screen?.visible = false
	}

	private fun rows(path: String): List<Label> {
		val box = getNode(path)
		return (0 until (box?.getChildCount() ?: 0)).mapNotNull { box?.getChild(it) as? Label }
	}

	fun open() {
		if (isOpen) return
		screen?.visible = true
		showList()
		refresh()
	}

	fun close() {
		screen?.visible = false
	}

	/** À appeler à chaque frame tant que l'écran est ouvert : c'est le menu de pause qui le fait. */
	fun handle(interact: Boolean) {
		if (!isOpen) return
		val back = Input.isActionJustPressed(PauseMenu.ACTION)
		if (isReading) {
			// La fiche se referme sur la liste, d'une touche ou de l'autre.
			if (back || interact) showList()
			return
		}
		if (back) {
			close()
			return
		}
		val all = RegionalDex.all
		if (all.isEmpty()) return
		if (interact) {
			// On ne lit que la fiche d'une espèce qu'on a vue.
			if (Pokedex.isSeen(all[selected].id)) showSheet(all[selected])
			return
		}

		var step = 0
		if (MenuKeys.down()) step += 1
		if (MenuKeys.up()) step -= 1
		if (Input.isActionJustPressed("ui_right")) step += PAGE
		if (Input.isActionJustPressed("ui_left")) step -= PAGE
		if (step == 0) return
		// Une ligne à la fois, la liste boucle ; par pages, elle s'arrête aux deux bouts.
		selected = if (step == 1 || step == -1) (selected + step + all.size) % all.size else (selected + step).coerceIn(0, all.size - 1)
		refresh()
	}

	private fun showList() {
		sheet?.visible = false
		list?.visible = true
	}

	private fun showSheet(entry: DexEntry) {
		val caught = Pokedex.isCaught(entry.id)
		PixelShadow.setText(height, T(HEIGHT).format(if (caught) measure(entry.height, "m") else UNKNOWN))
		PixelShadow.setText(weight, T(WEIGHT).format(if (caught) measure(entry.weight, "kg") else UNKNOWN))
		PixelShadow.setText(text, if (caught) (if (french()) entry.textFr else entry.textEn) else T(NOT_CAUGHT))
		list?.visible = false
		sheet?.visible = true
	}

	private fun refresh() {
		val all = RegionalDex.all
		val ids = RegionalDex.ids
		PixelShadow.setText(counts, T(COUNTS).format(Pokedex.seenCount(ids), Pokedex.caughtCount(ids)))
		if (all.isEmpty()) return
		selected = selected.coerceIn(0, all.size - 1)
		if (selected < top) top = selected
		if (selected >= top + ROWS) top = selected - ROWS + 1

		for (row in 0 until ROWS) {
			val entry = all.getOrNull(top + row)
			PixelShadow.setText(numbers.getOrNull(row), entry?.let { digits(top + row + 1) } ?: "")
			PixelShadow.setText(names.getOrNull(row), entry?.let { nameOf(it) } ?: "")
			PixelShadow.setText(marks.getOrNull(row), if (entry != null && Pokedex.isCaught(entry.id)) CAUGHT_MARK else "")
		}
		cursor?.setPosition(Vector2(CURSOR_X, CURSOR_Y + (selected - top) * ROW_HEIGHT))
		scrollUp?.visible = top > 0
		scrollDown?.visible = top + ROWS < all.size

		val entry = all[selected]
		val seen = Pokedex.isSeen(entry.id)
		val caught = Pokedex.isCaught(entry.id)
		portrait?.texture = if (seen) portraitOf(entry) else null
		unknown?.visible = !seen
		PixelShadow.setText(number, T(NUMBER).format(digits(selected + 1)))
		PixelShadow.setText(nameLabel, nameOf(entry))
		PixelShadow.setText(genus, if (caught) (if (french()) entry.genusFr else entry.genusEn) else "")
		PixelShadow.setText(status, T(if (caught) STATUS_CAUGHT else if (seen) STATUS_SEEN else STATUS_UNKNOWN))
	}

	/** Le nom d'une espèce dans la langue du jeu — ou des tirets, tant qu'on ne l'a pas vue. */
	private fun nameOf(entry: DexEntry): String = when {
		!Pokedex.isSeen(entry.id) -> HIDDEN_NAME
		french() -> entry.nameFr
		else -> entry.nameEn
	}

	private fun french(): Boolean = TranslationServer.getLocale().startsWith("fr")

	private fun digits(value: Int): String = value.toString().padStart(3, '0')

	private fun measure(value: Double, unit: String): String =
		if (value <= 0.0) UNKNOWN else "${value.toString().replace('.', if (french()) ',' else '.')} $unit"

	private fun portraitOf(entry: DexEntry): Texture2D? =
		if (entry.hasFront) ResourceLoader.load(NationalDex.FRONT_DIR + entry.id + ".png") as? Texture2D else null
}

/** Gauche et Droite sautent dix espèces. */
private const val PAGE = 10

/** La place du curseur devant la première ligne, et la hauteur d'une ligne, en pixels d'écran. */
private const val CURSOR_X = 32.0
private const val CURSOR_Y = 44.0
private const val ROW_HEIGHT = 64.0

private const val HIDDEN_NAME = "-----"
private const val UNKNOWN = "???"

/** La marque d'une espèce prise, au bout de sa ligne. */
private const val CAUGHT_MARK = "●"

private val COUNTS = N("Vus %d  Pris %d")
private val NUMBER = N("No %s")
private val HEIGHT = N("Taille : %s")
private val WEIGHT = N("Poids : %s")
private val NOT_CAUGHT = N("Il faut l'avoir attrapé pour en savoir plus.")
private val STATUS_CAUGHT = N("Attrapé")
private val STATUS_SEEN = N("Vu")
private val STATUS_UNKNOWN = N("Inconnu")
