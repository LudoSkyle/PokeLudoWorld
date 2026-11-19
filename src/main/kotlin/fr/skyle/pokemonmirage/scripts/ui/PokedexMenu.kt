package fr.skyle.pokemonmirage.scripts.ui

import fr.skyle.pokemonmirage.scripts.core.AudioManager
import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.DexEntry
import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.NationalDex
import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.Pokedex
import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.RegionalDex
import godot.annotation.Register
import godot.annotation.Script
import godot.api.AtlasTexture
import godot.api.CanvasLayer
import godot.api.Control
import godot.api.Input
import godot.api.Label
import godot.api.ResourceLoader
import godot.api.Texture2D
import godot.api.TextureRect
import godot.api.TranslationServer
import godot.core.Rect2
import godot.core.Vector2

/**
 * Le Pokédex régional, celui qu'on ouvre en jeu depuis le menu de pause.
 *
 * **C'est le Pokédex de Pokémon Essentials v21.1, porté** : son habillage est
 * fait pour lui (`assets/ui/pokedex/CREDITS.md`), et tout ce qui est posé ici
 * l'est aux places de ses deux scripts — la liste (`PokemonPokedex_Scene`,
 * `Window_Pokedex`) et la fiche (`PokemonPokedexInfo_Scene`, page 1). Les
 * noms de ses méthodes sont gardés dans les commentaires.
 *
 * L'écran est dessiné **dans les pixels de l'habillage**, 512 × 384, puis
 * grossi deux fois et demie : il tient les 1280 × 960 de l'écran, en 4:3.
 * Les places de la scène sont donc celles d'Essentials, telles quelles.
 *
 * Ce qu'on sait d'une espèce dépend de ce qu'on en a fait ([Pokedex]) :
 * jamais vue, elle n'a que son numéro et des tirets ; **vue**, son nom, son
 * portrait et sa fiche ; **prise**, sa catégorie, ses types, sa taille, son
 * poids et sa description.
 */
@Script
class PokedexMenu : CanvasLayer() {

	companion object {
		var instance: PokedexMenu? = null
			private set

		/** Lignes visibles de la liste (Essentials : `page_item_max`). */
		const val ROWS = 10
	}

	private var screen: Control? = null

	// La liste.
	private var list: Control? = null
	private var listName: Label? = null
	private var listIcon: TextureRect? = null
	private var seenCount: Label? = null
	private var ownedCount: Label? = null
	private var marks: List<TextureRect> = emptyList()
	private var numbers: List<Label> = emptyList()
	private var names: List<Label> = emptyList()
	private var cursor: Control? = null
	private var sliderUp: Control? = null
	private var sliderDown: Control? = null
	private var sliderBox: Control? = null

	// La fiche.
	private var entry: Control? = null
	private var portrait: TextureRect? = null
	private var own: Control? = null
	private var heading: Label? = null
	private var genus: Label? = null
	private var types: List<TextureRect> = emptyList()
	private var height: Label? = null
	private var weight: Label? = null
	private var text: Label? = null

	private var ownIcon: Texture2D? = null
	private var seenIcon: Texture2D? = null
	private var typeSheet: Texture2D? = null

	/** Les espèces que montre la liste (Essentials : `@dexlist`), et celle que désigne le curseur. */
	private var shown: List<DexEntry> = emptyList()
	private var selected = 0
	private var top = 0

	val isOpen: Boolean
		get() = screen?.visible == true

	/** Vrai quand la fiche d'une espèce est ouverte, à la place de la liste. */
	val isReading: Boolean
		get() = entry?.visible == true

	/** Le numéro régional de l'espèce sous le curseur, 0 si la liste est vide : pour les tests. */
	@Register
	fun shownNumber(): Int = shown.getOrNull(selected)?.let { RegionalDex.number(it.id) } ?: 0

	/** Le nombre de lignes de la liste, visibles ou non : pour les tests. */
	@Register
	fun listedCount(): Int = shown.size

	/** Inscrit l'espèce [id] comme vue, puis comme prise si [caught] : pour les tests, qui n'ont pas de combat. */
	@Register
	fun register(id: String, caught: Boolean) {
		if (caught) Pokedex.catch(id) else Pokedex.see(id)
		if (isOpen) {
			pbRefreshDexList(selected)
			if (isReading) drawPageInfo()
		}
	}

