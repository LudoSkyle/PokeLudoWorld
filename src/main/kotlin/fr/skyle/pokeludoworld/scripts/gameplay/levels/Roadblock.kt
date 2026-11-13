package fr.skyle.pokeludoworld.scripts.gameplay.levels

import fr.skyle.pokeludoworld.scripts.core.SceneManager
import fr.skyle.pokeludoworld.scripts.gameplay.characters.Npc
import fr.skyle.pokeludoworld.scripts.gameplay.characters.Player
import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Area2D
import godot.core.Vector2

/**
 * Passage gardé. Posé sur la case laissée libre à côté d'un garde : si le
 * joueur s'y engage, le garde le repousse d'une case en prenant sa place, lui
 * dit ce qu'il dit quand on lui parle, puis retourne à son poste.
 *
 * Ce n'est pas une collision : le joueur entre vraiment sur la case, et c'est
 * ce qui déclenche la scène.
 *
 * C'est le joueur qui prévient, à l'instant où il termine son pas (voir
 * Player) : avec la touche tenue il enchaîne le pas suivant dans la même
 * image, et un script qui l'observerait de l'extérieur ne le verrait jamais
 * posé sur la case. D'où la zone, sur le même calque que les portes.
 */
@Script
class Roadblock : Area2D() {

	/** Nom du garde, sous `World/Entities`. Il doit être sur une case voisine. */
	@Category("Garde")
	@Export
	var guard: String = ""

	/** Direction dans laquelle le joueur est repoussé. */
	@Category("Garde")
	@Export
	var pushDirection: Vector2 = Vector2.RIGHT

	private enum class Phase { IDLE, MOVING_IN, TALKING, MOVING_OUT }

	private var phase = Phase.IDLE
	private var guardStep = Vector2.ZERO
	private var guardMoved = false

	private var player: Player? = null

	/** Appelé par le joueur quand il vient de se poser sur cette case. */
	fun intercept(arriving: Player) {
		if (phase != Phase.IDLE || SceneManager.instance?.isChanging == true) return
		val npc = node(ENTITIES + guard) as? Npc ?: return
		if (npc.isWalking) return

		player = arriving
		arriving.lock()
		// Le joueur recule sans se retourner ; le garde vient à sa place.
		guardMoved = arriving.stepBack(pushDirection)
		guardStep = (position - npc.position).normalized()
		if (guardMoved) guardMoved = npc.walk(guardStep)
		phase = Phase.MOVING_IN
	}

	@Register
	override fun _process(delta: Double) {
		if (phase == Phase.IDLE) return
		val current = player ?: return
		val npc = node(ENTITIES + guard) as? Npc ?: return
		val box = MessageBox.instance ?: return

		when (phase) {
			Phase.IDLE -> {}

			Phase.MOVING_IN -> {
				if (current.isWalking || npc.isWalking) return
				npc.face(pushDirection)
				npc.speak()
				phase = Phase.TALKING
			}

			Phase.TALKING -> {
				if (box.isOpen) return
				if (guardMoved) npc.walk(guardStep * -1.0)
				phase = Phase.MOVING_OUT
			}

			Phase.MOVING_OUT -> {
				if (npc.isWalking) return
				npc.faceHome()
				// La touche qui a mené ici est peut-être encore enfoncée.
				current.unlock(pushDirection * -1.0)
				player = null
				phase = Phase.IDLE
			}
		}
	}

	private fun node(path: String) = if (hasNode(path)) getNode(path) else null

	companion object {
		private const val ENTITIES = "../../World/Entities/"
	}
}
