package fr.skyle.pokemonmirage.scripts.core

import fr.skyle.pokemonmirage.scripts.ui.N
import godot.core.Vector2

/**
 * Le temps qu'il fait dehors : les huit temps de Rubis / Saphir / Émeraude,
 * décrits **comme Pokémon Essentials les décrit** (`GameData::Weather`, fichier
 * `012_Weather.rb` du kit). Chaque entrée reprend la sienne, valeur pour valeur.
 *
 * Cet objet ne fait que décrire : ce qui tombe, à quelle allure, quelle teinte.
 * C'est `WeatherLayer` qui anime, en suivant l'algorithme d'Essentials.
 *
 * **Une seule conversion** : leurs cases font 32 px et les nôtres 16. Toutes les
 * distances et toutes les vitesses sont donc les leurs divisées par deux — la
 * pluie tombe à (-600, 2400) chez eux, (-300, 1200) ici.
 */
object Weather {

	/** Le nombre de sprites que la météo peut animer (`RPG::Weather::MAX_SPRITES`). */
	const val MAX_SPRITES = 60

	/**
	 * Ce qu'une carte en demande. Essentials appelle la météo avec une
	 * puissance de 9, et `Game_Screen#weather` en tire `(9 + 1) * 60 / 10`.
	 */
	const val MAP_SPRITES = 60

	/**
	 * **Le seul écart voulu avec Essentials** : la pluie et l'averse tombent à
	 * trois dixièmes de leur allure. À la leur, une goutte traverse l'écran en
	 * un sixième de seconde ; la GBA, elle, laisse suivre chaque goutte des
	 * yeux. Mettre 1.0 rend l'allure d'origine.
	 */
	const val RAIN_PACE = 0.3

	/** La famille d'un temps : elle décide de quelques cas particuliers de l'animation. */
	enum class Category { NONE, RAIN, HAIL, SANDSTORM, SUN, FOG }

	/**
	 * Une teinte d'écran à la façon de RPG Maker : rouge, vert et bleu
	 * **ajoutés** à l'image (de -255 à 255), puis ce qu'on lui retire de
	 * couleur ([gray], de 0 à 255).
	 */
	class Tone(val red: Double, val green: Double, val blue: Double, val gray: Double)

	/**
	 * Un temps.
	 *
	 * - [particles] : les images de ce qui tombe, dans `assets/weather/`. Pour
	 *   la famille [Category.RAIN], **la dernière est l'éclaboussure**.
	 * - [tiles] : la nappe tuilée qui glisse par-dessus (blizzard, sable, brume).
	 * - [particleDrift], [tileDrift] : leurs vitesses, en pixels de jeu par
	 *   seconde. Tout va du haut-droite vers le bas-gauche.
	 * - [tone] : la teinte d'écran, selon le nombre de sprites demandé.
	 */
	enum class Sky(
		val label: String,
		val category: Category,
		val particles: List<String> = emptyList(),
		val tiles: List<String> = emptyList(),
		val particleDrift: Vector2 = Vector2.ZERO,
		val tileDrift: Vector2 = Vector2.ZERO,
		val tone: (Double) -> Tone = { Tone(0.0, 0.0, 0.0, 0.0) },
	) {
		CLEAR(N("Météo : normale"), Category.NONE),

		RAIN(
			N("Météo : pluie"), Category.RAIN,
			particles = listOf("rain_1", "rain_2", "rain_3", "rain_4"),
			particleDrift = Vector2(-300.0 * RAIN_PACE, 1200.0 * RAIN_PACE),
			tone = { Tone(-it / 2, -it / 2, -it / 2, 10.0) },
		),

		/** `:HeavyRain` : les images et l'allure de l'orage, sans ses éclairs. */
		DOWNPOUR(
			N("Météo : averse"), Category.RAIN,
			particles = listOf("storm_1", "storm_2", "storm_3", "storm_4"),
			particleDrift = Vector2(-1800.0 * RAIN_PACE, 1800.0 * RAIN_PACE),
			tone = { Tone(-it * 3 / 4, -it * 3 / 4, -it * 3 / 4, 10.0) },
		),

		SNOW(
			N("Météo : neige"), Category.HAIL,
			particles = listOf("hail_1", "hail_2", "hail_3"),
			particleDrift = Vector2(-120.0, 120.0),
			tone = { Tone(it / 2, it / 2, it / 2, 0.0) },
		),

		BLIZZARD(
			N("Météo : blizzard"), Category.HAIL,
			particles = listOf("blizzard_1", "blizzard_2", "blizzard_3", "blizzard_4"),
			tiles = listOf("blizzard_tile"),
			particleDrift = Vector2(-360.0, 120.0),
			tileDrift = Vector2(-600.0, 300.0),
			tone = { Tone(it * 3 / 4, it * 3 / 4, it * 3 / 4, 0.0) },
		),

		SANDSTORM(
			N("Météo : tempête de sable"), Category.SANDSTORM,
			particles = listOf("sandstorm_1", "sandstorm_2", "sandstorm_3", "sandstorm_4"),
			tiles = listOf("sandstorm_tile"),
			particleDrift = Vector2(-600.0, 320.0),
			tileDrift = Vector2(-400.0, 200.0),
			tone = { Tone(it / 2, 0.0, -it / 2, 0.0) },
		),

		/** `:Sun` : rien ne tombe ; la teinte bat, voir `WeatherLayer`. */
		ZENITH(
			N("Météo : zénith"), Category.SUN,
			tone = { Tone(64.0, 64.0, 32.0, 0.0) },
		),

		FOG(
			N("Météo : brouillard"), Category.FOG,
			tiles = listOf("fog_tile"),
			tileDrift = Vector2(-16.0, 0.0),
		),
	}

	/** Le temps qu'il fait. Il ne change pas tout seul : on le choisit. */
	var sky: Sky = Sky.CLEAR

	/** Passe au temps suivant, et revient au premier après le dernier. */
	fun cycle() {
		val all = Sky.entries
		sky = all[(sky.ordinal + 1) % all.size]
	}

	/** Le libellé du temps qu'il fait, pour l'outil de mise au point. */
	fun label(): String = sky.label
}