	@Register
	override fun _ready() {
		instance = this
		screen = getNode("Control/Screen") as? Control
		list = getNode("Control/Screen/List") as? Control
		listName = getNode("Control/Screen/List/Name") as? Label
		listIcon = getNode("Control/Screen/List/Icon") as? TextureRect
		seenCount = getNode("Control/Screen/List/Seen") as? Label
		ownedCount = getNode("Control/Screen/List/Owned") as? Label
		marks = children("Control/Screen/List/Marks")
		numbers = children("Control/Screen/List/Numbers")
		names = children("Control/Screen/List/Names")
		cursor = getNode("Control/Screen/List/Cursor") as? Control
		sliderUp = getNode("Control/Screen/List/SliderUp") as? Control
		sliderDown = getNode("Control/Screen/List/SliderDown") as? Control
		sliderBox = getNode("Control/Screen/List/SliderBox") as? Control
		entry = getNode("Control/Screen/Entry") as? Control
		portrait = getNode("Control/Screen/Entry/Portrait") as? TextureRect
		own = getNode("Control/Screen/Entry/Own") as? Control
		heading = getNode("Control/Screen/Entry/Heading") as? Label
		genus = getNode("Control/Screen/Entry/Genus") as? Label
		types = listOfNotNull(getNode("Control/Screen/Entry/Type0") as? TextureRect, getNode("Control/Screen/Entry/Type1") as? TextureRect)
		height = getNode("Control/Screen/Entry/Height") as? Label
		weight = getNode("Control/Screen/Entry/Weight") as? Label
		text = getNode("Control/Screen/Entry/Text") as? Label
		ownIcon = ResourceLoader.load(UI_DIR + "icon_own.png") as? Texture2D
		seenIcon = ResourceLoader.load(UI_DIR + "icon_seen.png") as? Texture2D
		typeSheet = ResourceLoader.load(UI_DIR + "icon_types.png") as? Texture2D
		// Un pixel de police fait ici deux pixels de l'habillage.
		PixelShadow.attachAll(screen, FONT_PIXEL)
		screen?.visible = false
	}

	private inline fun <reified T> children(path: String): List<T> {
		val box = getNode(path)
		return (0 until (box?.getChildCount() ?: 0)).mapNotNull { box?.getChild(it) as? T }
	}

	fun open() {
		if (isOpen) return
		screen?.visible = true
		entry?.visible = false
		list?.visible = true
		pbRefreshDexList(selected)
	}

	fun close() {
		screen?.visible = false
	}

	/** À appeler à chaque frame tant que l'écran est ouvert : c'est le menu de pause qui le fait. */
	fun handle(interact: Boolean) {
		if (!isOpen) return
		val back = Input.isActionJustPressed(PauseMenu.ACTION)
		if (isReading) pbScene(back) else pbPokedex(interact, back)
	}

	// ------------------------------------------------------------------ la liste

	/** Essentials : `PokemonPokedex_Scene#pbPokedex`, la boucle de la liste. La recherche (ACTION) n'est pas portée. */
	private fun pbPokedex(interact: Boolean, back: Boolean) {
		if (back) {
			close()
			return
		}
		if (shown.isEmpty()) return
		if (interact) {
			// On ne lit que la fiche d'une espèce qu'on a vue.
			if (Pokedex.isSeen(shown[selected].id)) pbDexEntry()
			return
		}
		var step = 0
		if (MenuKeys.down()) step += 1
		if (MenuKeys.up()) step -= 1
		if (Input.isActionJustPressed("ui_right")) step += ROWS
		if (Input.isActionJustPressed("ui_left")) step -= ROWS
		if (step == 0) return
		// Une ligne à la fois, la liste boucle ; par pages, elle s'arrête aux deux bouts.
		selected = if (step == 1 || step == -1) (selected + step + shown.size) % shown.size else (selected + step).coerceIn(0, shown.size - 1)
		drawList()
		pbRefresh()
	}

