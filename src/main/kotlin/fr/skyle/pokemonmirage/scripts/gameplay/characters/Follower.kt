package fr.skyle.pokemonmirage.scripts.gameplay.characters

import fr.skyle.pokemonmirage.scripts.autoload.Globals
import fr.skyle.pokemonmirage.scripts.log.Logger
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Node2D
import godot.core.Vector2
import kotlin.math.abs

/**
 * Le Pokémon qui suit le joueur : il marche **une case derrière lui**, sur la
 * case que le joueur vient de quitter, à son allure.
 *
 * Son image est celle de son espèce ([PokemonFrames]) — le fichier que lit
 * aussi un Pokémon posé sur la carte, chaque image à sa hauteur d'origine. Il s'anime sans cesse, même arrêté.
 *
 * Il n'a pas de corps : il n'arrête personne, et le joueur qui rebrousse
 * chemin passe à travers lui. À l'arrivée sur une carte il est sur la case du
 * joueur, caché ; il apparaît au premier pas.
 */
@Script
class Follower : Node2D() {

	/** Nom du fichier de `assets/pokemon/overworld/`, sans extension. */
	@Export
	var species: String = "wingull"

	private var sprite: CharacterAnimation? = null
	private var leader: Node2D? = null
	private var lead: CharacterMovement? = null
	private var seenSteps = -1
	private var target = Vector2.ZERO
	private var speed = 0.0
	private var direction = Vector2.DOWN

	/** Vrai tant qu'il rejoint sa case. */
	var isWalking: Boolean = false
		private set

	@Register
	override fun _ready() {
		sprite = getNode("Sprite") as? CharacterAnimation
		if (sprite?.let { PokemonFrames.dress(it, species, grid()) } != true) Logger.e("Pokemon suiveur sans image : $species")
		sprite?.refresh(direction, false)
	}

	/**
	 * Se range derrière [player], qui vient d'arriver quelque part : sur sa
	 * case, caché, jusqu'à son premier pas.
	 */
	fun follow(player: Node2D) {
		leader = player
		lead = (if (player.hasNode("Movement")) player.getNode("Movement") else null) as? CharacterMovement
		seenSteps = lead?.steps ?: -1
		position = player.position
		target = position
		isWalking = false
		visible = false
	}

	@Register
	override fun _process(delta: Double) {
		val player = leader ?: return
		val movement = lead ?: return

		// Le joueur engage un pas : la case qu'il quitte devient la nôtre.
		if (movement.steps != seenSteps) {
			seenSteps = movement.steps
			target = movement.origin
			// Même durée que le pas du joueur, quelle que soit la distance (après un saut, il y a deux cases à rattraper).
			val cells = (position.distanceTo(target) / grid()).coerceAtLeast(1.0)
			speed = movement.paceNow * grid() * cells
			isWalking = position.distanceTo(target) > 0.01
			visible = true
		}

		// Le joueur a été posé ailleurs sans marcher (une scène, une reprise) : on se range de nouveau sur sa case.
		if (!isWalking && !movement.isWalking && position.distanceTo(player.position) > grid() * 1.5) {
			follow(player)
			return
		}

		if (isWalking) {
			direction = cardinal(target - position)
			position = position.moveToward(target, delta * speed)
			if (position.distanceTo(target) < 0.01) {
				position = target
				isWalking = false
			}
		}
		// Arrivé, il regarde le joueur.
		if (!isWalking && player.position.distanceTo(position) > 0.01) direction = cardinal(player.position - position)

		// Il s'anime sans cesse, même arrêté, et toujours à la même cadence, qu'on marche ou qu'on coure — comme dans
		// les jeux d'origine et dans PSDK (`step_anime`). Son petit saut d'un pixel est dans son image.
		sprite?.refresh(direction, true)
	}

	private fun cardinal(gap: Vector2): Vector2 = when {
		abs(gap.x) >= abs(gap.y) -> if (gap.x >= 0.0) Vector2.RIGHT else Vector2.LEFT
		else -> if (gap.y >= 0.0) Vector2.DOWN else Vector2.UP
	}

	private fun grid(): Double = Globals.instance.gridSize.toDouble()
}
