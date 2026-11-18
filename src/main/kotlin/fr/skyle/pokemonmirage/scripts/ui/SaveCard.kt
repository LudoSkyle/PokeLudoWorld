package fr.skyle.pokemonmirage.scripts.ui

import fr.skyle.pokemonmirage.scripts.core.SaveGame
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Control
import godot.api.Label

/**
 * Une carte de l'écran de sélection des parties (voir SaveSlots). Elle a deux
 * visages, dans la même scène :
 *
 * - `Save` : une partie sauvegardée — son numéro, le portrait du joueur, le
 *   lieu, les badges, le Pokédex, le temps de jeu, et les six cases de
 *   l'équipe ;
 * - `Action` : une simple barre avec un texte — « Nouvelle partie »,
 *   « Options ».
 *
 * Les badges, le Pokédex et l'équipe n'existent pas encore dans le jeu : la
 * carte affiche ce que dit la sauvegarde (zéro, zéro, personne), et les
 * montrera le jour où la sauvegarde les portera.
 */
@Script
class SaveCard : Control() {

	private var save: Control? = null
	private var action: Control? = null

	@Register
	override fun _ready() {
		save = getNode("Save") as? Control
		action = getNode("Action") as? Control
		PixelShadow.attachAll(this)
	}

	/** Montre la partie de l'emplacement [slot]. */
	fun showSave(slot: Int, state: SaveGame.State) {
		save?.visible = true
		action?.visible = false
		write("Save/Title", T(TITLE).format(slot))
		write("Save/Location", T(state.location))
		write("Save/Badges/Value", state.badges.toString())
		write("Save/Pokedex/Value", state.pokedex.toString())
		write("Save/Time/Value", SaveGame.clock(state.seconds))
	}

	/** Montre une barre qui ne porte qu'un texte, déjà traduit. */
	fun showAction(text: String) {
		save?.visible = false
		action?.visible = true
		write("Action/Text", text)
	}

	private fun write(path: String, text: String) {
		PixelShadow.setText(getNode(path) as? Label, text)
	}
}

private val TITLE = N("Partie %d")