	/**
	 * Essentials : `pbRefreshDexList`, en ordre numérique — le seul qu'on ait. La
	 * liste **s'arrête à la dernière espèce vue** : les inconnues de la fin ne
	 * se montrent pas, celles du milieu gardent leur ligne de tirets.
	 */
	private fun pbRefreshDexList(index: Int) {
		val all = RegionalDex.all
		val last = all.indexOfLast { Pokedex.isSeen(it.id) }
		shown = all.take(last + 1)
		selected = index.coerceIn(0, maxOf(0, shown.size - 1))
		drawList()
		pbRefresh()
	}

	/** Essentials : `Window_Pokedex#refresh` et `drawItem` — les lignes visibles, puis le curseur. */
	private fun drawList() {
		if (selected < top) top = selected
		if (selected >= top + ROWS) top = selected - ROWS + 1
		top = top.coerceIn(0, maxOf(0, shown.size - ROWS))
		for (row in 0 until ROWS) {
			val line = shown.getOrNull(top + row)
			val seen = line != null && Pokedex.isSeen(line.id)
			marks.getOrNull(row)?.texture = when {
				line == null || !seen -> null
				Pokedex.isCaught(line.id) -> ownIcon
				else -> seenIcon
			}
			PixelShadow.setText(numbers.getOrNull(row), line?.let { digits(RegionalDex.number(it.id)) } ?: "")
			PixelShadow.setText(names.getOrNull(row), if (line == null) "" else if (seen) nameOf(line) else HIDDEN_NAME)
		}
		cursor?.visible = shown.isNotEmpty()
		cursor?.setPosition(Vector2(LIST_X, LIST_Y + (selected - top) * ROW_HEIGHT))
	}

	/** Essentials : `pbRefresh` — le nom et le portrait de l'espèce choisie, les deux comptes, l'ascenseur. */
	private fun pbRefresh() {
		val line = shown.getOrNull(selected)?.takeIf { Pokedex.isSeen(it.id) }
		PixelShadow.setText(listName, line?.let { nameOf(it) } ?: "")
		listIcon?.texture = line?.let { portraitOf(it) }
		val ids = RegionalDex.ids
		PixelShadow.setText(seenCount, Pokedex.seenCount(ids).toString())
		PixelShadow.setText(ownedCount, Pokedex.caughtCount(ids).toString())

		val above = top > 0
		val below = top + ROWS < shown.size
		sliderUp?.visible = above
		sliderDown?.visible = below
		sliderBox?.visible = above || below
		if (above || below) {
			// La boîte de l'ascenseur : sa hauteur dit la part de la liste qu'on voit, sa place où l'on en est.
			var boxHeight = SLIDER_HEIGHT * ROWS / shown.size
			boxHeight += minOf((SLIDER_HEIGHT - boxHeight) / 2, SLIDER_HEIGHT / 6)
			boxHeight = maxOf(boxHeight, 40)
			val y = SLIDER_Y + (SLIDER_HEIGHT - boxHeight) * top / (shown.size - ROWS)
			sliderBox?.setPosition(Vector2(SLIDER_X, y.toDouble()))
			sliderBox?.setSize(Vector2(40.0, boxHeight.toDouble()))
		}
	}

	// ------------------------------------------------------------------ la fiche

	/** Essentials : `pbDexEntry` puis `PokemonPokedexInfo_Scene#pbStartScene` — la fiche s'ouvre, et l'espèce crie. */
	private fun pbDexEntry() {
		list?.visible = false
		entry?.visible = true
		drawPageInfo()
		cry()
	}

	/** Essentials : `pbScene`, la boucle de la fiche. Une seule page : Gauche et Droite n'ont rien où aller. */
	private fun pbScene(back: Boolean) {
		if (back) {
			// Retour à la liste, le curseur sur l'espèce qu'on lisait.
			entry?.visible = false
			list?.visible = true
			drawList()
			pbRefresh()
			return
		}
		val before = selected
		if (MenuKeys.up()) pbGoToPrevious()
		if (MenuKeys.down()) pbGoToNext()
		if (selected != before) {
			drawPageInfo()
			cry()
		}
	}

	/** Essentials : `pbGoToPrevious` — l'espèce vue d'avant, s'il y en a une. */
	private fun pbGoToPrevious() {
		val index = (selected - 1 downTo 0).firstOrNull { Pokedex.isSeen(shown[it].id) } ?: return
		selected = index
	}

