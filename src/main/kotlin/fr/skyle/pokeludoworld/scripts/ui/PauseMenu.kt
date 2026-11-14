package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasLayer
import godot.api.Control
import godot.api.Input
import godot.api.NinePatchRect
import godot.api.ResourceLoader
import godot.api.Texture2D
import godot.core.Vector2

/**
 * Menu de pause : une colonne d'entrées en haut à droite, un curseur en début
 * de ligne.
 *
 * Comme la boîte de dialogue, il ne décide pas seul de s'ouvrir et ne lit
 * jamais la touche d'interaction : c'est le joueur qui l'ouvre et lui passe
 * la main à chaque image avec [handle]. Tant qu'il est ouvert, le monde est
 * figé (voir Player et Npc).
 *
 * Les entrées sont les enfants de `Control/Menu/Entries`, dans l'ordre. En
 * ajouter une, c'est ajouter un Label dans la scène et un cas dans [confirm].
 */
@Script
class PauseMenu : CanvasLayer() {

	companion object {
		var instance: PauseMenu? = null
			private set

		const val ACTION = "menu"
	}

	/** Cadre : nom d'un fichier de `assets/ui/frames`, sans l'extension. */
	@Category("Affichage")
	@Export
	var frame: String = "rse_01"

	private var menu: Control? = null
	private var cursor: Control? = null
	private var entries: List<Control> = emptyList()

	/** Entrée sous le curseur. Revient à la première à chaque ouverture. */
	var selected: Int = 0
		private set

	val isOpen: Boolean
		get() = menu?.visible == true

	/** Nom du nœud de l'entrée sous le curseur : `Bag`, `Options`, `Quit`. */
	val selectedName: String
		get() = entries.getOrNull(selected)?.name?.toString() ?: ""

	@Register
	override fun _ready() {
		instance = this
		menu = getNode("Control/Menu") as? Control
		cursor = getNode("Control/Menu/Cursor") as? Control

		val list = getNode("Control/Menu/Entries")
		entries = (0 until (list?.getChildCount() ?: 0)).mapNotNull { list?.getChild(it) as? Control }

		val texture = ResourceLoader.load("$FRAMES_DIR$frame.png") as? Texture2D
		if (texture == null) {
			Logger.e("Cadre de menu inconnu : $frame")
		} else {
			(getNode("Control/Menu/Frame") as? NinePatchRect)?.texture = texture
		}

		menu?.visible = false
	}

	fun open() {
		if (isOpen || entries.isEmpty()) return
		// Chaque ouverture repart de la première entrée.
		selected = 0
		menu?.visible = true
		placeCursor()
	}

	fun close() {
		menu?.visible = false
	}

	/**
	 * À appeler à chaque image tant que le menu est ouvert. [interact] est la
	 * pression d'interaction lue par le joueur.
	 */
	fun handle(interact: Boolean) {
		if (!isOpen) return

		// Un écran ouvert depuis le menu prend la main, et la rend en se fermant.
		val options = OptionsMenu.instance
		if (options != null && options.isOpen) {
			options.handle(interact)
			return
		}

		// La touche qui a ouvert le menu le referme.
		if (Input.isActionJustPressed(ACTION)) {
			close()
			return
		}

		if (Input.isActionJustPressed("ui_down")) move(1)
		if (Input.isActionJustPressed("ui_up")) move(-1)
		if (interact) confirm()
	}

	/** Le curseur boucle : Haut sur la première entrée mène à la dernière. */
	private fun move(step: Int) {
		selected = (selected + step + entries.size) % entries.size
		placeCursor()
	}

	private fun confirm() {
		when (selectedName) {
			"Quit" -> close()
			"Options" -> OptionsMenu.instance?.open()
			// Le Sac n'ouvre encore rien.
			else -> Logger.i("Menu : $selectedName (pas encore branche)")
		}
	}

	private fun placeCursor() {
		val entry = entries.getOrNull(selected) ?: return
		val list = entry.getParent() as? Control ?: return
		val arrow = cursor ?: return
		val y = list.getPosition().y + entry.getPosition().y + (entry.getSize().y - arrow.getSize().y) / 2.0
		arrow.setPosition(Vector2(arrow.getPosition().x, y))
	}
}

private const val FRAMES_DIR = "res://src/main/kotlin/fr/skyle/pokeludoworld/assets/ui/frames/"
