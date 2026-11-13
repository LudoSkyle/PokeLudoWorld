package fr.skyle.pokeludoworld.scripts.gameplay.levels

import fr.skyle.pokeludoworld.scripts.core.SceneManager
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Area2D
import godot.core.Vector2

/**
 * Porte. Une `Area2D`, donc elle ne bloque pas : la requête de déplacement du
 * joueur n'interroge que les corps, pas les zones.
 *
 * Les portes se nomment entre elles : chaque porte vise une carte et le *nom*
 * d'une porte de cette carte. Le joueur arrive devant elle, décalé de
 * [entryDirection].
 */
@Script
class SceneTrigger : Area2D() {

	@Category("Destination")
	@Export
	var targetScene: String = ""

	/** Nom du noeud porte dans la carte visée, sous son noeud `Doors`. */
	@Export
	var targetDoor: String = ""

	@Category("Arrivee")
	@Export
	var entryDirection: Vector2 = Vector2.DOWN

	private var fired = false

	@Register
	override fun _process(delta: Double) {
		val manager = SceneManager.instance ?: return

		if (manager.isChanging) {
			// On vient peut-être d'arriver sur cette porte : ne pas repartir.
			fired = true
			return
		}

		val bodies = getOverlappingBodies()
		var touching = false

		// Comparaison par nom : un corps tire d'un VariantArray<Node2D> ne
		// revient pas comme l'instance Kotlin, donc `is Player` serait faux.
		for (i in 0 until bodies.size) {
			if (bodies.get(i).name.toString() == "Player") {
				touching = true
				break
			}
		}


		if (!touching) {
			fired = false
			return
		}

		if (fired || targetScene.isEmpty()) return

		fired = true
		manager.changeLevel(targetScene, targetDoor)
	}
}
