package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.gameplay.items.Inventory
import fr.skyle.pokeludoworld.scripts.gameplay.items.Items
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

	/** Vrai du moment où le menu s'ouvre à celui où il se ferme, écrans compris. */
	var isOpen: Boolean = false
		private set

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

		PixelShadow.attachAll(menu)
		menu?.visible = false
	}

	fun open() {
		if (isOpen || entries.isEmpty()) return
		// Chaque ouverture repart de la première entrée.
		selected = 0
		isOpen = true
		menu?.visible = true
		placeCursor()
	}

	fun close() {
		isOpen = false
		menu?.visible = false
	}

	/**
	 * Cache ou remontre le panneau sans fermer le menu : l'écran de sauvegarde
	 * prend sa place à l'écran, puis la lui rend si l'on répond Non.
	 */
	fun showPanel(shown: Boolean) {
		if (isOpen) menu?.visible = shown
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

		val bag = BagMenu.instance
		if (bag != null && bag.isOpen) {
			bag.handle(interact)
			return
		}

		val save = SaveMenu.instance
		if (save != null && save.isOpen) {
			save.handle(interact)
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
			"Save" -> SaveMenu.instance?.open()
			"Bag" -> BagMenu.instance?.open()
			"Debug" -> debug()
			else -> Logger.i("Menu : entree inconnue $selectedName")
		}
	}

	/**
	 * Outils de mise au point. Pour l'instant : remplir le sac d'un peu de
	 * tout, puisque rien dans le jeu ne donne encore d'objet.
	 */
	private fun debug() {
		Items.ALL.filter { !it.isKey }.forEachIndexed { index, item -> Inventory.add(item.id, index + 3) }
		close()
		MessageBox.instance?.play(
			listOf(
				N("Des objets de test ont été ajoutés au sac."),
				"@give:old_rod " + N("Vous recevez la Vieille canne !"),
				"@give:town_map " + N("Vous recevez la Carte du village !"),
			),
		)
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
