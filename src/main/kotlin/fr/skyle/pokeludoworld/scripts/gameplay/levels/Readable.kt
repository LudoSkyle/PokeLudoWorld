package fr.skyle.pokeludoworld.scripts.gameplay.levels

import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.MultilineText
import godot.annotation.Script
import godot.api.StaticBody2D
import java.time.LocalTime

/**
 * Meuble qu'on peut examiner : bibliothèque, poubelle, serveur, télé, horloge.
 *
 * Le meuble lui-même reste une tuile ; ceci est un corps invisible posé sur sa
 * case, que le joueur trouve par la requête physique devant lui. Contrairement
 * à un panneau, ce qu'il dit peut dépendre du moment : l'heure, une émission.
 */
@Script
class Readable : StaticBody2D() {

	/** `text` (défaut), `clock` ou `tv`. */
	@Category("Contenu")
	@Export
	var kind: String = "text"

	/** Pour `kind = text`. Une barre verticale `|` sépare deux boîtes. */
	@Category("Contenu")
	@MultilineText
	@Export
	var text: String = ""

	fun read() {
		MessageBox.instance?.play(messages())
	}

	private fun messages(): List<String> = when (kind) {
		"clock" -> {
			val now = LocalTime.now()
			listOf("L horloge indique %d h %02d.".format(now.hour, now.minute))
		}

		"tv" -> split(TV_PROGRAMS.random())
		else -> split(text)
	}

	private fun split(raw: String): List<String> =
		raw.split("|").map { it.trim() }.filter { it.isNotEmpty() }

	companion object {
		/**
		 * Dans l'esprit des jeux d'origine : la télé décrit en une phrase ce
		 * qui passe, et le héros repart. Aucun Pokémon pour l'instant.
		 */
		private val TV_PROGRAMS = listOf(
			"C est la meteo.|Grand soleil sur tout le village aujourd hui !",
			"C est la meteo.|Quelques nuages ce soir, mais pas une goutte de pluie.",
			"C est la meteo.|Un petit vent frais soufflera sur la cote demain matin.",
			"Il y a un film a la tele.|Quatre garcons marchent le long d une voie ferree.|Je ferais mieux d y aller aussi.",
			"Il y a un film a la tele.|Deux hommes dansent sur un piano geant.|Bon, il est temps de bouger !",
			"Une emission de cuisine.|Le chef rate sa crepe, le public applaudit quand meme.",
			"Un documentaire sur les grottes de la region.|Il parait qu on s y perd facilement.",
			"Un jeu televise.|Le candidat hesite... Ah, mauvaise reponse !",
			"C est le journal.|Rien a signaler au village, et c est tres bien comme ca.",
			"Une publicite pour des chaussures de course.|Avec elles on irait deux fois plus vite, parait-il.",
		)
	}
}