	/** Essentials : `pbGoToNext` — l'espèce vue d'après, s'il y en a une. */
	private fun pbGoToNext() {
		val index = (selected + 1 until shown.size).firstOrNull { Pokedex.isSeen(shown[it].id) } ?: return
		selected = index
	}

	/** Essentials : `drawPageInfo`. La trace de pas et le nombre de combats ne sont pas portés. */
	private fun drawPageInfo() {
		val species = shown.getOrNull(selected) ?: return
		val owned = Pokedex.isCaught(species.id)
		portrait?.texture = portraitOf(species)
		own?.visible = owned
		PixelShadow.setText(heading, "${digits(RegionalDex.number(species.id))}  ${nameOf(species)}")
		PixelShadow.setText(genus, if (owned) (if (french()) species.genusFr else species.genusEn) else T(UNKNOWN_GENUS))
		PixelShadow.setText(height, if (owned) measure(species.height, "m") else UNKNOWN_HEIGHT.replace('.', comma()))
		PixelShadow.setText(weight, if (owned) measure(species.weight, "kg") else UNKNOWN_WEIGHT.replace('.', comma()))
		PixelShadow.setText(text, if (owned) (if (french()) species.textFr else species.textEn) else "")
		types.forEachIndexed { index, icon -> icon.texture = if (owned) typeIcon(species.types.getOrNull(index)) else null }
	}

	private fun cry() {
		// Essentials coupe le son en cours avant de faire crier l'espèce (`pbSEStop`) : son cri s'entend toujours.
		shown.getOrNull(selected)?.let { AudioManager.instance?.cry(it.id, force = true) }
	}

	/** L'étiquette d'un type : sa case dans la planche, 96 × 32, à la place que lui donne Essentials. */
	private fun typeIcon(type: String?): Texture2D? {
		val index = TYPE_ICONS.indexOf(type ?: return null).takeIf { it >= 0 } ?: return null
		val sheet = typeSheet ?: return null
		return AtlasTexture().apply {
			atlas = sheet
			region = Rect2(0.0, index * 32.0, 96.0, 32.0)
		}
	}

	private fun nameOf(species: DexEntry): String = if (french()) species.nameFr else species.nameEn

	private fun french(): Boolean = TranslationServer.getLocale().startsWith("fr")

	private fun comma(): Char = if (french()) ',' else '.'

	private fun digits(value: Int): String = value.toString().padStart(3, '0')

	private fun measure(value: Double, unit: String): String = "%.1f".format(java.util.Locale.ROOT, value).replace('.', comma()) + " $unit"

	private fun portraitOf(species: DexEntry): Texture2D? =
		if (species.hasFront) ResourceLoader.load(NationalDex.FRONT_DIR + species.id + ".png") as? Texture2D else null
}

private const val UI_DIR = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/ui/pokedex/"

/** Un pixel de police, en pixels de l'habillage : la police est dessinée deux fois plus grosse que lui. */
private const val FONT_PIXEL = 2.0

/** Le coin de la première ligne de la liste (la fenêtre d'Essentials est en (206, 30), son contenu 16 plus loin), et la hauteur d'une ligne. */
private const val LIST_X = 222.0
private const val LIST_Y = 46.0
private const val ROW_HEIGHT = 32.0

/** L'ascenseur : sa colonne, le haut de sa course et sa longueur (Essentials : `sliderheight`). */
private const val SLIDER_X = 468.0
private const val SLIDER_Y = 78
private const val SLIDER_HEIGHT = 268

private const val HIDDEN_NAME = "----------"
private const val UNKNOWN_HEIGHT = "????.? m"
private const val UNKNOWN_WEIGHT = "????.? kg"
private val UNKNOWN_GENUS = N("Pokémon ?????")

/** Les types dans l'ordre de la planche `icon_types.png`, celui d'Essentials (`IconPosition` de son `types.txt`) ; la case 9 est son « ??? ». */
private val TYPE_ICONS = listOf(
	"normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost", "steel", "qmarks",
	"fire", "water", "grass", "electric", "psychic", "ice", "dragon", "dark", "fairy",
)
