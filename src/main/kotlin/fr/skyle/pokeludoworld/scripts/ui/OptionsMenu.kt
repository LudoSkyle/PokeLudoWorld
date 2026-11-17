package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.core.AudioManager
import fr.skyle.pokeludoworld.scripts.core.Settings
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasLayer
import godot.api.Control
import godot.api.Input
import godot.api.Label
import godot.core.Color
import godot.core.Vector2

/**
 * Écran des options, ouvert depuis le menu de pause et posé par-dessus lui.
 *
 * Une ligne par réglage — vitesse du texte, langue, et trois volumes (musique,
 * cris des Pokémon, autres sons) : Haut/Bas changent de ligne, Gauche/Droite changent
 * la valeur, qui s'applique et s'enregistre aussitôt. La dernière ligne,
 * Retour, ramène au menu — comme la touche du menu.
 *
 * Comme le menu, il ne lit pas la touche d'interaction : il la reçoit par
 * [handle], appelé par le menu de pause.
 */
@Script
class OptionsMenu : CanvasLayer() {

	companion object {
		var instance: OptionsMenu? = null
			private set
	}

	private var screen: Control? = null
	private var cursor: Control? = null
	private var rows: List<Control> = emptyList()
	private var speeds: List<Label> = emptyList()
	private var languages: List<Label> = emptyList()
	private var volumes: Map<Settings.Volume, Label?> = emptyMap()

	private var row = 0

	val isOpen: Boolean
		get() = screen?.visible == true

	@Register
	override fun _ready() {
		instance = this
		screen = getNode("Control/Screen") as? Control
		cursor = getNode("Control/Screen/Cursor") as? Control

		val list = getNode("Control/Screen/Rows")
		rows = (0 until (list?.getChildCount() ?: 0)).mapNotNull { list?.getChild(it) as? Control }

		val choices = getNode("Control/Screen/Rows/TextSpeed/Choices")
		speeds = (0 until (choices?.getChildCount() ?: 0)).mapNotNull { choices?.getChild(it) as? Label }

		val tongues = getNode("Control/Screen/Rows/Language/Choices")
		languages = (0 until (tongues?.getChildCount() ?: 0)).mapNotNull { tongues?.getChild(it) as? Label }

		volumes = VOLUME_ROWS.entries.associate { (row, volume) -> volume to getNode("Control/Screen/Rows/$row/Value") as? Label }

		PixelShadow.attachAll(screen)
		screen?.visible = false
	}

	fun open() {
		if (isOpen) return
		row = 0
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

		if (Input.isActionJustPressed("ui_right") || Input.isActionJustPressed("ui_left")) {
			AudioManager.instance?.sfx("cursor")
		}
		if (MenuKeys.down()) row = (row + 1) % rows.size
		if (MenuKeys.up()) row = (row - 1 + rows.size) % rows.size

		when (rows.getOrNull(row)?.name?.toString()) {
			"TextSpeed" -> {
				// Pas de boucle ici : x0.5 et x4 sont les deux bouts.
				if (Input.isActionJustPressed("ui_right")) setTextSpeed(Settings.textSpeed + 1)
				if (Input.isActionJustPressed("ui_left")) setTextSpeed(Settings.textSpeed - 1)
			}
			"Language" -> {
				if (Input.isActionJustPressed("ui_right")) Settings.setLanguage(Settings.language + 1)
				if (Input.isActionJustPressed("ui_left")) Settings.setLanguage(Settings.language - 1)
			}
			in VOLUME_ROWS.keys -> {
				// Pas de boucle : muet et 100 % sont les deux bouts.
				val volume = VOLUME_ROWS.getValue(rows[row].name.toString())
				if (Input.isActionJustPressed("ui_right")) setVolume(volume, Settings.volume(volume) + 1)
				if (Input.isActionJustPressed("ui_left")) setVolume(volume, Settings.volume(volume) - 1)
			}
			"Back" -> if (interact) {
				close()
				return
			}
		}

		refresh()
	}

	private fun setTextSpeed(index: Int) {
		Settings.setTextSpeed(index)
		MessageBox.instance?.secondsPerLetter = Settings.secondsPerLetter
	}

	/** Règle un volume, l'applique à ce qui joue, et fait entendre le résultat : un cri pour les cris, un bruitage pour les sons. */
	private fun setVolume(volume: Settings.Volume, step: Int) {
		Settings.setVolume(volume, step)
		AudioManager.instance?.applyVolumes()
		when (volume) {
			Settings.Volume.CRIES -> AudioManager.instance?.cry(SAMPLE_CRY)
			Settings.Volume.SOUNDS -> AudioManager.instance?.sfx("confirm")
			Settings.Volume.MUSIC -> Unit          // elle joue déjà : on l'entend changer
		}
	}

	private fun refresh() {
		volumes.forEach { (volume, label) -> label?.text = "${Settings.volume(volume) * 100 / Settings.VOLUME_STEPS} %" }
		speeds.forEachIndexed { index, label ->
			label.addThemeColorOverride("font_color", if (index == Settings.textSpeed) CHOSEN else INK)
		}
		languages.forEachIndexed { index, label ->
			label.addThemeColorOverride("font_color", if (index == Settings.language) CHOSEN else INK)
		}

		val current = rows.getOrNull(row) ?: return
		val list = current.getParent() as? Control ?: return
		val arrow = cursor ?: return
		val y = list.getPosition().y + current.getPosition().y + (current.getSize().y - arrow.getSize().y) / 2.0
		arrow.setPosition(Vector2(arrow.getPosition().x, y))
	}
}

/** Les lignes de volume de la scène, et le réglage de chacune. */
private val VOLUME_ROWS = mapOf("MusicVolume" to Settings.Volume.MUSIC, "CriesVolume" to Settings.Volume.CRIES, "SoundsVolume" to Settings.Volume.SOUNDS)

/** Le cri qu'on fait entendre en réglant le volume des cris. */
private const val SAMPLE_CRY = "wingull"

private val INK = Color(0.345098, 0.345098, 0.313725, 1.0)
private val CHOSEN = Color(0.878431, 0.188235, 0.125490, 1.0)
