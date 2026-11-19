package fr.skyle.pokemonmirage.scripts.core

/**
 * L'horloge du jeu : le temps qui s'est écoulé **pour le jeu**, image après
 * image, et non celui de la montre. Tout ce qui se règle sur du temps s'y
 * règle — l'eau et le vent des shaders, la répétition des touches dans les
 * menus, la fin d'un jingle ou d'un cri.
 *
 * Tant que le jeu tourne en temps réel, les deux temps sont les mêmes. Ils se
 * séparent quand on fait avancer le jeu à pas fixe, plus vite que la montre
 * (`--fixed-fps`, les tests) : un jeu réglé sur la montre s'y désaccorde, l'eau
 * ne bouge plus entre deux images, un cri « dure » des centaines de pas.
 *
 * C'est `Globals`, toujours là, qui la fait avancer ([advance]).
 */
object GameClock {

	/** Secondes de jeu écoulées depuis le lancement. */
	var seconds: Double = 0.0
		private set

	/** Les mêmes, en millisecondes : ce que donnait `Time.getTicksMsec()`. */
	fun msec(): Long = (seconds * 1000.0).toLong()

	fun advance(delta: Double) {
		seconds += delta
	}
}
