package fr.skyle.pokeludoworld.scripts.gameplay.characters

import fr.skyle.pokeludoworld.scripts.log.Logger
import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.MultilineText
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CharacterBody2D
import godot.api.ResourceLoader
import godot.api.SpriteFrames
import godot.core.Vector2

/**
 * Personnage non joueur : il se tient sur une case, bloque le passage, et
 * parle quand on l'examine en se tournant vers celui qui lui parle.
 *
 * Il réutilise les composants du joueur — [CharacterMovement] pour les pas,
 * [CharacterAnimation] pour le sprite — sans composant d'entrée : ce sont
 * d'autres scripts qui le font marcher (voir Roadblock).
 */
@Script
class Npc : CharacterBody2D() {

	/** Nom d'une planche de `resources/spriteframes` : worker, gardener, bug_catcher. */
	@Category("Apparence")
	@Export
	var appearance: String = "worker"

	/** Direction regardée au repos. */
	@Category("Apparence")
	@Export
	var facing: Vector2 = Vector2.DOWN

	/** Ce qu'il dit. Une barre verticale `|` sépare deux boîtes. */
	@Category("Contenu")
	@MultilineText
	@Export
	var text: String = ""

	/** Direction regardée en ce moment. */
	var direction: Vector2 = Vector2.DOWN
		private set

	val isWalking: Boolean
		get() = movement?.isWalking ?: false

	private var movement: CharacterMovement? = null
	private var sprite: CharacterAnimation? = null

	@Register
	override fun _ready() {
		movement = getNode("Movement") as? CharacterMovement
		sprite = getNode("Sprite") as? CharacterAnimation
		movement?.attach(this)

		val frames = ResourceLoader.load("$FRAMES_DIR$appearance.tres") as? SpriteFrames
		if (frames == null) {
			Logger.e("Apparence de PNJ inconnue : $appearance")
		} else {
			sprite?.spriteFrames = frames
		}

		direction = facing
		sprite?.refresh(direction, false)
	}

	@Register
	override fun _process(delta: Double) {
		movement?.process(delta)
		sprite?.refresh(direction, isWalking)
	}

	fun face(newDirection: Vector2) {
		direction = newDirection
	}

	/** Reprend la direction de repos. */
	fun faceHome() {
		direction = facing
	}

	/** Fait un pas d'une case. Renvoie false si la case est occupée. */
	fun walk(step: Vector2): Boolean {
		direction = step
		return movement?.tryWalk(step) ?: false
	}

	/** Dit son texte, sans se tourner. */
	fun speak() {
		val messages = text.split("|").map { it.trim() }.filter { it.isNotEmpty() }
		MessageBox.instance?.play(messages)
	}

	/** On lui parle depuis une case voisine, en regardant dans [fromDirection]. */
	fun talk(fromDirection: Vector2) {
		if (isWalking) return
		direction = fromDirection * -1.0
		speak()
	}

	companion object {
		private const val FRAMES_DIR = "res://src/main/kotlin/fr/skyle/pokeludoworld/resources/spriteframes/"
	}
}
