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
			listOf("L'horloge indique %d h %02d.".format(now.hour, now.minute))
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
			"C'est la météo.|Grand soleil sur tout le village aujourd hui !",
			"C'est la météo.|Quelques nuages ce soir, mais pas une goutte de pluie.",
			"C'est la météo.|Un petit vent frais soufflera sur la côte demain matin.",
			"Il y a un film à la télé.|Quatre garçons marchent le long d'une voie ferrée.|Je ferais mieux d'y aller aussi.",
			"Il y a un film à la télé.|Deux hommes dansent sur un piano géant.|Bon, il est temps de bouger !",
			"Une émission de cuisine.|Le chef rate sa crêpe, le public applaudit quand même.",
			"Un documentaire sur les grottes de la région.|Il paraît qu'on s'y perd facilement.",
			"Un jeu télévisé.|Le candidat hésite... Ah, mauvaise réponse !",
			"C'est le journal.|Rien à signaler au village, et c'est très bien comme ça.",
			"Une publicité pour des chaussures de course.|Avec elles on irait deux fois plus vite, paraît-il.",
		)
	}
}
