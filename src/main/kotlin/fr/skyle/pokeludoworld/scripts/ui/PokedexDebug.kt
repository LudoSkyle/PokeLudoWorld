package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.gameplay.pokemon.DexEntry
import fr.skyle.pokeludoworld.scripts.gameplay.pokemon.NationalDex
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
import godot.core.Rect2

/**
 * Vue de debug du Pokédex national, ouverte depuis les outils de Debug du menu
 * de pause : **toutes** les espèces, vues ou non, pour vérifier que chacune a
 * ses noms, sa taille, son poids, ses deux descriptions, son icône et son
 * sprite. Ce n'est pas le Pokédex du jeu — celui-là sera régional, et ne
 * montrera que ce qu'on a rencontré.
 *
 * À gauche la liste, à droite la fiche. Haut/Bas : une espèce ; Gauche/Droite :
 * dix d'un coup ; la touche du menu referme. Une espèce à qui il manque quelque
 * chose porte une étoile dans la liste, et la fiche dit quoi.
 */
@Script
class PokedexDebug : CanvasLayer() {

	companion object {
		var instance: PokedexDebug? = null
			private set

		/** Lignes de la liste visibles à la fois. */
		const val ROWS = 14
	}

	private var screen: Control? = null
	private var title: Label? = null
	private var list: Label? = null
	private var names: Label? = null
	private var facts: Label? = null
	private var french: Label? = null
	private var english: Label? = null
	private var lacks: Label? = null
	private var icon: TextureRect? = null
	private var walker: TextureRect? = null

	private var selected = 0
	private var top = 0

	val isOpen: Boolean
		get() = screen?.visible == true

	/** Le numéro national de l'espèce montrée : ce que les tests regardent. */
	@Register
	fun shownNumber(): Int = NationalDex.all.getOrNull(selected)?.number ?: 0

	@Register
	override fun _ready() {
		instance = this
		screen = getNode("Control/Screen") as? Control
		title = getNode("Control/Screen/Title") as? Label
		list = getNode("Control/Screen/List") as? Label
		names = getNode("Control/Screen/Names") as? Label
		facts = getNode("Control/Screen/Facts") as? Label
		french = getNode("Control/Screen/French") as? Label
		english = getNode("Control/Screen/English") as? Label
		lacks = getNode("Control/Screen/Lacks") as? Label
		icon = getNode("Control/Screen/Icon") as? TextureRect
		walker = getNode("Control/Screen/Walker") as? TextureRect
		screen?.visible = false
	}

	fun open() {
		if (isOpen) return
		screen?.visible = true
		refresh()
	}

	fun close() {
		screen?.visible = false
	}

	/** À appeler à chaque image tant que l'écran est ouvert. */
	fun handle(interact: Boolean) {
		if (!isOpen) return
		if (Input.isActionJustPressed(PauseMenu.ACTION)) {
			close()
			return
		}
		val count = NationalDex.all.size
		if (count == 0) return
		var step = 0
		if (MenuKeys.down()) step += 1
		if (MenuKeys.up()) step -= 1
		if (Input.isActionJustPressed("ui_right")) step += PAGE
		if (Input.isActionJustPressed("ui_left")) step -= PAGE
		if (step == 0) return
		// Haut et Bas bouclent ; un saut de page s'arrête aux deux bouts.
		selected = if (step == 1 || step == -1) (selected + step + count) % count else (selected + step).coerceIn(0, count - 1)
		refresh()
	}

	private fun refresh() {
		val all = NationalDex.all
		val entry = all.getOrNull(selected) ?: return
		if (selected < top) top = selected
		if (selected >= top + ROWS) top = selected - ROWS + 1

		val incomplete = all.count { it.missing.isNotEmpty() }
		title?.text = "Pokédex national — ${all.size} espèces, $incomplete incomplètes"
		list?.text = (top until minOf(top + ROWS, all.size)).joinToString("\n") { index ->
			val line = all[index]
			"${if (index == selected) ">" else " "} ${line.number.toString().padStart(4, '0')} ${line.nameFr}${if (line.missing.isEmpty()) "" else " *"}"
		}
		names?.text = "${entry.nameFr} / ${entry.nameEn}"
		facts?.text = "${entry.genusFr} / ${entry.genusEn}\nGén. ${entry.generation} — ${measure(entry.height, "m")} — ${measure(entry.weight, "kg")} — ${entry.id}"
		french?.text = entry.textFr.ifEmpty { "(pas de description en français)" }
		english?.text = entry.textEn.ifEmpty { "(no English description)" }
		lacks?.text = if (entry.missing.isEmpty()) "" else "Manque : " + entry.missing.joinToString(", ")
		icon?.texture = iconOf(entry)
		walker?.texture = walkerOf(entry)
	}

	private fun measure(value: Double, unit: String): String = if (value <= 0.0) "? $unit" else "${value.toString().replace('.', ',')} $unit"

	/** La première des deux images de l'icône, dans sa case de la planche. */
	private fun iconOf(entry: DexEntry): Texture2D? {
		if (!entry.hasIcon) return null
		val sheet = ResourceLoader.load(NationalDex.ICONS) as? Texture2D ?: return null
		val column = (entry.number - 1) % NationalDex.ICON_COLUMNS
		val row = (entry.number - 1) / NationalDex.ICON_COLUMNS
		return AtlasTexture().apply {
			atlas = sheet
			region = Rect2(column * 64.0, row * 32.0, 32.0, 32.0)
		}
	}

	/** L'image de face du sprite de marche : la troisième de la colonne de gauche de son bloc. */
	private fun walkerOf(entry: DexEntry): Texture2D? {
		if (!entry.hasOverworld) return null
		// Son propre fichier d'abord (les gros Pokémon, ceux du décor) : deux colonnes de quatre images carrées.
		val own = NationalDex.OVERWORLD_DIR + entry.id + ".png"
		if (ResourceLoader.exists(own)) {
			val sheet = ResourceLoader.load(own) as? Texture2D ?: return null
			val side = sheet.getWidth() / 2.0
			return AtlasTexture().apply {
				atlas = sheet
				region = Rect2(0.0, side * 2, side, side)
			}
		}
		// Sinon sa case de la planche commune.
		val sheet = ResourceLoader.load(NationalDex.OVERWORLD) as? Texture2D ?: return null
		val column = (entry.number - 1) % NationalDex.ICON_COLUMNS
		val row = (entry.number - 1) / NationalDex.ICON_COLUMNS
		return AtlasTexture().apply {
			atlas = sheet
			region = Rect2(column * 64.0, row * 128.0 + 64.0, 32.0, 32.0)
		}
	}
}

/** Espèces sautées par Gauche et Droite. */
private const val PAGE = 10
